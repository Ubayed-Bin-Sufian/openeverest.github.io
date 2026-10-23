---
title: "KServe provider can now publish TypeSafe decision models on the Envoy AI Gateway"
date: 2026-10-22T11:02:50
draft: false
topics:
 - kserve
 - ai
 - releases
link: https://github.com/openeverest/provider-kserve/releases/tag/v0.4.3
summary: The KServe provider now publishes TypeSafe decision models through the Envoy AI Gateway, so model traffic flows through the gateway like any other workload.
---

The KServe provider can now publish TypeSafe decision models on the Envoy AI Gateway, exposing them alongside your other AI workloads behind a single gateway front door.

This means decision models served by KServe get the Envoy AI Gateway's routing, observability, and policy handling natively — no separate exposure path or custom proxying required.

To learn more, see the [release notes](https://github.com/openeverest/provider-kserve/releases/tag/v0.4.3).
