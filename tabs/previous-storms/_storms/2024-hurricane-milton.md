---
layout: default
title: Hurricane Milton
season: 2024
landfall: October 9, 2024 &mdash; Siesta Key, FL
permalink: /storms/hurricane-milton-2024/
sort_date: 2024-10-09
thumbnail: /tabs/previous-storms/media/images/storms/2024-hurricane-milton/Milton_Landfall.jpg
overview: >-
  Hurricane Milton was one of the most powerful hurricanes ever recorded in the Atlantic Basin, rapidly intensifying to a
  Category 5 before making a destructive landfall near Siesta Key, Florida.
---

<h1 class="storm-page__title">Hurricane Milton</h1>
Hurricane Milton was one of the most powerful hurricanes ever recorded in the Atlantic Basin. After forming in the southwestern Gulf of Mexico in early October, Milton rapidly intensified into a Category 5 hurricane with estimated winds of about 180 mph. The storm tracked unusually eastward across the Gulf before making landfall near Siesta Key, Florida, as a Category 3 hurricane. Despite weakening before landfall, Milton caused major coastal damage, widespread flooding, and dozens of tornadoes across Florida’s peninsula.

## Overview
- **Peak Intensity:** Category 5 (180 mph)
- **Landfall Intensity:** Category 3 (115 mph)
- **Formation:** October 5, 2024, in the southwestern Gulf of Mexico
- **Landfall:** Siesta Key, Florida, 8:30 PM EDT, October 9, 2024
- **Minimum Pressure:** 895 mb

## Timeline
- **October 5:** A tropical depression forms in the southwest Gulf and quickly strengthens into Tropical Storm Milton.
- **October 6:** Milton becomes a hurricane as it moves slowly eastward.
- **October 7:** Rapid intensification occurs, with a small eye and peak winds near 180 mph.
- **October 8:** The storm grows in size and begins to weaken while heading toward Florida.
- **October 9:** Milton makes landfall near Siesta Key as a Category 3 hurricane, producing destructive winds and surge.
- **October 10:** The system weakens inland, bringing heavy rainfall and tornadoes to central and eastern Florida.

## Impacts
- **Storm Surge:** Water levels rose 6–9 feet above ground from Venice to Boca Grande, with locally higher values near Manasota Key. Severe coastal flooding and erosion were observed.
- **Rainfall:** Totals reached up to 20 inches around the Tampa Bay region, causing widespread flooding.
- **Wind Damage:** Strong Category 3 winds damaged buildings and power infrastructure along Florida’s Gulf Coast.
- **Tornadoes:** Around 45 tornadoes occurred across the Florida Peninsula, including several rated EF-3 near Fort Pierce and Vero Beach.

<br />

#### _Source_
<em>The information above is sourced from the National Hurricane Center's Tropical Cyclone Report. You can view the full document <a href="https://www.nhc.noaa.gov/data/tcr/AL142024_Milton.pdf" target="_blank" rel="noopener noreferrer">here</a>.</em>

<br />

## Media

<!-- Milton-only local styles. Scoped so it cannot affect other pages. -->
<style>
  #milton-photos {
    width: 100%;
    margin: 0 auto;
  }
  #milton-photos .media-row {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    column-gap: 0.75rem;
    row-gap: 1.25rem;
    align-items: stretch;
  }
  #milton-photos figure {
    margin: 0;
    display: flex;
    flex-direction: column;
  }
  #milton-photos figure a {
    display: block;
    width: 100%;
    height: 100%;
    padding: 0;
    background-color: #000;
    border-radius: 10px;
    overflow: hidden;
  }
  #milton-photos figure:first-child a,
  #milton-photos figure:last-child a {
    aspect-ratio: 963 / 815;
  }
  #milton-photos img {
    display: block;
    width: 100% !important;
    height: 100% !important;
    object-fit: cover !important;
  }
  #milton-photos figcaption {
    text-align: center;
    font-size: 0.9rem;
    margin-top: 0;
    padding: 0.25rem 0 0.75rem;
  }
  #milton-photos figure:first-child figcaption {
    padding-bottom: 1.5rem;
  }
  @media (max-width: 900px) {
    #milton-photos .media-row {
      grid-template-columns: 1fr;
      row-gap: 1.5rem;
    }
    #milton-photos figure a {
      flex: none;
    }
  }
</style>

<details class="storm-plot-group" open>
  <summary class="storm-plot-summary">Photos</summary>

  <!-- Keep this wrapper so the block aligns like Helene without touching sitewide CSS -->
  <div id="milton-photos" class="media-wide"
       style="--media-base-width: calc(100% + 6rem); --media-max-target: 1500px; --media-gutter: 1rem;">

    <div class="media-row two-up media-row--fill media-row--equal-height">
      <figure>
        <a
          href="{{ '/tabs/previous-storms/media/images/Milton_radar.GIF' | relative_url }}"
          target="_blank" rel="noopener noreferrer">
          <img
            src="{{ '/tabs/previous-storms/media/images/Milton_radar.GIF' | relative_url }}"
            alt="Hurricane Milton radar loop"
            loading="lazy" decoding="async" />
        </a>
        <figcaption>Reflectivity of Hurricane Milton. Crosshairs show vehicle location.</figcaption>
      </figure>

      <figure>
        <a
          href="{{ '/tabs/previous-storms/media/images/Milton_eye.png' | relative_url }}"
          target="_blank" rel="noopener noreferrer">
          <img
            src="{{ '/tabs/previous-storms/media/images/Milton_eye.png' | relative_url }}"
            alt="Inside the eye of Hurricane Milton"
            loading="lazy" decoding="async" />
        </a>
        <figcaption>Inside the eye of Hurricane Milton</figcaption>
      </figure>
    </div>
  </div>
</details>

<details class="storm-plot-group" open>
  <summary class="storm-plot-summary">Videos</summary>
  <p>Videos coming soon.</p>
</details>

<!-- DATA-SECTION:START -->

<h2>Data</h2>

<div class="storm-data">
  <details class="storm-plot-group" open>
    <summary class="storm-plot-summary">Multi-Panel Plots</summary>
    <div class="storm-plot storm-multi-panels">
      {% assign milton_multi_panel_image = '/tabs/previous-storms/media/images/multi-panels/Hurricane_Milton_MultiPanel.png' | relative_url %}
      <figure class="storm-multi-panels__figure">
        <a
          href="{{ milton_multi_panel_image }}"
          target="_blank" rel="noopener noreferrer">
          <img
            src="{{ milton_multi_panel_image }}"
            alt="Multi-panel plot for Hurricane Milton"
            loading="lazy" decoding="async" />
        </a>
      </figure>
    </div>
  </details>
  <details class="storm-plot-group" open>
    <summary class="storm-plot-summary">Pressure (MSLP)</summary>
    <div class="storm-plot">

      <iframe src="{{ '/tabs/data/datasets/2024-hurricane-milton/plots/Hurricane_Milton_MSLP.html' | relative_url }}?v={{ site.time | date: '%s' }}" width="100%" height="520" loading="lazy" style="border:0"></iframe>
    </div>
  </details>
  <details class="storm-plot-group">
    <summary class="storm-plot-summary">Pressure Tendencies</summary>
    <div class="storm-plot">
      <iframe src="{{ '/tabs/data/datasets/2024-hurricane-milton/plots/Hurricane_Milton_PTendency_5min.html' | relative_url }}?v={{ site.time | date: '%s' }}" width="100%" height="520" loading="lazy" style="border:0"></iframe>
    </div>
    <div class="storm-plot">
      <iframe src="{{ '/tabs/data/datasets/2024-hurricane-milton/plots/Hurricane_Milton_PTendency_10min.html' | relative_url }}?v={{ site.time | date: '%s' }}" width="100%" height="520" loading="lazy" style="border:0"></iframe>
    </div>
    <div class="storm-plot">
      <iframe src="{{ '/tabs/data/datasets/2024-hurricane-milton/plots/Hurricane_Milton_PTendency_15min.html' | relative_url }}?v={{ site.time | date: '%s' }}" width="100%" height="520" loading="lazy" style="border:0"></iframe>
    </div>
    <div class="storm-plot">
      <iframe src="{{ '/tabs/data/datasets/2024-hurricane-milton/plots/Hurricane_Milton_PTendency_30min.html' | relative_url }}?v={{ site.time | date: '%s' }}" width="100%" height="520" loading="lazy" style="border:0"></iframe>
    </div>
    <div class="storm-plot">
      <iframe src="{{ '/tabs/data/datasets/2024-hurricane-milton/plots/Hurricane_Milton_PTendency_1hour.html' | relative_url }}?v={{ site.time | date: '%s' }}" width="100%" height="520" loading="lazy" style="border:0"></iframe>
    </div>
  </details>
  <details class="storm-plot-group" open>
    <summary class="storm-plot-summary">Wind Speed</summary>
    <div class="storm-plot">

      <iframe src="{{ '/tabs/data/datasets/2024-hurricane-milton/plots/Hurricane_Milton_WindSpeed.html' | relative_url }}?v={{ site.time | date: '%s' }}" width="100%" height="520" loading="lazy" style="border:0"></iframe>
    </div>
  </details>
  <details class="storm-plot-group" open>
    <summary class="storm-plot-summary">Temperature &amp; Dewpoint</summary>
    <div class="storm-plot">

      <iframe src="{{ '/tabs/data/datasets/2024-hurricane-milton/plots/Hurricane_Milton_Temp_Dew.html' | relative_url }}?v={{ site.time | date: '%s' }}" width="100%" height="520" loading="lazy" style="border:0"></iframe>
    </div>
  </details>
  <details class="storm-plot-group" open>
    <summary class="storm-plot-summary">Rain Rate</summary>
    <div class="storm-plot">

      <iframe src="{{ '/tabs/data/datasets/2024-hurricane-milton/plots/Hurricane_Milton_RainRate.html' | relative_url }}?v={{ site.time | date: '%s' }}" width="100%" height="520" loading="lazy" style="border:0"></iframe>
    </div>
  </details>
</div>
<!-- DATA-SECTION:END -->
