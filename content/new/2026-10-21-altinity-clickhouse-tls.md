---
title: "Altinity ClickHouse provider now encrypts client, query, and pod-to-pod traffic"
date: 2026-10-21T14:31:36
draft: false
topics:
 - clickhouse
 - security
 - releases
link: https://github.com/openeverest/provider-altinity-clickhouse/releases/tag/v0.3.0
summary: The Altinity ClickHouse provider can now require TLS for client connections, encrypts distributed queries between replicas, and secures replication, parts fetches, and Keeper traffic between pods.
---

The Altinity ClickHouse provider now supports TLS end to end: client connections can be required to use TLS, distributed queries between replicas are encrypted, and instances no longer send query traffic across the network in plaintext.

Pod-to-pod traffic is protected as well. Replicas fetch parts over HTTPS, ClickHouse reaches Keeper over TLS, and Keeper nodes talk to each other over TLS. In required mode, a NetworkPolicy additionally limits Keeper access to the instance's own ClickHouse pods, its Keeper nodes, and the operator — closing off a previously internal-only trust boundary.

Client TLS and encrypted distributed queries are available in provider 0.2.0, and full pod-to-pod TLS in 0.3.0. To learn more, see the [release notes](https://github.com/openeverest/provider-altinity-clickhouse/releases/tag/v0.3.0).
