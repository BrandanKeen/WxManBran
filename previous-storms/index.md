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
    <div class="posts-grid posts-grid--fit">
      {% assign storms_sorted = storms_for_season | sort: 'sort_date' | reverse %}
      {% for storm in storms_sorted %}
      {% assign storm_thumbnail = storm.thumbnail | default: storm.thumb | default: storm.image %}
      {% assign landfall_date_source = storm.landfall_date | default: storm.sort_date %}
      <article class="post-card">
        <header class="post-card__header">
          {% if landfall_date_source %}
          <time class="post-date" datetime="{{ landfall_date_source | date_to_xmlschema }}">
            {{ landfall_date_source | date: "%B %-d, %Y" }}
          </time>
          {% endif %}
          <h3 class="post-title">
            <a class="link-chip" href="{{ storm.url | relative_url }}">{{ storm.title }}</a>
          </h3>
        </header>
        {% if storm_thumbnail %}
        <a class="post-card__thumb-link" href="{{ storm.url | relative_url }}">
          <img class="post-card__thumb" src="{{ storm_thumbnail | relative_url }}" alt="{{ storm.title }} thumbnail">
        </a>
        {% endif %}
        <p class="read-more-wrap">
          <a class="read-more link-chip" href="{{ storm.url | relative_url }}">Explore storm →</a>
        </p>
      </article>
      {% endfor %}
    </div>
    {% endif %}
  {% endif %}
</section>
{% endfor %}

{% if all_seasons == empty %}
<p>No storms logged yet. Create Markdown files in <code>_storms</code> to populate this archive.</p>
{% endif %}
