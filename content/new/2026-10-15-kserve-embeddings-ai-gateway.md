---
title: "KServe embedding models can now be served through the Envoy AI Gateway"
date: 2026-10-15T19:08:55Z
draft: false
topics:
 - kserve
 - ai
 - releases
link: https://github.com/openeverest/provider-kserve/releases/tag/v0.4.0
summary: Embedding models can now be served through the Envoy AI Gateway, giving embedding traffic the same routing and management as other model endpoints.
---

Embedding models deployed on KServe instances can now be served through the Envoy AI Gateway, so embedding traffic gets the same routing and traffic management as every other model endpoint.

Previously, embedding models ran on their own endpoints, outside the AI Gateway introduced in provider-kserve v0.2.0. Together with the predictor topology from v0.3.0, embeddings can now run on CPU or GPU nodes and be exposed through the gateway like any other model.

Embedding support in the AI Gateway is available in provider-kserve v0.4.0. To learn more, visit the [release notes](https://github.com/openeverest/provider-kserve/releases/tag/v0.4.0).

<!-- release-key: openeverest/provider-kserve@v0.4.0 -->
