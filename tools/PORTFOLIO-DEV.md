# Portfolio Development Orchestrator

**portfolio-dev.py** is a command-line tool that manages multi-repository portfolio projects with a plugin architecture for extensibility.

## Quick Start

```bash
# List all available portfolios
python3 tools/portfolio-dev.py list

# List portfolios with details
python3 tools/portfolio-dev.py list --verbose

# Check portfolio status
python3 tools/portfolio-dev.py core --status

# Create a new feature branch in all projects
python3 tools/portfolio-dev.py core --new-branch feature/my-feature

# Commit all changes across projects
python3 tools/portfolio-dev.py core --commit-all "message: implement feature X"

# Push all changes
python3 tools/portfolio-dev.py core --push

# Validate cross-project links
python3 tools/portfolio-dev.py core --validate --dry-run
```

## Available Portfolios

### Core Portfolio
The main website with blog and CV.

```bash
python3 portfolio-dev.py core --status
```

Projects:
- `pilakkat1964.github.io` - Main landing site
- `blog` - Technical blog
- `cv` - Resume/CV

### Z-Tools Portfolio
Portfolio of productivity tools.

```bash
python3 portfolio-dev.py z-tools --status
```

Projects:
- `z-tools` - Portfolio lead (Jekyll site + orchestration)
- `z-open` - Python utility
- `z-edit` - Python utility
- `z-kitty-launcher` - Rust utility
- `z-rclone-mount-applete` - Rust utility

### Others Portfolio
Standalone projects that don't fit other portfolios.

```bash
python3 portfolio-dev.py others --status
```

Projects:
- `LinearAlgebra-4-CV-DL` - Python project

### All Portfolios
Meta-portfolio combining all projects. Typically used for listing and general information.

## Commands

### list
List all available portfolios.

```bash
python3 portfolio-dev.py list
python3 portfolio-dev.py list --verbose
```

**Options:**
- `--verbose` - Show detailed project information for each portfolio

### setup
Prepare a portfolio for development.

```bash
python3 portfolio-dev.py core --setup
```

Performs:
- Validates prerequisites (git, Python)
- Checks bootstrap requirements
- Prepares environment

### status
Show current status of all projects in a portfolio.

```bash
python3 portfolio-dev.py core --status
```

Returns JSON with:
- Project names and repositories
- Git clone status
- Uncommitted changes count
- Current branch
- Clean/dirty state

**Example output:**
```json
{
  "portfolio": "core",
  "projects": [
    {
      "name": "pilakkat1964.github.io",
      "repo": "pilakkat1964/pilakkat1964.github.io",
      "exists": false,
      "cloned": false
    },
    {
      "name": "blog",
      "repo": "pilakkat1964/blog",
      "exists": true,
      "cloned": true,
      "status": "dirty",
      "changes": 2,
      "current_branch": "main"
    }
  ]
}
```

### new-branch
Create a new feature branch in all projects of a portfolio.

```bash
python3 portfolio-dev.py core --new-branch feature/my-feature
```

**What happens:**
- Creates branch `feature/my-feature` in each project
- Switches to new branch
- Ready for development

**Naming conventions:**
- `feature/description` - New feature
- `fix/description` - Bug fix
- `docs/description` - Documentation
- `refactor/description` - Code refactoring

### commit-all
Commit all staged and unstaged changes across all projects.

```bash
python3 portfolio-dev.py core --commit-all "message: implement feature X"
```

**What happens:**
- Stages all changes (`git add -A`)
- Creates commit with message in each project
- Skips projects with no changes

**Tips:**
- Use conventional commit format: `type: description`
- Examples: `feat: add new feature`, `fix: correct bug`, `docs: update readme`

### push
Push all committed changes across all projects.

```bash
python3 portfolio-dev.py core --push
```

**What happens:**
- Pushes to remote tracking branch
- One project failure doesn't stop others
- Shows summary of successes/failures

### validate
Validate cross-project links.

```bash
python3 portfolio-dev.py core --validate --dry-run
python3 portfolio-dev.py core --validate --fix
```

**Options:**
- `--dry-run` - Show what would be fixed without making changes
- `--fix` - Automatically fix broken links

For full link validation documentation, see [VALIDATE-LINKS.md](./VALIDATE-LINKS.md).

## Architecture

### Plugin System

**portfolio-dev.py** uses a plugin architecture to support portfolio leads with customized orchestration logic:

```
portfolio-dev.py (toplevel orchestrator)
├── Built-in plugins: core, all
└── Dynamic plugins: z-tools, others, ...
    └── Load from: <portfolio>/portfolio-orchestrator.py
```

### Plugin Interface

Each portfolio plugin must implement:

```python
class PortfolioOrchestrator(PluginInterface):
    def validate_setup(self) -> (bool, list[str])
    def setup(self) -> bool
    def get_status(self) -> dict
    def new_branch(self, branch_name: str) -> bool
    def commit_all(self, message: str) -> bool
    def push(self) -> bool
```

### Creating a Custom Portfolio

To create a new portfolio with customized behavior:

1. Create portfolio lead repository
2. Create `portfolio-orchestrator.py` in root
3. Implement `PortfolioOrchestrator` class
4. Register in `tools/portfolio-config.yaml`

Example:

```yaml
others:
  description: "Other portfolio projects"
  type: "plugin"
  plugin_path: "others/portfolio-orchestrator.py"
  projects:
    - repo: "pilakkat1964/LinearAlgebra-4-CV-DL"
```

## Configuration

### portfolio-config.yaml

Central configuration for all portfolios:

```yaml
portfolios:
  core:
    description: "Main website + blog + CV"
    type: "builtin"
    projects:
      - repo: "pilakkat1964/pilakkat1964.github.io"
        name: "pilakkat1964.github.io"
```

**Portfolio types:**
- `builtin` - Implemented in portfolio-dev.py
- `plugin` - Loaded from external portfolio-orchestrator.py

**Project fields:**
- `repo` - Repository reference
- `name` - Local directory name
- `language` - Programming language
- `role` - Optional role (e.g., "lead" for portfolio leads)

## Workflows

### Starting Development

```bash
# 1. List portfolios to choose which to work on
python3 portfolio-dev.py list --verbose

# 2. Check current status
python3 portfolio-dev.py z-tools --status

# 3. Create feature branch
python3 portfolio-dev.py z-tools --new-branch feature/my-feature

# 4. Make changes in projects...

# 5. Check status before committing
python3 portfolio-dev.py z-tools --status

# 6. Commit all changes
python3 portfolio-dev.py z-tools --commit-all "feat: implement new feature"

# 7. Validate links
python3 portfolio-dev.py z-tools --validate --dry-run

# 8. Push changes
python3 portfolio-dev.py z-tools --push
```

### Multi-Portfolio Development

```bash
# Work on core first
python3 portfolio-dev.py core --new-branch feature/unified
python3 portfolio-dev.py core --commit-all "feat: update main site"
python3 portfolio-dev.py core --push

# Then work on z-tools
python3 portfolio-dev.py z-tools --new-branch feature/unified
python3 portfolio-dev.py z-tools --commit-all "feat: update portfolio lead"
python3 portfolio-dev.py z-tools --push
```

### Release Workflow

```bash
# Check status across all projects
python3 portfolio-dev.py all --status

# Create release branch in core
python3 portfolio-dev.py core --new-branch release/v1.0

# Commit final changes
python3 portfolio-dev.py core --commit-all "release: v1.0"

# Validate all links before publishing
python3 portfolio-dev.py core --validate

# Push to GitHub
python3 portfolio-dev.py core --push
```

## Troubleshooting

### "Project not found, skipping"

This occurs when a project in the portfolio isn't cloned locally. Solutions:

1. Clone the project manually:
   ```bash
   git clone git@github.com:pilakkat1964/project-name.git project-name
   ```

2. Or use workspace setup:
   ```bash
   bash tools/setup-portfolio-workspace.sh --portfolios core --path ~/workspace/main-ws
   ```

### "No changes to commit"

This is normal when there are no modifications. The command succeeds silently.

### Failed commands in one project

Commands continue with other projects even if one fails. Check the exit code:
- `0` = all succeeded
- `1` = one or more failed

Use `--status` to check which projects have issues.

## Integration with GSD

**portfolio-dev.py** integrates with GSD workflows:

```bash
# Set up GSD workspace with portfolio
bash tools/setup-portfolio-workspace.sh --portfolios core --path ~/workspace/gsd-ws

# Use GSD to plan and execute phases
cd ~/workspace/gsd-ws
gsd-new-workspace --name core-dev
```

See [SETUP-WORKSPACE.md](./SETUP-WORKSPACE.md) for details.

## Advanced Usage

### JSON Output

All status commands output JSON for scripting:

```bash
python3 portfolio-dev.py core --status | jq '.projects[] | select(.status == "dirty")'
```

### Verbose Output

Enable debug logging:

```bash
python3 portfolio-dev.py core --status --verbose
```

### Plugin Development

See [PORTFOLIO-STRUCTURE.md](../.planning/PORTFOLIO-STRUCTURE.md) for details on creating custom portfolio plugins.

