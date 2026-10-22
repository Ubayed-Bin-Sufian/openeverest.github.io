---
title: "TiDB provider adds monitoring for PD, TiKV, TiDB, and TiFlash"
date: 2026-10-21T15:31:57
draft: false
topics:
 - tidb
 - monitoring
 - releases
link: https://github.com/openeverest/provider-tidb/releases/tag/v0.2.0
summary: The TiDB provider now creates a PodMonitor and a VMPodScrape, exposing metrics from every TiDB component to Prometheus and VictoriaMetrics.
---

The TiDB provider now creates a PodMonitor covering PD, TiKV, TiDB, and TiFlash, plus a VMPodScrape for VictoriaMetrics, so metrics from every component of a provisioned cluster are collected automatically.

Previously, component metrics had to be scraped with hand-written monitor definitions.

Automatic component monitoring is available in provider-tidb 0.2.0. To learn more, see the [release notes](https://github.com/openeverest/provider-tidb/releases/tag/v0.2.0).
