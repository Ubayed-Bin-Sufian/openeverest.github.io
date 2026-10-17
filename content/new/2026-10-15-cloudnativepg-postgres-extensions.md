---
title: "CloudNativePG instances gain first-class PostgreSQL extensions"
date: 2026-10-15T17:06:52Z
draft: false
topics:
 - postgresql
 - extensions
 - releases
link: https://github.com/AdityaPimpalkar/provider-cloudnative-pg/releases/tag/v0.3.2
summary: pgvector, pgAudit, TimescaleDB, PostGIS, pgRouting, pg_ivm, wal2json, and Apache AGE can now be enabled straight from the instance spec.
---

CloudNativePG instances can now enable PostgreSQL extensions directly from the instance spec with `spec.components.engine.parameters.extensions.<name>.enabled`: pgvector, pgAudit, TimescaleDB OSS, PostGIS, pgRouting, pg_ivm, wal2json, and Apache AGE.

pgvector and pgAudit are bundled for PostgreSQL 14–18 and can be enabled on a running instance. TimescaleDB, PostGIS, pgRouting, pg_ivm, wal2json, and Apache AGE load from image volumes on PostgreSQL 18 with Kubernetes ImageVolume support (1.35+, or 1.33/1.34 with the feature gate). Enabling TimescaleDB also repairs instances that previously never became Ready because their `Database` resource was not synced.

First-class extensions are available in provider-cloudnative-pg v0.3.2. To learn more, visit the [release notes](https://github.com/AdityaPimpalkar/provider-cloudnative-pg/releases/tag/v0.3.2).

<!-- release-key: adityapimpalkar/provider-cloudnative-pg@v0.3.2 -->
