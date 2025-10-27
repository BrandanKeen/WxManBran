---
title: Tropical Updates
layout: default
permalink: /tropical-updates/
---

{% comment %}
Build-safe query: filter from site.posts so it’s never nil in PR/CI,
then sort by date (desc). This avoids “cannot sort a null”.
{% endcomment %}
{% assign updates = site.posts
  | where_exp: "p", "p.categories contains 'tropical-updates'"
  | sort: "date"
  | reverse %}

{% if updates.size == 0 %}
<p>No tropical updates found yet.</p>
{% endif %}

{% for post in updates %}
  <div class="row">
    <div class="col left">
      <h2><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h2>
      <p><small>{{ post.date | date: "%b %-d, %Y %H:%M" }}</small></p>
      {% if post.thumb %}
        <img src="{{ post.thumb }}" alt="">
      {% endif %}
      {% if post.summary %}
        <p>{{ post.summary }}</p>
      {% endif %}
      <p><a href="{{ post.url | relative_url }}">Read more</a></p>
    </div>
    <div class="col right">
      {% if post.youtube_id %}
        <iframe width="100%" height="315"
          src="https://www.youtube-nocookie.com/embed/{{ post.youtube_id }}?rel=0&modestbranding=1"
          title="YouTube video" frameborder="0"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowfullscreen></iframe>
      {% else %}
        <p>No video briefing available.</p>
      {% endif %}
    </div>
  </div>
{% endfor %}
