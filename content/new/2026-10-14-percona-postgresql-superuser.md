---
title: "You can now expose the PostgreSQL superuser in Percona PostgreSQL clusters"
date: 2026-10-14T12:59:16Z
draft: false
topics:
 - percona-postgresql
 - postgresql
 - releases
link: https://github.com/openeverest/provider-percona-postgresql/releases/tag/v0.5.0
summary: The provider can now expose the PostgreSQL superuser account, for operations that need full privileges on a Percona PostgreSQL cluster.
---

The Percona PostgreSQL provider can now expose the PostgreSQL superuser account, giving administrators a documented path to full-privilege access when migration or maintenance work demands it.

Previously, superuser-level operations required manual steps inside the pod, outside the provider's managed workflow.

Superuser exposure is available now with provider-percona-postgresql v0.5.0. To learn more, visit the [release notes](https://github.com/openeverest/provider-percona-postgresql/releases/tag/v0.5.0).
