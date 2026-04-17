# Site Development Guide — pilakkat.mywire.org

## Overview

This guide is for developers adding features, fixing bugs, or extending the pilakkat.mywire.org website. It covers the development environment setup, architecture details, testing, and deployment procedures.

## Development Environment

### Prerequisites

- **Git**: `git --version` should show v2.x or higher
- **Ruby**: 3.4.9+ (pinned versions per repo)
- **Bundler**: `gem install bundler`
- **mise** (optional): For managing tool versions across projects

### Tool Versions

| Repository | Ruby | Jekyll | Notes |
|-----------|------|--------|-------|
| `blog` | 3.4.9 | 4.x | See `mise.toml` |
| `pilakkat1964.github.io` | 3.x | 4.x | Auto-detected |
| `cv` | 3.x | 3.x | Uses auto-build |

### Using `mise` (Recommended)

Install `mise` from https://mise.jdx.dev

**For blog development** (tool versions auto-managed):
```bash
cd blog/
mise install  # Installs Ruby 3.4.9 (from mise.toml)
```

### Local Setup

#### 1. Clone Repositories

```bash
# Main site
git clone git@github.com:pilakkat1964/pilakkat1964.github.io.git
cd pilakkat1964.github.io
bundle install

# Blog
git clone git@github.com:pilakkat1964/blog.git
cd blog
bundle install

# CV (optional)
git clone git@github.com:pilakkat1964/cv.git
cd cv
bundle install
```

#### 2. Configure Git

```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

#### 3. Set Up SSH Keys (if not already done)

```bash
ssh-keygen -t ed25519 -C "your.email@example.com"
ssh-add ~/.ssh/id_ed25519
# Add public key to GitHub account: https://github.com/settings/keys
```

## Architecture

### Repository Structure

```
pilakkat1964.github.io/
├── .github/workflows/
│   └── pages-deploy.yml        # Build & deploy workflow
├── _config.yml                 # Site configuration
├── _includes/                  # Shared components
├── _layouts/                   # Page templates
├── _sass/                      # Style preprocessor
├── assets/
│   ├── css/
│   ├── js/
│   └── images/
├── _posts/ (if blog posts)     # Blog posts
├── index.md                    # Homepage
└── about.md                    # About page

blog/
├── .github/workflows/
│   └── pages-deploy.yml        # Build & deploy workflow
├── .gitmodules                 # Git submodules (Chirpy assets)
├── _config.yml                 # Blog configuration
├── _includes/                  # Shared includes
├── _layouts/
│   └── home.html               # Homepage layout (WITH HIERARCHY NAV)
├── _posts/                     # Blog posts
├── _tabs/                      # Static pages (About, etc)
├── assets/
│   ├── css/
│   ├── js/
│   ├── img/
│   └── lib/ (submodule)        # Chirpy theme assets
├── index.html                  # Blog homepage (uses home layout)
└── Gemfile                     # Dependencies
```

### Hierarchy Navigation Architecture

**Blog Homepage** (`/blog/`):

The navigation is implemented in `blog/_layouts/home.html`:

```html
---
layout: default
---

<!-- Navigation styling -->
<style>
  .hierarchy-nav {
    background: #f5f5f5;
    border-left: 4px solid #0366d6;
    border-bottom: 1px solid #ddd;
    padding: 12px 15px;
    margin: 0 -15px 20px -15px;
  }
  .hierarchy-nav a {
    color: #0366d6;
    text-decoration: none;
    font-size: 15px;
    font-weight: 600;
    transition: color 0.2s ease;
    display: inline-flex;
    align-items: center;
    gap: 6px;
  }
  .hierarchy-nav a:hover {
    color: #0256c7;
    text-decoration: underline;
  }
</style>

<!-- Navigation HTML -->
<div class="hierarchy-nav">
  <a href="/" title="Navigate to site home">
    ↑ Site Home
  </a>
</div>

<!-- Original Chirpy home layout content (post list, pagination, etc.) -->
<!-- ... -->
```

**Key points**:
- Navigation is in custom `_layouts/home.html` (overrides Chirpy default)
- Must include full Chirpy post-rendering logic (Liquid templating)
- Styling must match Chirpy color scheme
- Margins adjusted to align with Chirpy's content padding

**Why custom layout**:
- Chirpy's default `home.html` doesn't render `{{ content }}` from `index.html`
- Had to override to inject navigation while preserving post list rendering
- Alternative approached failed (JavaScript injection, CSS pseudo-elements)

### Build Pipeline

#### Blog Build Process

```
git push → GitHub Actions → Checkout + Install → Build → Deploy → Live
```

**Workflow file**: `.github/workflows/pages-deploy.yml`

**Key steps**:
1. Checkout with submodules: `submodules: true`
2. Install Ruby 3.4.9 via `ruby/setup-ruby@v1`
3. Install gems: `bundle install`
4. Clean cache: `rm -rf .jekyll-cache _site`
5. Build: `bundle exec jekyll build --baseurl /blog`
6. Upload to Pages: `actions/upload-pages-artifact@v4`
7. Deploy: `actions/deploy-pages@v4`

**Build time**: ~2 minutes

#### Main Site Build Process

Similar to blog, but:
- No git submodules
- Different theme (minima)
- `--baseurl` is empty (serves at root `/`)

## Development Workflow

### Creating a Feature Branch

```bash
git checkout -b feature/description-of-change
```

### Testing Locally

#### Blog

```bash
cd blog/

# With mise (automatic Ruby version)
bundle exec jekyll serve --baseurl /blog

# Or explicitly (without mise)
ruby 3.4.9
bundle exec jekyll serve --baseurl /blog
```

**Access**: `http://localhost:4000/blog/`

#### Main Site

```bash
cd pilakkat1964.github.io/
bundle exec jekyll serve
```

**Access**: `http://localhost:4000/`

#### CV

```bash
cd cv/
bundle exec jekyll serve --baseurl /cv
```

**Access**: `http://localhost:4000/cv/`

### Making Changes

#### Adding a Blog Post

```bash
cd blog/
cat > _posts/2026-04-17-my-post.md <<'EOF'
---
title: "My Post Title"
date: 2026-04-17 10:00:00 +0800
categories: [Category]
tags: [tag1, tag2]
---

# Post content

Content goes here...
EOF
```

**Test locally**: Refresh `http://localhost:4000/blog/` to see new post

#### Modifying Navigation

1. Edit `blog/_layouts/home.html`:
   - Change link URL
   - Update styling
   - Adjust margins/spacing

2. **Test locally**:
   ```bash
   # Kill running server
   # Re-run: bundle exec jekyll serve --baseurl /blog
   ```
   - Reload `http://localhost:4000/blog/`
   - Check navigation link

3. **Verify post list still works**: Scroll down to see blog posts

4. **Test responsiveness**: Use browser DevTools (F12) → toggle device toolbar

#### Adding Navigation to New Page

1. Create page template in `_layouts/custom.html`:
   ```html
   ---
   layout: default
   ---

   <div class="hierarchy-nav">
     <a href="/parent-url/">↑ Up to Parent</a>
   </div>

   {{ content }}
   ```

2. Use in page front matter:
   ```yaml
   ---
   layout: custom
   title: Page Title
   ---
   ```

3. Test locally

### Styling Changes

#### Blog (Chirpy)

**Theme colors**: Primary theme colors in Chirpy are in:
- `assets/css/jekyll-theme-chirpy.css` (minified)
- Or check Chirpy source: https://github.com/cotes2020/jekyll-theme-chirpy

**Adding custom styles**:
1. Create `assets/css/custom.css`
2. Include in `_config.yml`:
   ```yaml
   sass:
     load_paths:
       - assets/css
   ```
3. Or override in `_layouts/home.html` `<style>` section (quick changes)

**Colors used**:
- Primary: `#0366d6` (Chirpy blue)
- Hover: `#0256c7` (darker blue)
- Background: `#f5f5f5` (light gray)
- Border: `#ddd` (light gray)

#### Main Site (minima)

**Theme colors**: See `_sass/minima/` directory

**Custom styles**: Create or edit `assets/css/style.scss`

### Testing Locally

#### Visual Testing

1. **Desktop**: Regular browser window
2. **Tablet**: DevTools → Responsive Design Mode → Tablet size
3. **Mobile**: DevTools → Responsive Design Mode → Mobile size

#### Functionality Testing

- [ ] All links work
- [ ] CSS loads (no unstyled page)
- [ ] Images load
- [ ] Navigation works
- [ ] Responsive layout adjusts
- [ ] Search works (if applicable)
- [ ] Forms submit (if applicable)

#### Performance Testing

```bash
# Check build time
time bundle exec jekyll build --baseurl /blog

# Check generated site size
du -sh blog/_site/

# Check asset sizes
ls -lh blog/_site/assets/css/
ls -lh blog/_site/assets/js/
```

### Browser DevTools Tips

**Open DevTools**: F12 or Ctrl+Shift+I

**Useful tabs**:
- **Elements**: Inspect HTML structure
- **Console**: See JavaScript errors
- **Network**: Check resource loading
- **Application**: Clear cache/cookies

**Responsive Design Mode**: Ctrl+Shift+M

## Testing

### Unit Testing

Not typically used in Jekyll sites, but if adding custom plugins:

```bash
# Create test file: lib/filters_test.rb
# Run: bundle exec ruby lib/filters_test.rb
```

### Integration Testing

**Manual testing** is standard for Jekyll sites:

1. **Build locally**: Ensure no build errors
2. **Visual inspection**: Check rendered HTML
3. **Cross-browser**: Test in Chrome, Firefox, Safari
4. **Cross-device**: Test on mobile, tablet, desktop
5. **Performance**: Check PageSpeed Insights

### Automated Testing (GitHub Actions)

Currently no automated tests, but can add:

```yaml
# In .github/workflows/test.yml
- name: Check Links
  run: bundle exec htmlproofer ./_site
```

### Manual Testing Checklist

- [ ] No build errors
- [ ] All pages load
- [ ] Navigation links work
- [ ] External links are valid
- [ ] Images display
- [ ] CSS/JS load correctly
- [ ] Mobile responsive
- [ ] Dark mode works (if applicable)
- [ ] Search works (blog)
- [ ] Categories/Tags work (blog)
- [ ] No console errors (DevTools)
- [ ] Page loads in <3s (good performance)

## Committing & Pushing

### Commit Message Format

```
type: short description

Detailed explanation of changes (if needed).

- Bullet points for specific changes
- Another change
```

**Types**:
- `feat:` New feature
- `fix:` Bug fix
- `style:` Styling/CSS changes
- `refactor:` Code restructuring
- `docs:` Documentation
- `chore:` Maintenance/config changes

**Examples**:
```
feat: add navigation to blog homepage

- Implement hierarchy navigation with "↑ Site Home" link
- Add styling to match Chirpy theme colors
- Preserve full post list functionality

fix: correct navigation link color on hover

docs: update site development guide
```

### Staging Changes

```bash
# See what changed
git status

# Stage specific file
git add path/to/file.md

# Stage all changes
git add -A

# Review staged changes
git diff --cached
```

### Committing

```bash
# Create commit
git commit -m "type: description"

# Or interactive commit
git commit

# Fix last commit
git commit --amend
```

### Pushing

```bash
# Push to origin main
git push origin main

# Push to feature branch
git push origin feature/description

# Force push (use with caution!)
git push --force-with-lease origin main
```

## Code Review & Pull Requests

### Creating a Pull Request

1. **Push feature branch**: `git push origin feature/name`
2. **Go to GitHub**: https://github.com/pilakkat1964/blog
3. **Click "New Pull Request"**
4. **Select** `main` as base branch
5. **Add description**: What changes? Why? How to test?
6. **Create PR**
7. **Monitor GitHub Actions**: Ensure build succeeds

### Code Review Best Practices

- **Review own code first**: Before requesting review
- **Test locally**: Verify changes work
- **Keep PRs small**: Easier to review
- **Clear descriptions**: Explain the change
- **Request specific reviewers**: If multiple maintainers

### Merging

**Once approved**:
1. GitHub Actions workflow must pass (green check)
2. Reviewer approves PR
3. Click "Merge pull request"
4. Delete feature branch
5. Verify live site updates in 2-5 minutes

## Deployment

### Automatic Deployment

**Workflow**:
1. Commit code to `main` branch
2. Push to GitHub: `git push origin main`
3. GitHub Actions triggers automatically
4. Build completes (2-5 minutes)
5. Site updates at: `https://pilakkat.mywire.org/blog/`

**No manual deployment needed** — fully automated!

### Monitoring Deployment

**In GitHub UI**:
1. Go to repo → "Actions" tab
2. See workflow run status
3. Click run to see logs
4. Green checkmark = success, red X = failure

**Workflow logs show**:
- Build output
- Dependency versions
- Build time
- Any errors

### Rollback (If Needed)

**Revert last commit**:
```bash
git revert HEAD
git push origin main
```

**Revert to specific commit**:
```bash
git revert [commit-hash]
git push origin main
```

**Force revert** (use with caution):
```bash
git reset --hard [commit-hash]
git push --force-with-lease origin main
```

## Troubleshooting

### Build Fails Locally

**Problem**: `bundle exec jekyll build` fails

**Solutions**:
1. **Clear cache**: `rm -rf .jekyll-cache _site`
2. **Reinstall gems**: `bundle install`
3. **Check Ruby version**: `ruby --version` matches Gemfile
4. **Check for syntax errors**: In markdown files or config
5. **Review error message**: Usually very descriptive

### Local Server Doesn't Reload

**Problem**: Changes don't appear when page reloads

**Solutions**:
1. **Stop server**: Ctrl+C
2. **Clear cache**: `rm -rf .jekyll-cache _site`
3. **Restart server**: `bundle exec jekyll serve --baseurl /blog`
4. **Clear browser cache**: Ctrl+Shift+Delete
5. **Try different browser**: Chrome, Firefox, etc.

### GitHub Actions Fails

**Problem**: Workflow run shows red X

**Steps**:
1. Click failed workflow run
2. Expand "Build site" step
3. Read error message (usually clear)
4. Common errors:
   - Syntax error in front matter: Fix YAML
   - Missing gem: Update Gemfile.lock
   - Path error: Check baseurl, urls
5. Fix, commit, push to retry

### Navigation Not Showing

**Problem**: `↑ Site Home` link missing from blog

**Steps**:
1. Check `blog/_layouts/home.html` exists
2. Verify front matter: `layout: home`
3. Check for HTML errors in DevTools (F12)
4. Rebuild: `rm -rf .jekyll-cache && bundle exec jekyll build --baseurl /blog`
5. Check live site after push (GitHub Actions rebuild)

### Git Merge Conflicts

**Problem**: Can't merge due to conflicts

**Resolution**:
1. Pull latest: `git pull origin main`
2. Resolve conflicts in editor (see `<<<<<<<` markers)
3. Stage resolved files: `git add .`
4. Commit: `git commit -m "resolve conflicts"`
5. Push: `git push origin [branch-name]`

## Performance Optimization

### Jekyll Build Performance

**Measure**:
```bash
time bundle exec jekyll build --baseurl /blog
```

**Optimize**:
- **Disable unused plugins**: Comment out in Gemfile
- **Limit posts in dev**: Use `--future` flag only when needed
- **Clear cache**: `rm -rf .jekyll-cache`

### Asset Optimization

**Images**:
- Compress before adding to repo
- Use `image: { path: url, lqip: placeholder }`
- Consider lazy-loading for many images

**CSS/JS**:
- Minify production builds (Chirpy does this)
- Remove unused CSS
- Lazy-load non-critical JS

### Content Delivery

**GitHub Pages CDN**:
- Automatically cached at edge locations
- Clear cache via `PURGE` request (if needed)
- No configuration needed

## References

- [Jekyll Official Docs](https://jekyllrb.com/docs/)
- [Chirpy Theme GitHub](https://github.com/cotes2020/jekyll-theme-chirpy)
- [GitHub Pages Docs](https://docs.github.com/en/pages)
- [Jekyll Liquid Templating](https://shopify.github.io/liquid/)
- [YAML Syntax](https://yaml.org/spec/1.2/spec.html)
- [Markdown Syntax](https://www.markdownguide.org/basic-syntax/)

## Support

- **Issues**: Create GitHub issue in repo
- **Discussions**: GitHub Discussions (if enabled)
- **Email**: pilakkat1964@gmail.com

## Last Updated

April 17, 2026
