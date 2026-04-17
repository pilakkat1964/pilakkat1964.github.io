# Multi-Level Portfolio Site Hierarchy Navigation

## Overview

This document describes the shared navigation scheme used across portfolio systems where multiple project documentation sites are hierarchically organized. This pattern is reusable across different portfolio instances with varying scope and composition.

The basic pattern consists of:
- **Level 1 (Portfolio Lead)**: A parent portfolio site that aggregates and links child projects
- **Level 2+ (Projects)**: Individual project documentation sites with automatic "up" navigation to parent

Example hierarchy (Z-Tools Portfolio):
```
Z-Tools Portfolio (Level 1)
├── Z-Edit (Level 2)
├── Z-Open (Level 2)
├── Z-Kitty Launcher (Level 2)
└── Z-RClone Mount Applete (Level 2)
```

Each project has its own dedicated documentation site with automatic navigation between parent and child sites.

## General Site Structure

### Level 1: Portfolio Lead Site
- **Purpose**: Unified entry point showing all projects in the portfolio
- **Theme**: Project-specific (e.g., Minimal Mistakes for portfolios, Architect for projects)
- **Navigation**: 
  - Forward links: "Navigate the Ecosystem" or "Projects" section showing all child projects
  - Backward link: Optional parent link to upper-level portfolio (if applicable)
- **Configuration**: `hierarchy_level: 1`

### Level 2+: Project/Child Sites
- **Purpose**: Detailed project documentation and guides
- **Theme**: Consistent across all projects in portfolio (e.g., Architect)
- **Navigation**:
  - Forward links: Cross-project links to related projects
  - Backward link: "↑ Up to [Portfolio Name]" at top of all pages
- **Configuration**: `hierarchy_level: 2` (or higher for multi-level hierarchies)

## Navigation Implementation

### Configuration-Driven System

Each Jekyll site defines hierarchy metadata in `docs/_config.yml`:

```yaml
# Portfolio Lead (Level 1)
hierarchy_level: 1
hierarchy_parent_url: /                                    # Root or parent portfolio
hierarchy_parent_title: "Parent Portfolio or Site Name"

# Project Sites (Level 2)
hierarchy_level: 2
hierarchy_parent_url: /portfolio-path                      # Path to parent portfolio
hierarchy_parent_title: "Portfolio Name"
```

### Automatic Navigation Include

All sites use standardized `docs/_includes/hierarchy-nav.html`:

```html
{% if site.hierarchy_level and site.hierarchy_level > 1 %}
  <!-- Site Hierarchy Navigation -->
  <div style="background-color: #f5f5f5; border-bottom: 1px solid #ddd; padding: 12px 0; margin-bottom: 20px;">
    {% if site.hierarchy_parent_url %}
      <div style="padding: 0 15px;">
        <a href="{{ site.hierarchy_parent_url }}" style="color: #0366d6; text-decoration: none; font-size: 14px;">
          ↑ Up to {{ site.hierarchy_parent_title }}
        </a>
      </div>
    {% endif %}
  </div>
{% endif %}
```

**Key Design Decisions:**
- Only displays for Level 2+ sites (not on portfolio root)
- Uses absolute URLs without Jekyll filters (prevents baseurl doubling)
- Level-based visibility prevents redundant navigation
- Consistent styling across all projects

### Layout Integration

The include is called from the page layout that will be used for each theme:

**For Minimal Mistakes Theme (Portfolio Leads)**:
- Create/override `docs/_includes/page__content.html`
- Add `{% include hierarchy-nav.html %}` after opening tag

**For Architect Theme (Projects)**:
- Add `{% include hierarchy-nav.html %}` to `docs/_layouts/default.html`
- Place near top of page content for prominence

### Forward Navigation

Portfolio leads should include a "Navigate the Ecosystem" or "Projects" section in their homepage:

```markdown
## Projects in This Portfolio

- **[Project 1 Name](url)** - Project 1 description
- **[Project 2 Name](url)** - Project 2 description
- **[Project 3 Name](url)** - Project 3 description
```

Child projects can include cross-project links in their navigation or sidebar for discoverability.

## Implementation Checklist

### For Portfolio Lead (Level 1)

- [ ] Set `hierarchy_level: 1` in `docs/_config.yml`
- [ ] Set `hierarchy_parent_url: /` (or path to parent portfolio)
- [ ] Set `hierarchy_parent_title` to parent name
- [ ] Create/include `docs/_includes/hierarchy-nav.html` if desired
- [ ] Add "Projects/Ecosystem" section to homepage listing child projects
- [ ] Link to all child projects with descriptive text

### For Project Sites (Level 2+)

- [ ] Set `hierarchy_level: 2` in `docs/_config.yml`
- [ ] Set `hierarchy_parent_url: /path-to-parent` (e.g., `/z-tools`)
- [ ] Set `hierarchy_parent_title: "Parent Portfolio Name"`
- [ ] Copy `docs/_includes/hierarchy-nav.html` to project repo
- [ ] Add `{% include hierarchy-nav.html %}` to appropriate layout file
- [ ] Test that "↑ Up to [Parent]" link appears on all pages
- [ ] Verify link points to correct parent URL

## Troubleshooting Common Issues

### Navigation Not Showing

**Problem**: "Up to Parent" link not visible on child project pages

**Check List**:
1. Verify `hierarchy_level: 2` in `docs/_config.yml`
2. Verify `hierarchy_parent_url` is defined
3. Verify include file exists at `docs/_includes/hierarchy-nav.html`
4. Verify include is called in layout file
5. Check Jekyll build log for errors
6. Verify site rebuild after changes (GitHub Pages may cache)

**Fix**:
```yaml
# docs/_config.yml
hierarchy_level: 2
hierarchy_parent_url: /parent-path
hierarchy_parent_title: "Parent Name"
```

### Links Pointing to Wrong Location

**Problem**: Navigation links show incorrect URLs (e.g., `/parent/parent` instead of `/parent`)

**Cause**: The `relative_url` Jekyll filter is being applied to absolute URLs

**Fix**: Remove the filter from hierarchy-nav.html:
```html
<!-- WRONG: -->
<a href="{{ site.hierarchy_parent_url | relative_url }}">

<!-- CORRECT: -->
<a href="{{ site.hierarchy_parent_url }}">
```

### Navigation Showing on Portfolio Lead

**Problem**: "Up to Parent" link appears on portfolio lead site (shouldn't)

**Cause**: The conditional `site.hierarchy_level > 1` is not working

**Fix**: Ensure `hierarchy_level: 1` is set in portfolio lead's `_config.yml`:
```yaml
# docs/_config.yml for portfolio lead
hierarchy_level: 1
```

### Navigation Not Styled Consistently

**Problem**: Navigation bar looks different across projects

**Solution**: Standardize the CSS in `hierarchy-nav.html`. Use the provided styles:
```html
<div style="background-color: #f5f5f5; border-bottom: 1px solid #ddd; padding: 12px 0; margin-bottom: 20px;">
```

Alternatively, move styles to a shared CSS file if managing multiple portfolios.

## Maintenance Guide

### Adding a New Project to Existing Portfolio

1. **Create Jekyll documentation** in project's `docs/` folder
2. **Add hierarchy metadata** to project's `docs/_config.yml`:
   ```yaml
   hierarchy_level: 2
   hierarchy_parent_url: /portfolio-path
   hierarchy_parent_title: "Portfolio Name"
   ```
3. **Copy navigation include**:
   - Source: `/path-to-portfolio-lead/docs/_includes/hierarchy-nav.html`
   - Destination: `docs/_includes/hierarchy-nav.html` in new project
4. **Add include to layout** file
5. **Update portfolio lead homepage** to include new project in projects list

### Updating Navigation Links

If portfolio lead URL changes:

1. Update `hierarchy_parent_url` in ALL child projects' `_config.yml`
2. Update forward links in portfolio lead homepage
3. Test all links after deployment

### Adapting for Different Portfolio Scope

This navigation scheme is flexible and works for portfolios of any size:

**Small Portfolio (3-5 projects)**:
- Use standard 2-level hierarchy
- Simple project list on homepage

**Large Portfolio (10+ projects)**:
- Group projects by category on homepage
- Consider sub-portfolios (3-level hierarchy)
- Add search functionality for discoverability

**Multi-Portfolio Instance**:
- Each portfolio uses same navigation scheme independently
- Portfolio lead sites link to each other if needed
- Shared navigation.html include can be copied to all portfolios

## Example Implementations

### Z-Tools Portfolio (Production)
- **Portfolio**: https://pilakkat.mywire.org/z-tools/
- **Projects**: z-edit, z-open, z-kitty-launcher, z-rclone-mount-applete
- **Status**: ✅ Implemented and working
- **Theme**: Minimal Mistakes (portfolio), Architect (projects)

### Expanding to Multiple Portfolios

When adding "Others" portfolio:
1. Create `others/` directory structure identical to z-tools
2. Copy `docs/_includes/hierarchy-nav.html` to `others/docs/_includes/`
3. Set up `others/docs/_config.yml` with `hierarchy_level: 1`
4. Add projects to `portfolio-config.yaml` (toplevel) with `type: portfolio`

## Files Involved

### Shared Files (Can be copied across portfolios)
- `docs/_includes/hierarchy-nav.html` — Standard navigation include
- `docs/_layouts/default.html` — Modified to include hierarchy-nav (theme-specific)

### Portfolio-Specific Files
- `docs/_config.yml` — Hierarchy metadata (portfolio-specific values)
- `docs/index.md` — Homepage with project links (portfolio-specific content)

### Documentation
- `NAVIGATION.md` — This file (can be placed in toplevel and referenced)

## Version History

**April 17, 2026**: Initial shared navigation documentation
- Z-Tools Portfolio implementation complete
- Schema tested and validated
- Ready for replication across multiple portfolio instances

## References

- **Z-Tools Portfolio**: Working reference implementation
- **GitHub Pages**: https://pages.github.com/
- **Jekyll Includes**: https://jekyllrb.com/docs/includes/
- **Minimal Mistakes**: https://mmistakes.github.io/minimal-mistakes/
- **Architect Theme**: https://github.com/pages-themes/architect

