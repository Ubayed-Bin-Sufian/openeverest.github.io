---
title: "Percona providers now label PMM metrics with the instance and namespace"
date: 2026-10-19T16:23:06Z
draft: false
topics:
 - percona-postgresql
 - mongodb
 - monitoring
 - releases
link: https://github.com/openeverest/provider-percona-postgresql/releases/tag/v0.5.1
summary: PMM metrics exported by the Percona PostgreSQL, Percona Server for MongoDB, and Percona XtraDB Cluster providers now carry the instance and namespace labels.
---

The Percona providers for PostgreSQL, Percona Server for MongoDB, and Percona XtraDB Cluster now label their PMM (Percona Monitoring and Management) metrics with the originating instance and namespace.

Previously, metrics from multiple instances could appear in PMM without enough labels to tell them apart, making dashboards and alerts harder to scope to a single cluster.

The labels are available now in provider-percona-postgresql v0.5.1, provider-percona-server-mongodb v0.4.1, and provider-percona-xtradb-cluster v0.3.2. To learn more, visit the [provider-percona-postgresql v0.5.1 release](https://github.com/openeverest/provider-percona-postgresql/releases/tag/v0.5.1).