# Cross-Repository Link Validator

**validate-links.py** checks for broken links across multiple Jekyll sites with different baseurls.

## Quick Start

```bash
# List available profiles
python3 tools/validate-links.py --profile core --list-profiles

# Validate core portfolio (dry-run)
python3 tools/validate-links.py --profile core --dry-run

# Generate JSON report
python3 tools/validate-links.py --profile core --report-json

# Auto-fix broken links (when implemented)
python3 tools/validate-links.py --profile core --fix
```

## Available Profiles

### core
Validates main site + blog + CV links.

```bash
python3 validate-links.py --profile core --dry-run
```

Projects:
- `pilakkat1964.github.io` - Main site
- `blog` - Blog posts
- `cv` - Resume

### z-tools
Validates z-tools portfolio links.

```bash
python3 validate-links.py --profile z-tools --dry-run
```

Projects:
- `z-tools` - Portfolio site

### all
Validates all projects across all portfolios.

```bash
python3 validate-links.py --profile all --dry-run
```

## Commands

### list-profiles
Show all available validation profiles.

```bash
python3 validate-links.py --profile core --list-profiles
```

### Validation (default)
Run link validation and report results.

```bash
python3 validate-links.py --profile core
```

**Options:**
- `--dry-run` - Show what would be fixed without making changes
- `--fix` - Automatically fix broken links (when implemented)
- `--report-json` - Output as JSON instead of text

## Output

### Text Report (Default)

```
============================================================
Link Validation Report: core
============================================================

Total Links: 245
Valid Links: 243
Broken Links: 2
Success Rate: 99.2%

Broken Links:
------------------------------------------------------------

✗ /blog/posts/nonexistent
  File: blog/_posts/2026-01-15-test.md:42
  Reason: Broken link - file not found: /posts/nonexistent
  Context: Check [this post](/blog/posts/nonexistent) for details

✗ /cv/skills
  File: cv/index.md:15
  Reason: Broken link - file not found: /skills
  Context: My [skills](/cv/skills) are documented here

============================================================
```

### JSON Report

```bash
python3 validate-links.py --profile core --report-json
```

```json
{
  "summary": {
    "profile": "core",
    "total_links": 245,
    "valid_links": 243,
    "broken_links": 2,
    "success_rate": "99.2%"
  },
  "broken_links": [
    {
      "url": "/blog/posts/nonexistent",
      "file": "blog/_posts/2026-01-15-test.md",
      "line": 42,
      "reason": "Broken link - file not found: /posts/nonexistent",
      "context": "Check [this post](/blog/posts/nonexistent) for details"
    }
  ]
}
```

## Link Types

### Internal Links
Links within the same project.

```markdown
[Home](/) in main site
[Archives](/archive) in blog
```

### Cross-Project Links
Links between different Jekyll sites (different baseurls).

```markdown
[Read my blog](/blog/posts)
[View my CV](/cv)
[Z-tools portfolio](/z-tools)
```

### External Links
Links to external websites (not validated locally).

```markdown
[GitHub](https://github.com)
[Python](https://python.org)
```

## Configuration

### link-validation-config.yaml

Defines validation profiles and rules:

```yaml
profiles:
  core:
    description: "Validate main site + blog + CV links"
    projects:
      - pilakkat1964.github.io
      - blog
      - cv
    rules:
      - rule_id: "internal_links"
        pattern: "^/"
        scope: "pilakkat1964.github.io"
    behavior:
      on_broken: "warn"
      on_external: "skip"
      auto_fix: false
```

**Profile fields:**
- `description` - Profile purpose
- `projects` - List of projects to validate
- `rules` - Validation rules (for future extension)
- `behavior` - How to handle issues

**Behavior options:**
- `on_broken` - "ignore", "warn" (default), or "error"
- `on_external` - "ignore", "warn", or "skip" (default)
- `auto_fix` - true/false (for future implementation)

### portfolio-config.yaml

Link validator references portfolio configuration to:
- Locate project directories
- Understand baseurl contexts
- Map links to projects

## Workflows

### Continuous Link Validation

```bash
# Before committing changes
python3 validate-links.py --profile core --dry-run

# In CI/CD pipeline
python3 validate-links.py --profile core
```

### Integration with portfolio-dev.py

```bash
# Validate after creating new content
python3 portfolio-dev.py core --validate --dry-run

# Validate before pushing
python3 portfolio-dev.py core --validate
```

### Multi-Portfolio Validation

```bash
# Validate each portfolio separately
python3 validate-links.py --profile core --dry-run
python3 validate-links.py --profile z-tools --dry-run

# Or validate all at once
python3 validate-links.py --profile all --dry-run
```

## Troubleshooting

### "Project not found"

The validator skips projects that don't exist locally. This is normal in fresh clones.

Solution: Clone the projects first:
```bash
bash tools/setup-portfolio-workspace.sh --portfolios core --path ~/workspace
```

### "All links valid" but I see broken ones

The validator might not be detecting all link types. Check:

1. Link format - supports markdown `[text](url)` and HTML `href="url"`
2. File extensions - scans `.md` and `.html` files
3. File location - looks recursively in project directory

### External links showing as broken

External links starting with `http://` or `https://` are intentionally skipped.

To validate external links, use a separate tool like `linkchecker`:
```bash
linkchecker https://pilakkat.mywire.org
```

## Advanced Usage

### Parse links from custom files

Modify link parser to include more file types:

```python
# In validate-links.py, LinkParser.extract_all_links()
for file_path in base_path.rglob('*'):
    if file_path.is_file() and file_path.suffix in ['.md', '.html', '.yml']:
        # ... process file
```

### Create custom validation profile

Add to `link-validation-config.yaml`:

```yaml
profiles:
  custom:
    description: "Custom validation"
    projects:
      - my-project
    behavior:
      on_broken: "error"
      auto_fix: true
```

Then use:
```bash
python3 validate-links.py --profile custom
```

### Override per-portfolio

Portfolio leads can have their own `link-validation-config.yaml`:

```
z-tools/
├── link-validation-config.yaml  # Overrides toplevel
└── portfolio-orchestrator.py
```

The validator checks portfolio-level config first, falls back to toplevel.

## Exit Codes

- `0` - All links valid or no broken links found
- `1` - Broken links found or validation error

Use for CI/CD integration:

```bash
python3 validate-links.py --profile core
if [ $? -eq 0 ]; then
    echo "✓ All links valid"
else
    echo "✗ Broken links found"
    exit 1
fi
```

