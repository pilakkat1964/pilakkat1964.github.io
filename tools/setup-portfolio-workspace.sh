#!/bin/bash
#
# Setup Portfolio Workspace with GSD Integration
#
# Creates a new GSD workspace with selected portfolio projects.
# Supports: core, z-tools, others, all
#
# Usage:
#   ./setup-portfolio-workspace.sh --portfolios core --path ~/workspace/my-ws
#   ./setup-portfolio-workspace.sh --portfolios z-tools --path ~/workspace/z-ws
#   ./setup-portfolio-workspace.sh --portfolios all --path ~/workspace/all-ws
#

set -e

# ============================================================================
# Configuration
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PORTFOLIO_CONFIG="$SCRIPT_DIR/portfolio-config.yaml"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# ============================================================================
# Functions
# ============================================================================

log() {
    echo -e "${GREEN}[portfolio-workspace]${NC} $*"
}

warn() {
    echo -e "${YELLOW}[portfolio-workspace]${NC} $*" >&2
}

error() {
    echo -e "${RED}[portfolio-workspace]${NC} $*" >&2
    exit 1
}

usage() {
    cat << 'EOF'
Usage: setup-portfolio-workspace.sh [OPTIONS]

Setup a new GSD workspace for portfolio development.

OPTIONS:
  --portfolios PORTFOLIOS   Portfolio selection: core, z-tools, others, all
  --path PATH               Workspace root path (required)
  --strategy STRATEGY       Git strategy: worktree (default) or clone
  --help                    Show this help message

EXAMPLES:
  setup-portfolio-workspace.sh --portfolios core --path ~/workspace/main-ws
  setup-portfolio-workspace.sh --portfolios z-tools --path ~/workspace/z-tools-ws
  setup-portfolio-workspace.sh --portfolios all --path ~/workspace/all-ws
EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --portfolios)
            PORTFOLIOS="$2"
            shift 2
            ;;
        --path)
            WORKSPACE_PATH="$2"
            shift 2
            ;;
        --strategy)
            STRATEGY="$2"
            shift 2
            ;;
        --help)
            usage
            exit 0
            ;;
        *)
            error "Unknown option: $1"
            ;;
    esac
done

# Validate required arguments
if [[ -z "$PORTFOLIOS" ]] || [[ -z "$WORKSPACE_PATH" ]]; then
    error "Missing required arguments. Use --help for usage information."
fi

# Set defaults
STRATEGY="${STRATEGY:-worktree}"

# Validate portfolio selection
case "$PORTFOLIOS" in
    core|z-tools|others|all)
        log "Portfolio selection: $PORTFOLIOS"
        ;;
    *)
        error "Invalid portfolio selection: $PORTFOLIOS (valid: core, z-tools, others, all)"
        ;;
esac

# ============================================================================
# Validation
# ============================================================================

if [[ ! -f "$PORTFOLIO_CONFIG" ]]; then
    error "Portfolio configuration not found: $PORTFOLIO_CONFIG"
fi

if [[ ! -f "$(command -v python3)" ]]; then
    error "Python 3 is required but not found"
fi

# ============================================================================
# Extract Projects from Configuration
# ============================================================================

log "Loading portfolio configuration..."

# Use Python to extract project names and repos
PROJECTS=$(python3 << PYTHON_EOF
import yaml
from pathlib import Path

with open("$PORTFOLIO_CONFIG", 'r') as f:
    config = yaml.safe_load(f)

portfolios_to_include = []

# Map portfolio selection to actual portfolios
if "$PORTFOLIOS" == "all":
    portfolio_list = list(config['portfolios'].keys())
    # Remove 'all' portfolio itself
    portfolio_list = [p for p in portfolio_list if p != 'all']
else:
    portfolio_list = ["$PORTFOLIOS"]

# Extract projects from selected portfolios
projects = []
for portfolio_name in portfolio_list:
    if portfolio_name in config['portfolios']:
        portfolio = config['portfolios'][portfolio_name]
        for proj in portfolio.get('projects', []):
            if isinstance(proj, dict):
                name = proj.get('name', proj.get('repo', ''))
                repo = proj.get('repo', '')
            else:
                name = proj
                repo = proj
            
            projects.append((name, repo))

# Output as newline-separated: name|repo
for name, repo in projects:
    print(f"{name}|{repo}")
PYTHON_EOF
)

if [[ $? -ne 0 ]]; then
    error "Failed to parse portfolio configuration"
fi

if [[ -z "$PROJECTS" ]]; then
    error "No projects found for portfolio: $PORTFOLIOS"
fi

log "Found projects to setup:"
echo "$PROJECTS" | while IFS='|' read -r name repo; do
    log "  - $name ($repo)"
done

# ============================================================================
# Create Workspace Directory
# ============================================================================

if [[ -d "$WORKSPACE_PATH" ]]; then
    warn "Workspace path already exists: $WORKSPACE_PATH"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log "Cancelled."
        exit 0
    fi
else
    log "Creating workspace directory: $WORKSPACE_PATH"
    mkdir -p "$WORKSPACE_PATH"
fi

# ============================================================================
# Clone Projects
# ============================================================================

log "Setting up projects using strategy: $STRATEGY"

cd "$WORKSPACE_PATH" || error "Failed to enter workspace directory"

echo "$PROJECTS" | while IFS='|' read -r name repo; do
    if [[ -z "$name" ]] || [[ -z "$repo" ]]; then
        continue
    fi
    
    PROJECT_PATH="$WORKSPACE_PATH/$name"
    
    if [[ -d "$PROJECT_PATH" ]]; then
        log "Project already exists: $name"
        continue
    fi
    
    # Build repository URL
    if [[ "$repo" == git@* ]]; then
        REPO_URL="$repo"
    else
        REPO_URL="git@github.com:$repo.git"
    fi
    
    case "$STRATEGY" in
        worktree)
            log "Adding worktree: $name"
            if git worktree add -q "$name" origin/main 2>/dev/null || \
               git worktree add "$name" main 2>/dev/null; then
                log "✓ Worktree created: $name"
            else
                warn "Worktree setup incomplete (repository may need to be cloned first)"
            fi
            ;;
        clone)
            log "Cloning repository: $name"
            if git clone -q "$REPO_URL" "$name"; then
                log "✓ Repository cloned: $name"
            else
                warn "Failed to clone: $name"
            fi
            ;;
        *)
            error "Unknown strategy: $STRATEGY"
            ;;
    esac
done

# ============================================================================
# Create Workspace Configuration
# ============================================================================

log "Creating workspace configuration..."

cat > "$WORKSPACE_PATH/.portfolio-workspace" << WORKSPACE_CONFIG
# Portfolio Workspace Configuration
# Generated by setup-portfolio-workspace.sh

PORTFOLIO_SELECTION="$PORTFOLIOS"
WORKSPACE_PATH="$WORKSPACE_PATH"
CREATED_AT="$(date -Iseconds)"
STRATEGY="$STRATEGY"

# Top-level portfolio project
PORTFOLIO_PROJECT="$PROJECT_ROOT"
PORTFOLIO_CONFIG="$PORTFOLIO_CONFIG"

# Projects in this workspace:
PROJECTS="$PROJECTS"
WORKSPACE_CONFIG

log "✓ Workspace configuration created: $WORKSPACE_PATH/.portfolio-workspace"

# ============================================================================
# GSD Integration Instructions
# ============================================================================

log ""
log "=========================================="
log "Workspace Setup Complete!"
log "=========================================="
log ""
log "Workspace Path: $WORKSPACE_PATH"
log "Portfolio Selection: $PORTFOLIOS"
log "Strategy: $STRATEGY"
log ""
log "Next steps:"
log "  1. cd $WORKSPACE_PATH"
log "  2. Create or update GSD workspace:"
log "       gsd-new-workspace --name ${PORTFOLIOS}-ws --strategy $STRATEGY --path $WORKSPACE_PATH"
log "  3. Start development with GSD:"
log "       cd $PROJECT_ROOT"
log "       portfolio-dev.py $PORTFOLIOS --status"
log ""
log "To clean up workspace:"
log "  rm -rf $WORKSPACE_PATH"
log ""

