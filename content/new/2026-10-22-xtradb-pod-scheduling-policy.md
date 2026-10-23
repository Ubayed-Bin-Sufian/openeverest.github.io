---
title: "Percona XtraDB Cluster provider now exposes pod scheduling policy in the UI"
date: 2026-10-22T09:28:18
draft: false
topics:
 - mysql
 - xtradb
 - releases
link: https://github.com/openeverest/provider-percona-xtradb-cluster/releases/tag/v0.4.0
summary: Percona XtraDB Cluster instances can now be configured with pod scheduling policies — including affinity — directly from the OpenEverest UI.
---

The Percona XtraDB Cluster provider now lets you define pod scheduling policy, including affinity rules, from the OpenEverest UI, with the supported fields declared explicitly so you know exactly what can be configured.

Scheduling control lets you pin XtraDB Cluster pods to specific nodes or zones — important for latency, licensing, and high availability — without hand-editing manifests.

The provider also ships a conformance test and a default replica count. To learn more, see the [release notes](https://github.com/openeverest/provider-percona-xtradb-cluster/releases/tag/v0.4.0).
