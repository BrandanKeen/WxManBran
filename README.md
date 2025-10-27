# WxManBran.com

A lightweight Jekyll site for tropical weather storytelling. Everything is designed so you can edit Markdown directly on GitHub and let GitHub Pages publish automatically.

## Quick Start

1. Edit files from the GitHub interface (no local Ruby setup required).
2. Commit changes to `main`. GitHub Actions will build the site and deploy `_site`.
3. Visit <https://brandankeen.github.io/> (or your custom domain) to verify.

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
4. Write the update in Markdown. Include images by uploading them to `tabs/tropical-updates/media/<year>/updates/` and linking with `{{ '/tabs/tropical-updates/media/<year>/updates/<file>' | relative_url }}`.
5. Commit the file—your post appears automatically on the **Tropical Updates** page.

## Add a New Storm Page (5 Steps)

1. Open the `tabs/previous-storms/_storms` folder and create `YYYY-storm-name.md`.
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
3. Add headings for **At a Glance**, **Timeline**, and **Graphics & Media**. Drop images, GIFs, or reports into `tabs/previous-storms/media/<season>/<storm>/`. 
4. Reference media with `![Alt text]({{ '/tabs/previous-storms/media/<season>/<storm>/file.png' | relative_url }})` so links work on any domain.
5. Commit. The storm will be grouped automatically under the correct season on **Previous Storms**.

## Collections & Structure

- `_posts/` — blog-style updates shown on **Tropical Updates**.
- `tabs/` — navigation-aligned folders (`home`, `tropical-updates`, `data`, `previous-storms`, `learn`, `about`) containing each tab's pages, assets, and previews.
- `tabs/previous-storms/_storms/` — collection configured in `_config.yml` with `output: true` for individual storm pages.
- `_data/nav.yml` — controls the top navigation tabs.

## Plugins

The site uses GitHub Pages default plugins (`jekyll-feed` and `jekyll-sitemap`) for syndication and search indexing. No extra setup needed.

## Testing & Visualizing Changes

### Local preview

1. Install Ruby (>= 3.1) and Bundler.
2. Install dependencies:

   ```bash
   bundle install
   ```

3. Start the live preview server:

   ```bash
   bundle exec jekyll serve --livereload --host 0.0.0.0 --port 4000
   ```

   Visit <http://localhost:4000> to confirm your updates before committing. The `--livereload` flag automatically refreshes the browser as you edit.

### Continuous integration check

Every pull request automatically runs `.github/workflows/jekyll-ci.yml`, which installs the Gem bundle and executes:

```bash
bundle exec jekyll build
```

This mirrors the production Pages build, so you’ll know a change is safe to merge as soon as CI passes.

