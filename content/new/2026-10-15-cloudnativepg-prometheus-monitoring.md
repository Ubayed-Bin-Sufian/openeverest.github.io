---
title: "CloudNativePG metrics flow into Prometheus with a single toggle"
date: 2026-10-15T17:06:52Z
draft: false
topics:
 - postgresql
 - monitoring
 - releases
link: https://github.com/AdityaPimpalkar/provider-cloudnative-pg/releases/tag/v0.3.2
summary: Turning on Monitoring → Prometheus creates a PodMonitor that scrapes CloudNativePG instance metrics on port 9187 — no hand-written scrape configs.
---

CloudNativePG instances can now expose their metrics to Prometheus with a single toggle: Monitoring → Prometheus creates a PodMonitor (`<instance>-metrics`) that scrapes the CloudNativePG metrics exporter on port 9187, with the Prometheus Operator installed.

Scraping uses HTTPS when monitoring TLS is enabled, and `podMonitorLabels` lets your Prometheus `podMonitorSelector` select the monitor; turning the toggle off removes the PodMonitor again.

Prometheus monitoring is available in provider-cloudnative-pg v0.3.2. To learn more, visit the [release notes](https://github.com/AdityaPimpalkar/provider-cloudnative-pg/releases/tag/v0.3.2).

<!-- release-key: adityapimpalkar/provider-cloudnative-pg@v0.3.2 -->
