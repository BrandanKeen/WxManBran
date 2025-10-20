---
layout: default
title: Tropical Updates
permalink: /tropical-updates/
---

{%- assign posts_sorted = site.posts | sort: "date" | reverse -%}

<div class="section-intro">
  <h1>Tropical Updates</h1>
  <p>Stay tuned for the latest tropical weather discussions, video briefings, and detailed intercept plans as they become available.</p>
</div>

<div class="posts-grid posts-grid--fit">
  {%- for post in posts_sorted -%}

    {%- if post.youtube_id -%}
      <div class="post-pair">
        <!-- Left: existing Blog Post card -->
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

        <!-- Right: Brief card -->
<article class="post-card">
  <header class="post-card__header">
    <time class="post-date" datetime="{{ post.date | date_to_xmlschema }}">
      {{ post.date | date: "%B %d, %Y %-I %p" }} ET
    </time>
    <h2 class="post-title">
      <a class="link-chip" href="https://www.youtube.com/watch?v={{ post.youtube_id }}" target="_blank" rel="noopener">
        {{ post.video_title | default: post.title | append: ": Brief" }}
      </a>
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
          <div class="post-card__share">
            <span class="post-card__share-label">Share:</span>
            <a class="link-chip" href="https://www.facebook.com/sharer/sharer.php?u=https://youtu.be/{{ post.youtube_id }}" target="_blank" rel="noopener">Facebook</a>
            <a class="link-chip" href="https://twitter.com/intent/tweet?url=https://youtu.be/{{ post.youtube_id }}" target="_blank" rel="noopener">X (Twitter)</a>
            <a class="link-chip" href="mailto:?subject={{ post.video_title | default: post.title | append: ' Brief' | uri_escape }}&body={{ 'Check out this tropical weather brief: https://youtu.be/' | append: post.youtube_id | uri_escape }}">Email</a>
          </div>
        </article>
      </div>
    {%- else -%}
      <!-- No youtube_id: render the single Blog card -->
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
    {%- endif -%}

  {%- endfor -%}
</div>
