---
title: "CloudNativePG provider adds Require TLS, synchronous replication, and native backup retention"
date: 2026-10-22T14:02:00
draft: false
topics:
 - postgresql
 - security
 - high-availability
 - releases
link: https://github.com/AdityaPimpalkar/provider-cloudnative-pg/releases/tag/v0.3.3
summary: CloudNativePG instances gain required TLS for clients, synchronous replication, separate WAL storage, time-based backup retention with deletion, and read endpoints in the connection Secret.
---

The CloudNativePG provider's v0.3.3 release hardens PostgreSQL operations end to end:

- **Require TLS** — `parameters.requireTLS` rejects unencrypted client connections with a `pg_hba` reload, without restarting pods. New and restored instances in the UI get it by default.
- **Synchronous replication** — require a chosen number of standbys to confirm every commit, with quorum or priority-order confirmation, and choose whether writes stop (`required`) or fall back to asynchronous replication (`preferred`) when too few standbys remain.
- **Separate WAL storage** — put write-ahead logs on their own volume (`walStorage`), sized and expanded independently of the data volume, so write-heavy clusters get predictable performance.
- **Native backup retention and deletion** — time-window retention delegated to Barman across the cluster's whole archive (e.g. `30d`), plus `deletionPolicy: Delete` to remove base backups from the object store; conflicting policies on shared storage are refused up front.
- **Read endpoints in the connection Secret** — `host`, `host-r`, and `host-ro` for read-write, any-ready-instance, and replica-only targets, with `sslmode=require` included in the connection URI.

All of these are available in provider-cloudnative-pg v0.3.3. To learn more, see the [release notes](https://github.com/AdityaPimpalkar/provider-cloudnative-pg/releases/tag/v0.3.3).
