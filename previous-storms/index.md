---
layout: default
title: Previous Storms
permalink: /previous-storms/
---

<div class="section-intro">
  <h1>Previous Storms</h1>
  <p>Dive into the archive of tracked systems, organized by hurricane season. Each page includes key landfall details and room for radar loops or galleries.</p>
</div>

{% assign grouped = site.storms | group_by: 'season' | sort: 'name' | reverse %}
{% for group in grouped %}
<section class="storm-season">
  <h2>{{ group.name }} Season</h2>
  <ul class="card-list">
    {% assign storms_sorted = group.items | sort: 'title' %}
    {% for storm in storms_sorted %}
    <li class="card">
      <a href="{{ storm.url | relative_url }}">{{ storm.title }}</a>
      {% if storm.landfall %}
      <small>Landfall: {{ storm.landfall }}</small>
      {% endif %}
      {% if storm.excerpt %}
      <p>{{ storm.excerpt | strip_html | truncate: 160 }}</p>
      {% endif %}
    </li>
    {% endfor %}
  </ul>
</section>
{% endfor %}

{% if grouped == empty %}
<p>No storms logged yet. Create Markdown files in <code>_storms</code> to populate this archive.</p>
{% endif %}
