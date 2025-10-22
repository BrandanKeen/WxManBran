---
layout: default
title: Hurricane Milton
season: 2024
landfall: October 9, 2024 &mdash; Siesta Key, FL
permalink: /storms/hurricane-milton-2024/
sort_date: 2024-10-09
thumbnail: /assets/images/storms/2024-hurricane-milton/Milton_Landfall.jpg
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
  #milton-photos .media-row {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.5rem;
    justify-items: center;
    align-items: stretch;
  }
  #milton-photos figure {
    margin: 0;
    width: 100%;
    height: 100%;
    display: grid;
    grid-template-rows: minmax(0, 1fr) auto;
  }
  #milton-photos figure:first-child { max-width: 320px; }
  #milton-photos figure:last-child { max-width: 560px; }
  #milton-photos img {
    width: 100% !important;
    height: 100%;
    object-fit: contain;
    display: block;
  }
  #milton-photos figcaption {
    text-align: center;
    font-size: 0.9rem;
    min-height: 3rem;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  @media (max-width: 900px) {
    #milton-photos .media-row {
      grid-template-columns: 1fr;
    }
    #milton-photos figure {
      max-width: 100%;
      height: auto;
      grid-template-rows: auto auto;
    }
    #milton-photos img {
      height: auto;
    }
    #milton-photos figcaption {
      min-height: 0;
    }
  }
</style>

<details class="storm-plot-group" open>
  <summary class="storm-plot-summary">Photos</summary>

  <!-- Keep this wrapper so the block aligns like Helene without touching sitewide CSS -->
  <div id="milton-photos" class="media-wide"
       style="--media-base-width: calc(100% + 6rem); --media-max-target: 1500px; --media-gutter: 1rem;">

    <div class="media-row two-up media-row--fill">
      <figure>
        <img
          src="{{ '/assets/images/previous-storms/Milton_radar.GIF' | relative_url }}"
          alt="Hurricane Milton radar loop"
          loading="lazy" decoding="async" />
        <figcaption>Radar of Hurricane Milton. Crosshairs show vehicle location.</figcaption>
      </figure>

      <figure>
        <img
          src="{{ '/assets/images/previous-storms/Milton_eye.png' | relative_url }}"
          alt="Inside the eye of Hurricane Milton"
          loading="lazy" decoding="async" />
        <figcaption>Inside the eye of Hurricane Milton</figcaption>
      </figure>
    </div>
  </div>
</details>

<details class="storm-plot-group" open>
  <summary class="storm-plot-summary">Videos</summary>
  <p>Videos coming soon.</p>
</details>

<br />

<!-- DATA-SECTION:START -->

<h2>Data</h2>

<div class="storm-data">
  <details class="storm-plot-group" open>
    <summary class="storm-plot-summary">Multi-Panel Plots</summary>
    <div class="storm-plot storm-multi-panels">
      <figure class="storm-multi-panels__figure">
        <span class="storm-multi-panels__watermark" aria-hidden="true">WxManBran.com</span>
        <a href="{{ '/assets/plots/2024-hurricane-milton/Hurricane_Milton_MultiPanel.svg' | relative_url }}" target="_blank" rel="noopener noreferrer">
          <img src="{{ '/assets/plots/2024-hurricane-milton/Hurricane_Milton_MultiPanel.svg' | relative_url }}" alt="Multi-panel plot for Hurricane Milton" loading="lazy">
        </a>
      </figure>
    </div>
  </details>
  <details class="storm-plot-group" open>
    <summary class="storm-plot-summary">Pressure (MSLP)</summary>
    <div class="storm-plot">

      <iframe src="{{ '/assets/plots/2024-hurricane-milton/Hurricane_Milton_MSLP.html' | relative_url }}" width="100%" height="520" loading="lazy" style="border:0"></iframe>
    </div>
  </details>
  <details class="storm-plot-group">
    <summary class="storm-plot-summary">Pressure Tendencies</summary>
    <div class="storm-plot">
      <iframe src="{{ '/assets/plots/2024-hurricane-milton/Hurricane_Milton_PTendency_5min.html' | relative_url }}" width="100%" height="520" loading="lazy" style="border:0"></iframe>
    </div>
    <div class="storm-plot">
      <iframe src="{{ '/assets/plots/2024-hurricane-milton/Hurricane_Milton_PTendency_10min.html' | relative_url }}" width="100%" height="520" loading="lazy" style="border:0"></iframe>
    </div>
    <div class="storm-plot">
      <iframe src="{{ '/assets/plots/2024-hurricane-milton/Hurricane_Milton_PTendency_15min.html' | relative_url }}" width="100%" height="520" loading="lazy" style="border:0"></iframe>
    </div>
    <div class="storm-plot">
      <iframe src="{{ '/assets/plots/2024-hurricane-milton/Hurricane_Milton_PTendency_30min.html' | relative_url }}" width="100%" height="520" loading="lazy" style="border:0"></iframe>
    </div>
    <div class="storm-plot">
      <iframe src="{{ '/assets/plots/2024-hurricane-milton/Hurricane_Milton_PTendency_1hour.html' | relative_url }}" width="100%" height="520" loading="lazy" style="border:0"></iframe>
    </div>
  </details>
  <details class="storm-plot-group" open>
    <summary class="storm-plot-summary">Wind Speed</summary>
    <div class="storm-plot">

      <iframe src="{{ '/assets/plots/2024-hurricane-milton/Hurricane_Milton_WindSpeed.html' | relative_url }}" width="100%" height="520" loading="lazy" style="border:0"></iframe>
    </div>
  </details>
  <details class="storm-plot-group" open>
    <summary class="storm-plot-summary">Temperature &amp; Dewpoint</summary>
    <div class="storm-plot">

      <iframe src="{{ '/assets/plots/2024-hurricane-milton/Hurricane_Milton_Temp_Dew.html' | relative_url }}" width="100%" height="520" loading="lazy" style="border:0"></iframe>
    </div>
  </details>
  <details class="storm-plot-group" open>
    <summary class="storm-plot-summary">Rain Rate</summary>
    <div class="storm-plot">

      <iframe src="{{ '/assets/plots/2024-hurricane-milton/Hurricane_Milton_RainRate.html' | relative_url }}" width="100%" height="520" loading="lazy" style="border:0"></iframe>
    </div>
  </details>
</div>
<!-- DATA-SECTION:END -->
