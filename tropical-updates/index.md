---
layout: default
title: Tropical Updates
permalink: /tropical-updates/
---

{%- assign posts_sorted = site.posts | sort: "date" | reverse -%}

<div class="posts-grid posts-grid--fit">
  {%- for post in posts_sorted -%}
    <article class="post-card">
      <header>
        <time class="post-card__date" datetime="{{ post.date | date_to_xmlschema }}">
          {{ post.date | date: "%B %d, %Y %-I %p" }} ET
        </time>

        <h2 class="post-title">
          <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
        </h2>
      </header>

      {% if post.thumb %}
        <a class="post-card__thumb-link" href="{{ post.url | relative_url }}">
          <img class="post-card__thumb"
               src="{{ post.thumb | relative_url }}"
               alt="{{ post.thumb_alt | default: post.title }}">
        </a>
      {% endif %}

      <p class="read-more-wrap">
        <a class="read-more" href="{{ post.url | relative_url }}">Read more →</a>
      </p>
    </article>
  {%- endfor -%}
</div>
