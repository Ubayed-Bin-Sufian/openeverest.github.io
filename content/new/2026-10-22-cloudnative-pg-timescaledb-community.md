---
title: "CloudNativePG instances can now run TimescaleDB Community Edition"
date: 2026-10-22T14:02:00
draft: false
topics:
 - postgresql
 - timescaledb
 - extensions
 - releases
link: https://github.com/AdityaPimpalkar/provider-cloudnative-pg/pull/103
summary: A new timescaledbCommunity toggle enables TimescaleDB Community Edition — compression, continuous aggregates, and retention policies — on CloudNativePG instances, with PostgreSQL 18.6 as the new default.
---

The CloudNativePG provider adds a `timescaledbCommunity` extension toggle for TimescaleDB Community Edition (TimescaleDB 2.31.0, image pinned by digest). The existing `timescaledb` toggle mounts the Apache-2.0 build only; the Community Edition adds the features under the Timescale License — compression, continuous aggregates, and compression, retention and refresh policies.

It requires PostgreSQL 18.6, which is now the default version for new instances. Existing instances without an explicit version keep their current bundle. Like the Apache edition, the Community Edition can only be enabled at creation; the provider rejects enabling both editions together.

Note that the Timescale License is not open source: the Community Edition is for internal use or with a license from Timescale, and prohibits offering TimescaleDB to third parties as a database service. The provider itself remains Apache-2.0. To learn more, see the [change description](https://github.com/AdityaPimpalkar/provider-cloudnative-pg/pull/103) and the [release notes](https://github.com/AdityaPimpalkar/provider-cloudnative-pg/releases/tag/v0.3.3).
