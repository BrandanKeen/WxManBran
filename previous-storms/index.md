---
layout: default
title: Previous Storms
---
# Previous Storms

{% assign grouped = site.storms | group_by: "season" | sort: "name" | reverse %}
{% for g in grouped %}
## {{ g.name }}
<ul>
  {% for s in g.items %}
    <li><a href="{{ s.url | relative_url }}">{{ s.title }}</a></li>
  {% endfor %}
</ul>
{% endfor %}
