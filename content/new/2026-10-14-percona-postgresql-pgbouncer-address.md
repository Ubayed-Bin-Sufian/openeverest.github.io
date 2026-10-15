---
title: "PgBouncer connection endpoints now resolve correctly in Percona PostgreSQL"
date: 2026-10-14T12:59:16Z
draft: false
topics:
 - percona-postgresql
 - pgbouncer
 - releases
link: https://github.com/openeverest/provider-percona-postgresql/releases/tag/v0.5.0
summary: Exposed PgBouncer endpoints now publish the correct address — the load balancer address when exposed, the direct host when PgBouncer runs without replicas.
---

Percona PostgreSQL clusters now publish the correct connection address for PgBouncer in both deployment shapes: the load balancer address when PgBouncer is exposed through one, and the direct database host when PgBouncer runs without replicas.

Previously, clients could receive a wrong or unreachable endpoint in these configurations and fail to connect until the address was corrected manually.

The fix is available now with provider-percona-postgresql v0.5.0. To learn more, visit the [release notes](https://github.com/openeverest/provider-percona-postgresql/releases/tag/v0.5.0).
