---
title: "TiDB provider now encrypts all cluster traffic with provider-issued certificates"
date: 2026-10-21T15:31:57
draft: false
topics:
 - tidb
 - security
 - releases
link: https://github.com/openeverest/provider-tidb/releases/tag/v0.2.0
summary: The TiDB provider issues TLS certificates through cert-manager and encrypts all TiDB traffic, with backups running as a provider-managed account.
---

The TiDB provider now has cert-manager issue the TLS certificates for the cluster and encrypts TiDB traffic with those provider-issued certificates, so no component talks in plaintext.

BR backup and restore jobs also run as a provider-managed account instead of a default identity, tightening what those jobs can touch.

Encrypted TiDB traffic is available in provider-tidb 0.2.0. To learn more, see the [release notes](https://github.com/openeverest/provider-tidb/releases/tag/v0.2.0).
