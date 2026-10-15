---
title: "Percona PostgreSQL provider adds pod scheduling policies"
date: 2026-10-14T12:59:16Z
draft: false
topics:
 - percona-postgresql
 - postgresql
 - releases
link: https://github.com/openeverest/provider-percona-postgresql/releases/tag/v0.5.0
summary: You can now define pod scheduling policies for Percona PostgreSQL clusters, including affinity and placement rules.
---

The Percona PostgreSQL provider now supports pod scheduling policies, so you can control where cluster pods land through affinity and placement rules instead of patching workloads after creation.

Previously, scheduling constraints had to be applied out-of-band and could be lost on operator reconciliation.

Pod scheduling policies are available now with provider-percona-postgresql v0.5.0. To learn more, visit the [release notes](https://github.com/openeverest/provider-percona-postgresql/releases/tag/v0.5.0).
