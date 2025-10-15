# WxManBran.com

A lightweight Jekyll site for tropical weather storytelling. Everything is designed so you can edit Markdown directly on GitHub and let GitHub Pages publish automatically.

## Quick Start

1. Edit files from the GitHub interface (no local Ruby setup required).
2. Commit changes to `main`. GitHub Actions will build the site and deploy `_site`.
3. Visit <https://brandankeen.github.io/WxManBran/> (or your custom domain) to verify.

## Add a New Tropical Update (5 Steps)

1. In GitHub, open the `_posts` folder and click **Add file → Create new file**.
2. Name the file `YYYY-MM-DD-your-title.md` using the publish date.
3. Paste this front matter at the top:
   ```yaml
   ---
   layout: default
   title: Your Headline
   ---
   ```
4. Write the update in Markdown. Include images by uploading them to `assets/<year>/updates/` and linking with `{{ '/assets/<path>' | relative_url }}`.
5. Commit the file—your post appears automatically on the **Tropical Updates** page.

## Add a New Storm Page (5 Steps)

1. Open the `_storms` folder and create `YYYY-storm-name.md`.
2. Use this starter front matter:
   ```yaml
   ---
   layout: default
   title: Storm Name
   season: 2025
   landfall: Month Day, Year — Location
   permalink: /storms/storm-name-2025/
   ---
   ```
3. Add headings for **At a Glance**, **Timeline**, and **Graphics & Media**. Drop images or GIFs into `assets/<season>/<storm>/`.
4. Reference media with `![Alt text]({{ '/assets/<season>/<storm>/file.png' | relative_url }})` so links work on any domain.
5. Commit. The storm will be grouped automatically under the correct season on **Previous Storms**.

## Collections & Structure

- `_posts/` — blog-style updates shown on **Tropical Updates**.
- `_storms/` — collection configured in `_config.yml` with `output: true` for individual storm pages.
- `_data/nav.yml` — controls the top navigation tabs.
- `assets/` — store static files in sub-folders by year or feature.

## Plugins

The site uses GitHub Pages default plugins (`jekyll-feed` and `jekyll-sitemap`) for syndication and search indexing. No extra setup needed.

## Local Preview (Optional)

If you want to preview locally, install Ruby and run:

```bash
bundle exec jekyll serve
```

But this is optional—GitHub’s editor and preview tabs are usually all you need.
