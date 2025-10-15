---
layout: default
title: Tropical Updates
permalink: /tropical-updates/
---

{% assign posts_sorted = site.posts | sort: "date" | reverse %}

<div class="posts-grid">
  {% for post in posts_sorted %}
    <article class="card card--tight">
      <a class="card__link" href="{{ post.url | relative_url }}">
        <h3 class="card__title card__title--center">{{ post.title }}</h3>

        {% if post.thumb %}
          <img class="card__thumb card__thumb--small"
               src="{{ post.thumb | relative_url }}"
               alt="{{ post.thumb_alt | default: post.title }}">
        {% endif %}

        <span class="card__cta">Read more →</span>
      </a>
    </article>
  {% endfor %}
</div>
