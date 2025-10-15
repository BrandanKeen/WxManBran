---
layout: default
title: Tropical Updates
permalink: /tropical-updates/
---

{% assign posts_sorted = site.posts | sort: "date" | reverse %}

<div class="posts-grid">
  {% for post in posts_sorted %}
    <article class="card">
      <a class="card__link" href="{{ post.url | relative_url }}">
        {% if post.thumb %}
          <img class="card__thumb" src="{{ post.thumb | relative_url }}" alt="{{ post.thumb_alt | default: post.title }}">
        {% endif %}
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
