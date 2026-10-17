---
title: "KServe predictors add support for custom model container images"
date: 2026-10-15T19:08:55Z
draft: false
topics:
 - kserve
 - ai
 - releases
link: https://github.com/openeverest/provider-kserve/releases/tag/v0.4.0
summary: Predictors can serve any model packaged as a container image, not just the models from the built-in catalog.
---

KServe predictors can now serve models from custom container images, so any model that packages as a container can run on an OpenEverest KServe instance — not only the models from the built-in catalog.

For proprietary or fine-tuned models that are not in the catalog, point the predictor at your own image: the deployment gets the same predictor topology, monitoring, and traffic management as catalog models.

Custom model images are available in provider-kserve v0.4.0. To learn more, visit the [release notes](https://github.com/openeverest/provider-kserve/releases/tag/v0.4.0).

<!-- release-key: openeverest/provider-kserve@v0.4.0 -->
