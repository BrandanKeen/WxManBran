---
layout: default
title: Tropical Updates
permalink: /tropical-updates/
---

<div class="posts-grid">
  {% for post in site.posts %}
    <article class="card">
      <a class="card__link" href="{{ post.url | relative_url }}">
        <time class="card__date">
          {{ post.date | date: "%B %d, %Y" }} ·
          {% if post.display_time %}{{ post.display_time }}{% else %}{{ post.date | date: "%-I %p" }}{% endif %} ET
        </time>
        <h3 class="card__title">{{ post.title }}</h3>
        <p class="card__summary">
          {{ post.summary | default: post.excerpt | strip_html | truncate: 160 }}
        </p>
        <span class="card__cta">Read more →</span>
      </a>
    </article>
  {% endfor %}
</div>
