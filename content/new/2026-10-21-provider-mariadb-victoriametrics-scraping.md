---
title: "MariaDB provider adds automatic VictoriaMetrics scraping"
date: 2026-10-21T12:38:50
draft: false
topics:
 - mariadb
 - monitoring
 - releases
link: https://github.com/openeverest/provider-mariadb/releases/tag/v0.2.1
summary: The MariaDB provider now creates a VMServiceScrape, so MariaDB metrics land in VictoriaMetrics without any manual setup.
---

The MariaDB provider now creates a VMServiceScrape for VictoriaMetrics, so every provisioned MariaDB instance is automatically scraped and its metrics appear in VictoriaMetrics with no manual configuration.

Previously, teams had to define their own scrape jobs to get MariaDB metrics into a VictoriaMetrics stack.

Automatic scraping is available in provider-mariadb 0.2.1. To learn more, see the [release notes](https://github.com/openeverest/provider-mariadb/releases/tag/v0.2.1).
