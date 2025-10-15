---
layout: default
title: Tropical Updates
permalink: /tropical-updates/
---

{%- assign posts_sorted = site.posts | sort: "date" | reverse -%}

<div class="posts-grid">
  {%- for post in posts_sorted -%}
    <article class="card card--tight card--center">
      <a class="card__link" href="{{ post.url | relative_url }}">

        <h3 class="card__title">{{ post.title }}</h3>

        <!-- one “blank line” gap -->
        <div class="card__gap" aria-hidden="true"></div>

        <time class="card__date" datetime="{{ post.date | date_to_xmlschema }}">
          {{ post.date | date: "%B %d, %Y %-I %p" }} ET
        </time>

        {%- if post.thumb -%}
          <img class="card__thumb card__thumb--small"
               src="{{ post.thumb | relative_url }}"
               alt="{{ post.thumb_alt | default: post.title }}">
        {%- endif -%}

        <span class="card__cta">Read more →</span>
      </a>
    </article>
  {%- endfor -%}
</div>
