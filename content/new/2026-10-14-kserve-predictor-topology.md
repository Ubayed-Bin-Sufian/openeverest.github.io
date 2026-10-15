---
title: "KServe predictor topology brings embedding inference to CPU and GPU"
date: 2026-10-14T18:59:13Z
draft: false
topics:
 - kserve
 - ai
 - ui
 - releases
link: https://github.com/openeverest/provider-kserve/releases/tag/v0.3.0
summary: KServe instances gain predictor topology in the UI, CR, and API, unlocking Hugging Face embedding models on both CPU and GPU, with a model catalog and Prometheus monitoring built in.
---

The KServe provider introduces **predictor topology**: the layout of a predictor deployment is now a first-class, configurable part of the instance, available in the OpenEverest UI, the Custom Resource, and the API. Custom environment variables, scheduling constraints, external Services, service accounts, labels, and security contexts all pass through to the inference pods, so settings that previously could not reach the predictor now get there directly.

Predictor topology unlocks the **embeddings use case**: Hugging Face embedding models can now be served on regular CPU-only nodes as well as on GPU-backed ones. Previously, serving embeddings typically meant hand-building a GPU-backed deployment, which priced out inference workloads with modest throughput needs.

To make this turnkey, the provider ships a **model catalog** with various CPU, GPU, and classic models for predictor topologies — pick a ready-to-deploy model instead of assembling container images and arguments manually.

The new topology is observable, too: the provider emits a **PodMonitor** for every InferenceService, so predictor deployments can be monitored with standard Prometheus — metrics are scraped automatically as deployments come and go.

Predictor topology, the model catalog, and PodMonitor are available in provider-kserve v0.3.0. To learn more, visit the [release notes](https://github.com/openeverest/provider-kserve/releases/tag/v0.3.0).

<!-- release-key: openeverest/provider-kserve@v0.3.0 -->
