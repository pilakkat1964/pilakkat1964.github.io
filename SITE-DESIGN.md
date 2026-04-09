# Site Design — pilakkat.mywire.org

## Overview

Three GitHub repositories combine to serve the personal website of **Santhosh Kumar Pilakkat** at `https://pilakkat.mywire.org`.

## DNS Configuration

| Record | Type | Value |
|--------|------|-------|
| `pilakkat.mywire.org` | CNAME | `pilakkat1964.github.io` |

Only **one** CNAME record is needed. The `/blog` and `/cv` paths are served by separate GitHub project repos automatically under the same custom domain.

## Repositories

| Repo | URL Path | Theme | Deploy Method |
|------|----------|-------|---------------|
| [pilakkat1964/pilakkat1964.github.io](https://github.com/pilakkat1964/pilakkat1964.github.io) | `/` | minima (dark) | GH Actions → deploy-pages |
| [pilakkat1964/blog](https://github.com/pilakkat1964/blog) | `/blog/` | Chirpy | GH Actions → deploy-pages |
| [pilakkat1964/cv](https://github.com/pilakkat1964/cv) | `/cv/` | online-cv | GH Pages (branch) |

## Site Structure

```
pilakkat.mywire.org/
├── /                  → pilakkat1964.github.io repo (minima theme)
│   ├── /about/        → About page
│   └── /feed.xml      → RSS feed
├── /blog/             → blog repo (Chirpy theme)
│   ├── /blog/posts/   → Blog posts (markdown in _posts/)
│   ├── /blog/tags/    → Tag archive
│   └── /blog/categories/ → Category archive
└── /cv/               → cv repo (online-cv theme)
    └── /cv/print.html → Print-friendly CV
```

## Repository Details

### Main Site (`pilakkat1964.github.io`)
- **Theme**: minima 2.5 (dark skin)
- **`_config.yml` key settings**:
  - `url: "https://pilakkat.mywire.org"`
  - `baseurl: ""`
- **CNAME**: `pilakkat.mywire.org` (this is the root — CNAME lives here)
- **Deploy**: GitHub Actions workflow on push to `main`

### Blog (`pilakkat1964/blog`)
- **Theme**: [jekyll-theme-chirpy](https://github.com/cotes2020/jekyll-theme-chirpy)
- **`_config.yml` key settings**:
  - `url: "https://pilakkat.mywire.org"`
  - `baseurl: "/blog"`
- **No CNAME file** — served as a project page under the main domain
- **Deploy**: GitHub Actions (`pages-deploy.yml`) on push to `main`
- **Local dev**: Uses `mise` to pin Ruby 3.4.9

### CV (`pilakkat1964/cv`)
- **Theme**: [online-cv](https://github.com/sharu725/online-cv)
- **`_config.yml` key settings**:
  - `url: "https://pilakkat.mywire.org"`
  - `baseurl: "/cv"`
- **No CNAME file** — served as a project page under the main domain
- **Deploy**: GitHub Pages built-in (from `master` branch, Jekyll auto-build)

## Local Development

### Blog
```bash
cd blog/
bundle install
bundle exec jekyll serve --baseurl /blog
```

### CV
```bash
cd cv/
bundle install
bundle exec jekyll serve --baseurl /cv
```

### Main Site
```bash
cd pilakkat1964.github.io/
bundle install
bundle exec jekyll serve
```

## mise.toml (Blog)

The `blog/` repo contains a `mise.toml` that pins tool versions for local development:

```toml
[tools]
neovim = "latest"
ruby = "3.4.9"
```

`mise` (https://mise.jdx.dev) is a polyglot runtime manager similar to `asdf`. It **only affects local development** — GitHub Actions uses `ruby/setup-ruby@v1` independently and is not affected by `mise.toml`. Safe to keep.

## Adding Blog Posts

Create files in `blog/_posts/` with format `YYYY-MM-DD-title.md`:

```markdown
---
title: "My Post Title"
date: 2026-04-09 00:00:00 +0800
categories: [5G, SDR]
tags: [wifi, xtensa]
---

Post content here.
```
