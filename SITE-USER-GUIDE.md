# Site User Guide — pilakkat.mywire.org

## Overview

This guide explains how to navigate and use the **pilakkat.mywire.org** website, which combines three Jekyll-based sites under one domain:
- **Main Portfolio** (root `/`)
- **Tech Blog** (`/blog/`)
- **CV** (`/cv/`)

## Navigation Architecture

### Site Hierarchy

The website implements a **hierarchical navigation system** to help users understand where they are and move between different sections:

```
pilakkat.mywire.org (Root - Main Portfolio)
├── /blog/ (Tech Blog)
└── /cv/ (CV/Resume)
```

### Navigation Links

Each section displays context-aware navigation at the top of the page:

#### Main Portfolio (`/`)
- **No "up" navigation** — this is the top level
- Contains links to: Blog, CV, About, and social media

#### Blog (`/blog/`)
- **Shows**: `↑ Site Home` link
- **Color**: Chirpy theme blue (`#0366d6`)
- **Location**: Top of main content area, above the post list
- **Function**: Click to return to the main portfolio home

#### CV (`/cv/`)
- Navigation styling varies by theme
- Consistent placement at the top of the page

### Visual Design

All navigation links follow a consistent design pattern:

- **Color**: Theme-specific blue (`#0366d6` for Chirpy, `#0275d8` for others)
- **Font Weight**: Bold (600-700)
- **Border**: Left border (4px solid, colored)
- **Background**: Light gray (`#f5f5f5`)
- **Hover Effect**: Color darkens and underline appears
- **Icon**: Up arrow (`↑`) indicates parent/up navigation

Example styling (Chirpy blog):
```css
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
```

## Site Sections

### Main Portfolio (`https://pilakkat.mywire.org/`)

**Theme**: minima (dark skin)

**Content**:
- Portfolio home
- About page
- Links to blog and CV
- RSS feed

**Navigation**:
- Top navigation bar with links to Blog, CV, About
- Footer with social media links

**URL**: `https://pilakkat.mywire.org/`

### Tech Blog (`https://pilakkat.mywire.org/blog/`)

**Theme**: Chirpy (modern, responsive)

**Content**:
- Blog posts about technology topics (5G, SDR, IIoT, FPGA, Embedded Systems, Rust, Linux kernel, etc.)
- Categories and tags for organizing posts
- Search functionality
- Recently updated posts widget
- Trending tags widget

**Navigation**:
- **Top navigation**: `↑ Site Home` (returns to portfolio)
- **Sidebar navigation**: HOME, CATEGORIES, TAGS, ARCHIVES, ABOUT
- **Search bar**: Top right corner
- **Social media links**: Sidebar footer (GitHub, LinkedIn, Email, RSS)

**Features**:
- **Responsive design**: Adapts to mobile, tablet, and desktop
- **Dark/Light mode toggle**: Top right corner
- **Post metadata**: Author, date, categories, read time
- **Post sharing**: Via social media (if enabled)
- **Comments**: If enabled per post

**URL**: `https://pilakkat.mywire.org/blog/`

**Recent Posts**: View the latest posts on the homepage

**Browse by Category**: Click "CATEGORIES" in sidebar

**Browse by Tag**: Click "TAGS" in sidebar

**Archive**: Click "ARCHIVES" to see posts by date

### CV (`https://pilakkat.mywire.org/cv/`)

**Theme**: online-cv

**Content**:
- Resume/CV
- Work experience
- Skills
- Education
- Print-friendly format

**URL**: `https://pilakkat.mywire.org/cv/`

**Print**: Use browser print function or click "Print" button

## Accessing Content

### Finding Blog Posts

1. **From Portfolio**: Click "Blog" link in main navigation
2. **From Blog Homepage**: Posts are listed chronologically on the homepage
3. **By Category**: Click "CATEGORIES" → select a category
4. **By Tag**: Click "TAGS" → select a tag
5. **By Date**: Click "ARCHIVES" → select year/month

### Searching

- **Blog Search**: Use the search box in the top right corner of the blog
- **Type**: Partial post titles or keywords
- **Results**: Displayed below the search box with post titles, dates, and snippets

### Social Media

Links to social media profiles:
- GitHub: `https://github.com/pilakkat1964`
- LinkedIn: `https://linkedin.com/in/pilakkat`
- Email: Click the email icon to compose a message

### RSS Feed

Subscribe to blog updates:
- **Feed URL**: `https://pilakkat.mywire.org/blog/feed.xml`
- **Use**: Add to your RSS reader (Feedly, Inoreader, etc.)

## Mobile Experience

All sites are fully responsive:
- **Mobile**: Single-column layout
- **Tablet**: Two-column layout (when applicable)
- **Desktop**: Multi-column layout with sidebars

### Mobile Navigation

- **Hamburger menu**: Three-line icon (☰) on top left opens/closes sidebar
- **Search icon**: Magnifying glass opens search on mobile
- **Back button**: Browser back button or navigation links

## Keyboard Navigation

- **Tab**: Move between links
- **Enter**: Activate links and buttons
- **Esc**: Close search/modals (where applicable)

## Accessibility

- **Dark Mode**: Available on all sites for users who prefer reduced eye strain
- **High Contrast**: Navigation links use high-contrast colors
- **Screen Readers**: All content is properly marked up with semantic HTML
- **Keyboard Navigation**: All interactive elements are keyboard accessible

## Troubleshooting

### Page Not Loading

1. **Clear browser cache**: Ctrl+Shift+Delete (Windows) or Cmd+Shift+Delete (Mac)
2. **Try a different browser**: Chrome, Firefox, Safari, Edge
3. **Check internet connection**: Ensure you have active internet

### Navigation Links Not Working

1. **Verify URL**: Check if you're on the correct domain (`pilakkat.mywire.org`)
2. **Clear cookies**: Clear site data and try again
3. **Try direct URL**: Type the URL directly in address bar

### Blog Posts Not Showing

1. **Refresh page**: Press F5 or Cmd+R
2. **Wait for load**: Blog uses JavaScript to load posts - may take a few seconds on slow connections
3. **Check browser console**: Open Developer Tools (F12) and check Console tab for errors

### Images Not Loading

1. **Check connection**: Ensure images are loading (may be slow on mobile networks)
2. **Verify ad blocker**: Disable ad blockers/privacy extensions
3. **Clear cache**: Clear browser cache and reload

## Contact

For questions, issues, or feedback:
- **Email**: pilakkat1964@gmail.com
- **GitHub Issues**: https://github.com/pilakkat1964/pilakkat1964.github.io/issues
- **LinkedIn**: https://linkedin.com/in/pilakkat

## Last Updated

April 17, 2026
