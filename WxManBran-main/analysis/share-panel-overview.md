# Share panel placement

The social share panel for Tropical Update posts is rendered by the default layout after the main post content. When a page belongs to the built-in `posts` collection, `_layouts/default.html` includes the `_includes/share-buttons.html` partial immediately before the footer.

```liquid
<main id="content" class="site-content">
  {{ content }}
  {% if page.collection == 'posts' %}
    {% include share-buttons.html %}
  {% endif %}
</main>
```

The include outputs the Facebook, X, email, SMS, and copy-link controls in the `.share-panel` wrapper, and the component styles live in `assets/css/site.css` alongside the rest of the site design tokens.
