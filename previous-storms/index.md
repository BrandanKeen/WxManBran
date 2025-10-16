---
layout: default
title: Previous Storms
permalink: /previous-storms/
---

<div class="section-intro">
  <h1>Previous Storms</h1>
  <p>This portion of the website is still under construction. Upon completion, it will have interactive plots to view data from previous hurricane intercepts.</p>
</div>

{% assign storms_by_season = site.storms | group_by: 'season' %}
{% assign manual_seasons = "2025" | split: "," %}
{% assign existing_seasons = storms_by_season | map: 'name' | uniq %}
{% assign all_seasons = manual_seasons | concat: existing_seasons %}
{% assign all_seasons = all_seasons | uniq | sort | reverse %}

{% for season in all_seasons %}
<section class="storm-season">
  <h2>{{ season }} Season</h2>
  {% assign season_group = storms_by_season | where: "name", season | first %}
  {% if season_group %}
    {% assign storms_for_season = season_group.items | where_exp: "storm", "storm.placeholder != true" %}
    {% if storms_for_season.size > 0 %}
    <ul class="card-list">
      {% assign storms_sorted = storms_for_season | sort: 'title' %}
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
    {% endif %}
  {% endif %}
</section>
{% endfor %}

{% if all_seasons == empty %}
<p>No storms logged yet. Create Markdown files in <code>_storms</code> to populate this archive.</p>
{% endif %}
