---
layout: default
title: Tropical Updates
permalink: /tropical-updates/
---

{%- assign posts_sorted = site.posts | sort: "date" | reverse -%}

<div class="posts-grid posts-grid--fit">
  {%- for post in posts_sorted -%}
    <div class="post-pair">
      <!-- Left: existing Blog Post card (unchanged structure) -->
      <article class="post-card">
        <header class="post-card__header">
          <time class="post-date" datetime="{{ post.date | date_to_xmlschema }}">
            {{ post.date | date: "%B %d, %Y %-I %p" }} ET
          </time>

          <h2 class="post-title">
            <a class="link-chip" href="{{ post.url | relative_url }}">{{ post.title }}</a>
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
          <a class="read-more link-chip" href="{{ post.url | relative_url }}">Read more →</a>
        </p>
      </article>

      <!-- Right: Video Discussion card (only if youtube_id exists) -->
      {% if post.youtube_id %}
      <article class="post-card">
        <header class="post-card__header">
          <time class="post-date" datetime="{{ post.date | date_to_xmlschema }}">
            {{ post.date | date: "%B %d, %Y %-I %p" }} ET
          </time>

          <h2 class="post-title">
            <span class="link-chip">{{ post.title }}: Video Discussion</span>
          </h2>
        </header>

        <div class="post-card__video">
          <iframe
            src="https://www.youtube-nocookie.com/embed/{{ post.youtube_id }}?rel=0&modestbranding=1"
            title="{{ post.title }} video discussion"
            loading="lazy"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
            allowfullscreen></iframe>
        </div>
      </article>
      {% endif %}
    </div>
  {%- endfor -%}
</div>
