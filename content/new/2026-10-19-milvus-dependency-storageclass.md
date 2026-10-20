---
title: "provider-milvus adds StorageClass selection for bundled dependency volumes"
date: 2026-10-19T17:23:55Z
draft: false
topics:
 - milvus
 - kubernetes
 - releases
link: https://github.com/openeverest/provider-milvus/releases/tag/v0.3.1
summary: You can now choose the StorageClass used by the bundled dependency volumes when installing provider-milvus.
---

The provider-milvus Helm chart now lets you choose the StorageClass used by the volumes of its bundled dependencies, so Milvus installs fit clusters where the default StorageClass is unsuitable — for example, clusters that only bind slow network storage by default.

Previously, bundled dependency volumes always used the cluster's default StorageClass, which could place Milvus data on the wrong storage tier with no way to override it.

To learn more, visit the [provider-milvus v0.3.1 release](https://github.com/openeverest/provider-milvus/releases/tag/v0.3.1).