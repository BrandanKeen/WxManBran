---
layout: default
title: Tropical Updates
permalink: /tropical-updates/
---

{%- assign posts_sorted = site.posts | sort: "date" | reverse -%}

<div class="posts-grid posts-grid--fit">
  {%- for post in posts_sorted -%}
    <article class="card card--tight card--center card--fit">
      <a class="card__link" href="{{ post.url | relative_url }}">

        <time class="card__date card__date--big" datetime="{{ post.date | date_to_xmlschema }}">
          {{ post.date | date: "%B %d, %Y %-I %p" }} ET
        </time>

        <h3 class="card__title card__title--big">{{ post.title }}</h3>

        {% if post.thumb %}
          <img class="card__thumb card__thumb--large"
               src="{{ post.thumb | relative_url }}"
               alt="{{ post.thumb_alt | default: post.title }}">
        {% endif %}

        <span class="card__cta">Read more →</span>
      </a>
    </article>
  {%- endfor -%}
</div>
