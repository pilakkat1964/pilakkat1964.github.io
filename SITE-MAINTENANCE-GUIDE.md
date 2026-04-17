# Site Maintenance Guide — pilakkat.mywire.org

## Overview

This guide covers day-to-day maintenance tasks for the pilakkat.mywire.org website, including updating content, managing navigation, monitoring site health, and troubleshooting common issues.

## Quick Reference

| Task | Repository | File(s) | Frequency |
|------|-----------|---------|-----------|
| Add blog post | `pilakkat1964/blog` | `_posts/YYYY-MM-DD-title.md` | As needed |
| Update CV | `pilakkat1964/cv` | Varies by theme | As needed |
| Update portfolio | `pilakkat1964.github.io` | `index.md`, `about.md` | As needed |
| Monitor build status | All three repos | `.github/workflows/` | Post-push |
| Check deployment | Live site | `https://pilakkat.mywire.org` | Post-build |
| Update navigation | Blog repo | `_layouts/home.html` | When structure changes |

## Managing Content

### Adding Blog Posts

1. **Location**: `blog/_posts/`
2. **Filename format**: `YYYY-MM-DD-title-with-hyphens.md`
3. **Example**: `2026-04-17-navigation-architecture.md`

**Front matter (mandatory)**:
```yaml
---
title: "Full Title of Post"
date: 2026-04-17 10:00:00 +0800
categories: [Category1, Category2]
tags: [tag1, tag2, tag3]
---
```

**Optional front matter**:
```yaml
---
author: Santhosh Kumar Pilakkat
pin: false  # Set to true to pin post to top
hidden: false  # Set to true to hide from listings
image:
  path: /path/to/image.jpg
  alt: Image description
---
```

**Content format**: Standard Markdown with support for:
- Headers (`# ## ### ####`)
- Bold/italic (`**bold** *italic*`)
- Links (`[text](url)`)
- Code blocks (with syntax highlighting)
- Lists (ordered and unordered)
- Blockquotes (`> quote`)
- Images (`![alt](url)`)

**Example post**:
```markdown
---
title: "Getting Started with Rust"
date: 2026-04-17 10:00:00 +0800
categories: [Programming]
tags: [rust, beginner]
---

# Introduction

This post explains how to get started with Rust...

## Installation

Follow these steps:

1. Install Rust: https://rustup.rs/
2. Run `rustc --version` to verify

## Your First Program

\`\`\`rust
fn main() {
    println!("Hello, world!");
}
\`\`\`

More content...
```

**Publishing**:
1. Commit and push to `blog` repo `main` branch
2. GitHub Actions will trigger automatically
3. Site rebuilds in ~2 minutes
4. Post appears on blog homepage and archive

### Updating Blog Posts

1. **Edit the markdown file** in `blog/_posts/`
2. **Update `date` field** if necessary (affects sorting)
3. **Commit and push**
4. **Site rebuilds automatically**

### Deleting Blog Posts

1. **Delete the file** from `blog/_posts/`
2. **Commit and push** with message: `remove: delete post title`
3. **Post disappears** from all listings automatically

### Updating Portfolio Content

**Main site** (`pilakkat1964.github.io`):
- Edit `index.md` for homepage
- Edit `about.md` for about page
- Create new markdown files for additional pages

**File format**:
```markdown
---
layout: page  # or post
title: Page Title
---

Page content in Markdown...
```

**URLs**: Files are served at their location
- `index.md` → `/`
- `about.md` → `/about/`
- `blog.md` → `/blog/` (if created)

### Updating CV

**CV repo** (`pilakkat1964/cv`):
- Edit `_data/data.yml` for content
- Update `assets/` for images/downloads
- Theme customization in `_sass/` (if needed)

See [CV README](https://github.com/pilakkat1964/cv/blob/master/README.md) for detailed instructions.

## Managing Navigation

### Navigation Architecture

**Current implementation**:
- Blog shows `↑ Site Home` link at top of homepage
- Child projects show `↑ Up to Parent` links
- Navigation styling matches theme colors

### Adding Navigation to New Pages

#### Blog (Chirpy Theme)

**File**: `_layouts/home.html`

**Current structure**:
```html
<style>
  .hierarchy-nav { /* styling */ }
</style>

<div class="hierarchy-nav">
  <a href="/" title="Navigate to site home">
    ↑ Site Home
  </a>
</div>

<!-- Rest of home layout content -->
```

**To add navigation to custom pages**:
1. Create `_layouts/custom.html`
2. Include hierarchy-nav div at top
3. Use layout in page front matter: `layout: custom`

#### Other Themes

**For minima theme** (main site):
- Edit `_includes/header.html` to add navigation
- Or create `_includes/nav-hierarchy.html` and include it

**For online-cv theme** (CV):
- Modify `_includes/header.html` or appropriate template

### Navigation Styling Guidelines

**Color palette** (match theme):
| Theme | Color | Code |
|-------|-------|------|
| Chirpy | Blue | `#0366d6` |
| minima | Blue | `#0275d8` |
| online-cv | Varies | Check theme |

**Styling template**:
```css
.hierarchy-nav {
  background: #f5f5f5;
  border-left: 4px solid [THEME-COLOR];
  border-bottom: 1px solid #ddd;
  padding: 12px 15px;
  margin: 0 -15px 20px -15px;  /* Adjust for theme spacing */
}
.hierarchy-nav a {
  color: [THEME-COLOR];
  text-decoration: none;
  font-size: 15px;
  font-weight: 600;
  transition: color 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.hierarchy-nav a:hover {
  color: [THEME-COLOR-DARKER];  /* 10% darker */
  text-decoration: underline;
}
```

## Monitoring Site Health

### Build Status

**Check GitHub Actions**:
1. Go to repository: `github.com/pilakkat1964/[repo-name]`
2. Click "Actions" tab
3. See workflow run status (green = success, red = failure)

**Workflow files**:
- `blog/.github/workflows/pages-deploy.yml` — Blog build/deploy
- `pilakkat1964.github.io/.github/workflows/pages-deploy.yml` — Main site
- `cv` uses GitHub Pages auto-build (no workflow file)

### Deployment Status

**GitHub Pages Deployments**:
1. Go to repository → "Deployments"
2. See active deployment URL
3. Click deployment for details

**For blog** (`pilakkat1964/blog`):
- Deploys to: `https://pilakkat1964.github.io/blog/`
- Custom domain: `https://pilakkat.mywire.org/blog/`

### Live Site Testing

**Checklist**:
- [ ] Homepage loads: `https://pilakkat.mywire.org/`
- [ ] Blog loads: `https://pilakkat.mywire.org/blog/`
- [ ] Latest post visible on blog homepage
- [ ] Blog post can be opened by clicking title
- [ ] Navigation links work (↑ Site Home)
- [ ] Search functionality works (blog)
- [ ] Categories/Tags work (blog)
- [ ] CSS styling loads correctly (no unstyled page)
- [ ] Images load correctly
- [ ] Mobile responsive (test on mobile device or browser dev tools)

**Quick test script**:
```bash
#!/bin/bash
echo "Testing site..."
curl -s https://pilakkat.mywire.org/ | grep -q "title" && echo "✅ Main site OK" || echo "❌ Main site ERROR"
curl -s https://pilakkat.mywire.org/blog/ | grep -q "hierarchy-nav" && echo "✅ Blog nav OK" || echo "❌ Blog nav ERROR"
curl -s https://pilakkat.mywire.org/blog/ | grep -q "post-list" && echo "✅ Blog posts OK" || echo "❌ Blog posts ERROR"
```

### Monitoring Performance

**Tools**:
- Google PageSpeed Insights: `https://pagespeed.web.dev/`
- GTmetrix: `https://gtmetrix.com/`
- WebPageTest: `https://www.webpagetest.org/`

**Key metrics**:
- Core Web Vitals (LCP, FID, CLS)
- Time to First Byte (TTFB)
- Fully Loaded Time

### Monitoring Uptime

**Tools**:
- UptimeRobot (free tier available)
- GitHub Status Page
- StatusCake (free tier)

**Recommended checks**:
```
GET https://pilakkat.mywire.org/ → expect 200
GET https://pilakkat.mywire.org/blog/ → expect 200
GET https://pilakkat.mywire.org/blog/feed.xml → expect 200
```

## Common Maintenance Tasks

### Update Ruby Version

**When**: When a new Ruby version is released and required by Chirpy or other gems

**Steps**:
1. Update `blog/Gemfile`: `ruby "3.X.Y"`
2. Update `blog/mise.toml`: `ruby = "3.X.Y"`
3. Delete `Gemfile.lock` (let CI regenerate it)
4. Commit and push
5. Monitor first GitHub Actions run for success

### Update Theme

**Chirpy blog theme**:
1. Check for updates: `cd blog && bundle update`
2. Review `Gemfile.lock` changes
3. Test locally: `bundle exec jekyll serve --baseurl /blog`
4. Commit and push if satisfied

### Add New Repository to Site

**If adding another Jekyll site** (e.g., `/projects/`):

1. Create new repo: `pilakkat1964/projects`
2. Set up Jekyll with desired theme
3. In `_config.yml`:
   ```yaml
   url: "https://pilakkat.mywire.org"
   baseurl: "/projects"
   ```
4. Set up GitHub Actions for deployment
5. Enable GitHub Pages deployment
6. Add navigation links in all sites pointing to new section
7. Update SITE-DESIGN.md with new architecture
8. Test that custom domain works

### Fix Broken Links

1. **Find broken links**:
   - Browser DevTools (F12) → Console tab
   - Or use: `htmlproofer _site/`
   
2. **Update links** in source files:
   - `blog/_posts/*.md`
   - `blog/_config.yml` (if config links)
   - Theme templates (if template links)

3. **Test locally** before pushing

### Restore from Backup

**GitHub is your backup**:
- All commits are stored on GitHub
- Revert to previous commit: `git revert [commit-hash]`
- Force push (if necessary): `git push --force-with-lease`

**Example - revert last commit**:
```bash
cd blog/
git revert HEAD
git push origin main
```

## Troubleshooting

### Blog Not Building

**Symptoms**: GitHub Actions workflow fails (red X)

**Steps**:
1. Check workflow log: Repo → Actions → Failed workflow run
2. Look for error message (usually in "Build site" step)
3. Common errors:
   - Syntax error in post front matter: Fix YAML
   - Missing required gem: Update `Gemfile.lock`
   - Invalid Markdown: Check syntax in post
4. Fix error, commit, push to retry

### Site Not Updating After Push

**Symptoms**: Changes don't appear on live site after 5+ minutes

**Steps**:
1. Verify push succeeded: `git status` shows "Your branch is up to date"
2. Check GitHub Actions: Repo → Actions → Latest workflow run
3. If workflow failed: Debug build error (see above)
4. If workflow succeeded:
   - Clear browser cache: Ctrl+Shift+Delete
   - Try incognito/private mode
   - Wait 5-10 minutes for CDN cache to clear

### Navigation Not Showing

**Symptoms**: `↑ Site Home` link missing from blog homepage

**Steps**:
1. Verify `_layouts/home.html` exists in blog repo
2. Check for front matter in post: `layout: home`
3. Look for CSS errors in browser DevTools (F12)
4. Rebuild: Commit small change, push to trigger rebuild

### Styling Broken

**Symptoms**: Page displays unstyled (plain text, no colors)

**Steps**:
1. Check CSS file is loading: DevTools → Network tab
2. Verify `baseurl` in `_config.yml` is correct
3. Check for CSS syntax errors: `assets/css/` files
4. Clear browser cache and reload
5. Test in different browser

## Security & Best Practices

### Secrets Management

**Never commit**:
- API keys or tokens
- Passwords
- Private credentials
- `.env` files

**If accidentally committed**:
1. Remove from file history: `git filter-branch`
2. Rotate all compromised credentials
3. Force push: `git push --force-with-lease`

### Access Control

- **Keep repositories public** (portfolio sites)
- **Use branch protection**: Require PR reviews for `main` branch
- **GitHub Settings** → Branches → Add rule for `main`

### Content Security

- **Review before publishing**: All content before live
- **Validate external links**: Test links in posts
- **Check images**: Verify image licenses/attributions

### Backup Strategy

**GitHub is your primary backup**:
- All commits stored in GitHub
- Can recover from any point in history

**Optional secondary backup**:
```bash
# Clone with full history
git clone --mirror git@github.com:pilakkat1964/blog.git blog-backup.git

# Create automated daily backup
# (via cron job or GitHub Actions)
```

## References

- [Jekyll Documentation](https://jekyllrb.com/docs/)
- [Chirpy Theme Docs](https://github.com/cotes2020/jekyll-theme-chirpy/wiki)
- [GitHub Pages Docs](https://docs.github.com/en/pages)
- [Markdown Guide](https://www.markdownguide.org/)

## Support & Issues

- **GitHub Issues**: Create issue in relevant repo
- **Email**: pilakkat1964@gmail.com
- **Documentation**: See SITE-DESIGN.md

## Last Updated

April 17, 2026
