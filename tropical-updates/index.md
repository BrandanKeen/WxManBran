---
layout: default
title: Tropical Updates
permalink: /tropical-updates/
---

<div class="section-intro">
  <h1>Tropical Updates</h1>
  <p>Fresh analysis from the WxManBran desk. Posts appear with the newest update first.</p>
</div>

{% if site.posts.size > 0 %}
<ul class="card-list">
  {% for post in site.posts %}
  <li class="card">
    <small>{{ post.date | date: '%B %d, %Y' }}</small>
    <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
    {% if post.excerpt %}
    <p>{{ post.excerpt | strip_html | truncate: 140 }}</p>
    {% endif %}
  </li>
  {% endfor %}
</ul>
{% else %}
<p>No updates yet. When you publish a new post in <code>_posts</code>, it will appear here automatically.</p>
{% endif %}
