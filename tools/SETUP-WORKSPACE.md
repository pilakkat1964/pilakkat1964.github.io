# Portfolio Workspace Setup

**setup-portfolio-workspace.sh** creates a new GSD workspace with selected portfolio projects.

## Quick Start

```bash
# Create workspace for core portfolio
bash tools/setup-portfolio-workspace.sh --portfolios core --path ~/workspace/main-ws

# Create workspace for z-tools portfolio  
bash tools/setup-portfolio-workspace.sh --portfolios z-tools --path ~/workspace/z-tools-ws

# Create workspace for all portfolios
bash tools/setup-portfolio-workspace.sh --portfolios all --path ~/workspace/all-ws
```

## Options

```
--portfolios PORTFOLIO   Portfolio selection: core, z-tools, others, all (required)
--path PATH              Workspace root path (required)
--strategy STRATEGY      Git strategy: worktree (default) or clone
--help                   Show help message
```

### Portfolio Selection

- `core` - Main site + blog + CV (3 projects)
- `z-tools` - Z-tools ecosystem (5 projects)
- `others` - Standalone projects (1+ projects)
- `all` - All portfolios and projects

### Git Strategy

- `worktree` (default) - Use git worktrees (lightweight, shares objects)
- `clone` - Clone each project separately (independent copies)

**Recommendation:** Use `worktree` for faster setup and disk efficiency.

## Workflows

### Basic Setup

```bash
# 1. Create workspace for core portfolio
bash tools/setup-portfolio-workspace.sh --portfolios core --path ~/workspace/main

# 2. Enter workspace
cd ~/workspace/main

# 3. Check what's there
ls -la
# Output:
# .portfolio-workspace  (configuration file)
# pilakkat1964.github.io/
# blog/
# cv/

# 4. Check project status
cd ..
python3 tools/portfolio-dev.py core --status
```

### GSD Integration

```bash
# 1. Create workspace with GSD
bash tools/setup-portfolio-workspace.sh --portfolios core --path ~/workspace/gsd-main

# 2. Create GSD workspace
cd pilakkat1964.github.io
gsd-new-workspace \
  --name core-dev \
  --strategy worktree \
  --path ~/workspace/gsd-main

# 3. Start development
gsd-discuss-phase

# 4. Use portfolio orchestrator
python3 tools/portfolio-dev.py core --new-branch feature/new-feature
```

### Multiple Portfolios

```bash
# Create separate workspaces for different portfolios
bash tools/setup-portfolio-workspace.sh --portfolios core --path ~/workspace/core
bash tools/setup-portfolio-workspace.sh --portfolios z-tools --path ~/workspace/z-tools
bash tools/setup-portfolio-workspace.sh --portfolios others --path ~/workspace/others

# Work on each independently
cd ~/workspace/core && python3 tools/portfolio-dev.py core --status
cd ~/workspace/z-tools && python3 tools/portfolio-dev.py z-tools --status
```

### Development Workflow

```bash
# 1. Set up workspace
bash tools/setup-portfolio-workspace.sh --portfolios z-tools --path ~/workspace/z-dev

# 2. Enter workspace
cd ~/workspace/z-dev

# 3. Check status
python3 ../../tools/portfolio-dev.py z-tools --status

# 4. Create feature branch
python3 ../../tools/portfolio-dev.py z-tools --new-branch feature/my-feature

# 5. Make changes in projects
# ... edit files in z-tools/, z-open/, etc.

# 6. Commit changes
python3 ../../tools/portfolio-dev.py z-tools --commit-all "feat: implement new feature"

# 7. Validate links
python3 ../../tools/portfolio-dev.py z-tools --validate --dry-run

# 8. Push changes
python3 ../../tools/portfolio-dev.py z-tools --push
```

## Workspace Structure

After setup, your workspace contains:

```
~/workspace/main-ws/
├── .portfolio-workspace        # Configuration file
├── pilakkat1964.github.io/     # Main site
├── blog/                       # Blog project
└── cv/                         # CV project
```

The `.portfolio-workspace` file records:

```bash
PORTFOLIO_SELECTION="core"
WORKSPACE_PATH="~/workspace/main-ws"
CREATED_AT="2026-04-16T22:00:00+00:00"
STRATEGY="worktree"
PORTFOLIO_PROJECT="/path/to/pilakkat1964.github.io"
PORTFOLIO_CONFIG="/path/to/tools/portfolio-config.yaml"
PROJECTS="pilakkat1964.github.io|pilakkat1964/pilakkat1964.github.io
blog|pilakkat1964/blog
cv|pilakkat1964/cv"
```

## Workspace Operations

### Check Workspace Info

```bash
cat ~/workspace/main-ws/.portfolio-workspace
```

### Remove Workspace

```bash
rm -rf ~/workspace/main-ws
```

### Clone Missing Projects

If some projects weren't cloned, add them manually:

```bash
cd ~/workspace/main-ws
git clone git@github.com:pilakkat1964/project-name.git project-name
```

### Update Workspace

Re-run setup to add or update projects:

```bash
bash tools/setup-portfolio-workspace.sh --portfolios all --path ~/workspace/main-ws
```

The script will:
- Skip existing projects
- Add new projects
- Preserve existing work

## Troubleshooting

### "Workspace path already exists"

You'll be prompted to continue. Choose:
- `y` - Continue with existing path
- `n` - Cancel and use different path

To remove and start fresh:
```bash
rm -rf ~/workspace/main-ws
bash tools/setup-portfolio-workspace.sh --portfolios core --path ~/workspace/main-ws
```

### "Project not found after setup"

Some projects may be empty repositories or not yet created. This is normal.

Check what exists:
```bash
ls -la ~/workspace/main-ws/
```

Clone missing projects manually:
```bash
cd ~/workspace/main-ws
git clone git@github.com:pilakkat1964/project-name.git project-name
```

### "Worktree setup incomplete"

Worktrees require the repository to exist first. Solutions:

1. Use `clone` strategy instead:
   ```bash
   bash tools/setup-portfolio-workspace.sh --portfolios core --path ~/workspace/main-ws --strategy clone
   ```

2. Or bootstrap the repository first and retry

### Permission denied

Ensure you have SSH credentials configured:

```bash
ssh -T git@github.com
# Should output: Hi username! You've successfully authenticated...
```

If not configured, see [GitHub SSH Setup](https://docs.github.com/en/authentication/connecting-to-github-with-ssh).

## Advanced Usage

### Workspace with Custom Strategy

```bash
# Use clone strategy (independent copies, more disk space)
bash tools/setup-portfolio-workspace.sh \
  --portfolios all \
  --path ~/workspace/all-separate \
  --strategy clone
```

### Nested Workspaces

Create workspaces within workspaces for nested GSD phases:

```bash
# Main workspace
bash tools/setup-portfolio-workspace.sh --portfolios core --path ~/workspace/main

# Phase-specific workspace
cd ~/workspace/main/pilakkat1964.github.io
gsd-new-workspace --name phase-1-ws --path ~/workspace/phase-1
```

### Automation

Script workspace creation:

```bash
#!/bin/bash
for portfolio in core z-tools others; do
  bash tools/setup-portfolio-workspace.sh \
    --portfolios "$portfolio" \
    --path ~/workspace/"$portfolio"-ws
done
```

## Integration Points

### With portfolio-dev.py

Workspaces are designed to work seamlessly with **portfolio-dev.py**:

```bash
cd ~/workspace/main-ws
python3 ../../tools/portfolio-dev.py core --status
```

### With GSD

Workspaces integrate with GSD workflows:

```bash
cd ~/workspace/main-ws
gsd-new-workspace --name core-dev
gsd-discuss-phase
gsd-plan-phase
gsd-execute-phase
```

### With Link Validation

Validate links within workspace:

```bash
cd ~/workspace/main-ws
python3 ../../tools/validate-links.py --profile core --dry-run
```

## Performance Tips

### Reduce Setup Time

Use `worktree` strategy (default):
```bash
# Fast (worktrees, shared objects)
bash tools/setup-portfolio-workspace.sh --portfolios core --path ~/ws --strategy worktree

# Slow (independent clones)
bash tools/setup-portfolio-workspace.sh --portfolios core --path ~/ws --strategy clone
```

### Reduce Disk Usage

Use `worktree` strategy with shallow clones. Worktrees share git objects while maintaining separate working directories.

Typical sizes:
- Worktree: ~100MB for core portfolio
- Clone: ~500MB for core portfolio (independent objects)

