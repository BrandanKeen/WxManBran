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
    <ul class="card-list storm-card-list">
      {% assign storms_sorted = storms_for_season | sort: 'sort_date' | reverse %}
      {% for storm in storms_sorted %}
      {% assign storm_thumbnail = storm.thumbnail | default: storm.thumb | default: storm.image %}
      <li class="storm-card">
        <a class="storm-card__link" href="{{ storm.url | relative_url }}">
          <div class="storm-card__thumb{% unless storm_thumbnail %} storm-card__thumb--empty{% endunless %}">
            {% if storm_thumbnail %}
            <img src="{{ storm_thumbnail | relative_url }}" alt="{{ storm.title }} thumbnail">
            {% endif %}
          </div>
          {% assign landfall_date_source = storm.landfall_date | default: storm.sort_date %}
          <h3 class="storm-card__title">
            {{ storm.title }}
            {% if landfall_date_source %}
            <span class="storm-card__date">&mdash; {{ landfall_date_source | date: "%B %-d" }}</span>
            {% endif %}
          </h3>
          {% assign overview_text = storm.overview | default: storm.excerpt %}
          {% if overview_text %}
          <p class="storm-card__overview">{{ overview_text | strip_html | strip }}</p>
          {% endif %}
        </a>
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
