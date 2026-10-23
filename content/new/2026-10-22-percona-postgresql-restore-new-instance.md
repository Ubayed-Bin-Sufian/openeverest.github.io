---
title: "Percona PostgreSQL provider adds restore to a new instance"
date: 2026-10-22T11:08:33
draft: false
topics:
 - postgresql
 - backups
 - releases
link: https://github.com/openeverest/provider-percona-postgresql/releases/tag/v0.6.0
summary: You can now restore another instance's backup — or any point in time within its retention window — into a brand-new PostgreSQL instance.
---

The Percona PostgreSQL provider can now restore one instance's backup or point-in-time into a separate, newly created instance. Restore a production snapshot into a staging instance, or recover a database as it looked at a specific moment, without touching the source cluster.

Previously, restores were confined to the instance the backup came from, which made safe recovery drills and copy-to-new-environment workflows cumbersome.

The capability is covered by an end-to-end restore test in the provider's suite. To learn more, see the [release notes](https://github.com/openeverest/provider-percona-postgresql/releases/tag/v0.6.0).
