---
title: "ClickHouse provider adds maintenance approval, upgrade preflight, and deletion protection"
date: 2026-10-21T14:31:36
draft: false
topics:
 - clickhouse
 - releases
link: https://github.com/openeverest/provider-altinity-clickhouse/releases/tag/v0.3.0
summary: Rolling restarts now wait for your approval, upgrades run preflight checks before anything is applied, Ready reflects the actual rollout state, and deleted instances retain their data by default.
---

The Altinity ClickHouse provider adds a set of day-2 safety features for running ClickHouse in production:

- **Maintenance approval** — provider-initiated rolling restarts are held until you approve the pending action, then proceed as a controlled rollout (v0.2.0).
- **Deletion protection** — deleting an instance retains its data by default, and instance pods are spread across nodes for resilience (v0.2.0).
- **Trustworthy Ready status** — the instance reports Ready only once the operator has fully rolled out the last applied change, and storage growth on a StorageClass that cannot expand volumes is rejected up front (v0.3.0).
- **Upgrade preflight** — helm upgrade exercises the new provider against your live instances and aborts before applying anything if an instance would be stranded (v0.3.0).

Together these close the gaps where an innocent action — a restart, an upgrade, a deletion — could previously disrupt or destroy a running cluster. To learn more, see the [release notes](https://github.com/openeverest/provider-altinity-clickhouse/releases/tag/v0.3.0).
