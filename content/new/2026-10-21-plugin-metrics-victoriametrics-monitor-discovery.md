---
title: "Metrics plugin now discovers VictoriaMetrics operator monitors"
date: 2026-10-21T13:37:48
draft: false
topics:
 - victoriametrics
 - monitoring
 - releases
link: https://github.com/openeverest/plugin-metrics/releases/tag/v0.2.1
summary: The OpenEverest metrics plugin automatically discovers VictoriaMetrics operator monitors, so Prometheus-class databases are scraped without extra configuration.
---

The OpenEverest metrics plugin can now discover VictoriaMetrics operator monitors for use as a Prometheus source, eliminating manual scrape configuration for clusters that run the VictoriaMetrics operator.

Previously, teams using VictoriaMetrics had to wire up monitor discovery themselves before metrics flowed into the plugin's Prometheus source.

Monitor discovery is available in plugin-metrics 0.2.1. To learn more, see the [release notes](https://github.com/openeverest/plugin-metrics/releases/tag/v0.2.1).
