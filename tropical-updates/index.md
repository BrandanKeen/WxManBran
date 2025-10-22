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

<script>
  document.addEventListener('DOMContentLoaded', function () {
    var shareDetails = document.querySelectorAll('.post-card__share');
    document.addEventListener('click', function (event) {
      shareDetails.forEach(function (details) {
        if (details.hasAttribute('open') && !details.contains(event.target)) {
          details.removeAttribute('open');
        }
      });
    });

    var copyButtons = document.querySelectorAll('.js-copy-link');
    copyButtons.forEach(function (button) {
      button.addEventListener('click', function () {
        var link = button.getAttribute('data-copy');
        if (!link) {
          return;
        }

        var resetText = function () {
          button.querySelector('.share-link__label').textContent = 'Copy link';
        };

        var setCopied = function () {
          button.querySelector('.share-link__label').textContent = 'Copied!';
          setTimeout(resetText, 2400);
        };

        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(link).then(setCopied).catch(function () {
            fallbackCopy();
          });
          return;
        }

        function fallbackCopy() {
          var tempInput = document.createElement('textarea');
          tempInput.value = link;
          tempInput.setAttribute('readonly', '');
          tempInput.style.position = 'absolute';
          tempInput.style.left = '-9999px';
          document.body.appendChild(tempInput);
          tempInput.select();
          try {
            document.execCommand('copy');
            setCopied();
          } catch (err) {
            resetText();
          }
          document.body.removeChild(tempInput);
        }

        fallbackCopy();
      });
    });
  });
</script>

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
          <details class="post-card__share read-more-wrap">
            <summary class="read-more link-chip">Share</summary>
            <div class="post-card__share-panel">
              <a class="share-link link-chip" href="https://www.facebook.com/sharer/sharer.php?u=https://youtu.be/{{ post.youtube_id }}" target="_blank" rel="noopener">
                <svg class="share-link__icon" aria-hidden="true" focusable="false" viewBox="0 0 24 24">
                  <path d="M22.675 0H1.326C.595 0 0 .595 0 1.326v21.348C0 23.405.595 24 1.326 24h11.495v-9.294H9.69v-3.622h3.13V8.413c0-3.1 1.894-4.788 4.659-4.788 1.325 0 2.463.099 2.793.143v3.24l-1.918.001c-1.504 0-1.796.715-1.796 1.763v2.312h3.587l-.467 3.622h-3.12V24h6.116C23.405 24 24 23.405 24 22.674V1.326C24 .595 23.405 0 22.675 0z" />
                </svg>
                <span class="share-link__label">Facebook</span>
              </a>
              <a class="share-link link-chip" href="https://twitter.com/intent/tweet?url=https://youtu.be/{{ post.youtube_id }}" target="_blank" rel="noopener">
                <svg class="share-link__icon" aria-hidden="true" focusable="false" viewBox="0 0 24 24">
                  <path d="M18.244 2H22L14.19 11.017 23.018 22H16.63l-5.036-6.437L6.09 22H2.244l8.557-9.88L1.982 2h6.482l4.38 5.84L18.244 2z" />
                </svg>
                <span class="share-link__label">X</span>
              </a>
              <a class="share-link link-chip" href="mailto:?subject={{ post.video_title | default: post.title | append: ' Brief' | uri_escape }}&body={{ 'Check out this tropical weather brief: https://youtu.be/' | append: post.youtube_id | uri_escape }}">
                <span class="share-link__label">Email</span>
              </a>
              <a class="share-link link-chip" href="sms:?&body={{ 'Check out this tropical weather brief: https://youtu.be/' | append: post.youtube_id | uri_escape }}">
                <span class="share-link__label">Text</span>
              </a>
              <button class="share-link link-chip js-copy-link" type="button" data-copy="https://youtu.be/{{ post.youtube_id }}">
                <span class="share-link__label">Copy link</span>
              </button>
            </div>
          </details>
        </article>
      </div>
    {%- else -%}
      <div class="post-pair">
        <!-- Blog post card -->
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

        <!-- Placeholder brief card keeps the row paired -->
        <article class="post-card post-card--brief-placeholder" aria-labelledby="brief-placeholder-{{ forloop.index }}">
          <header class="post-card__header">
            <time class="post-date" datetime="{{ post.date | date_to_xmlschema }}">
              {{ post.date | date: "%B %d, %Y %-I %p" }} ET
            </time>
            <h2 class="post-title" id="brief-placeholder-{{ forloop.index }}">
              {{ post.title | append: ": Brief" }}
            </h2>
          </header>

          <div class="post-card__placeholder">
            <p>No video briefing available.</p>
          </div>
        </article>
      </div>
    {%- endif -%}

  {%- endfor -%}
</div>
