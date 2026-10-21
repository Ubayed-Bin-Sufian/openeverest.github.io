---
title: "SeaweedFS"
technology: "SeaweedFS"
summary: "Run SeaweedFS, the open-source distributed object store, on any Kubernetes cluster. Provision the master, volume, filer, and S3 gateway as one instance, choose how S3 is exposed, and encrypt traffic between components - through a single UI and API, powered by the seaweedfs-operator."
description: "Self-hosted SeaweedFS S3-compatible object storage on Kubernetes with OpenEverest: master, volume, filer, and S3 gateway from one instance, per-component scaling and storage classes, replication, gRPC mTLS, and ClusterIP, NodePort, LoadBalancer, or Ingress exposure."
tagline: "S3-compatible object storage, on your platform."
logo: "/images/for/seaweedfs/logo.svg"
weight: 11
draft: false
aliases:
  - "/for/object-storage/"

# Carousel: screenshots are required; add a slide with `youtube:` for an embedded video.
slides:
  - image: "/images/for/seaweedfs/for-seaweedfs-0.png"
    title: "Guided Provisioning"
    description: "Name the instance and go with sensible defaults, or open each section to size the master, volume, filer, and S3 gateway - and review the full summary before you create it."
  - image: "/images/for/seaweedfs/for-seaweedfs-1.png"
    title: "Instance Overview"
    description: "Copy the S3 endpoint into any S3 client, see replicas, CPU, memory, and disk for every component at a glance, and edit the master, volume, filer, or S3 gateway in place."

# Key capabilities. `icon` maps to layouts/partials/feature-icon.html keywords.
capabilities:
  - icon: "storage"
    title: "One Instance, Full Stack"
    description: "A single OpenEverest instance becomes a complete SeaweedFS cluster - master, volume servers, filer, and S3 gateway - and its S3 endpoint is published as connection details once it is ready."
  - icon: "backup"
    title: "A Home for Your Backups"
    description: "Keep database backups next to your data: point an OpenEverest backup storage at the SeaweedFS S3 endpoint and your PostgreSQL and other instances back up to your own cluster instead of a public cloud bucket."
  - icon: "scaling"
    title: "Scale Each Component"
    description: "Set replicas, CPU, and memory for the master, volume, filer, and S3 gateway independently, and grow volume and filer disks in place when the StorageClass allows expansion."
  - icon: "resources"
    title: "Replication & Placement"
    description: "Choose how many copies of each volume SeaweedFS keeps, validated against the servers you run. Master, volume, and filer pods spread across nodes by default, with node selectors, tolerations, and affinity on top."
  - icon: "multi-cloud"
    title: "Expose S3 Your Way"
    description: "Keep S3 private on a ClusterIP, or publish it through a NodePort, a LoadBalancer, or an Ingress with your own host and TLS certificate - the external endpoint lands on the instance automatically."
  - icon: "private-deploy"
    title: "Encrypted Between Components"
    description: "Turn on mutual TLS for all gRPC traffic between master, volume, filer, and S3, with certificates from cert-manager - the operator's self-signed CA or your own Issuer."

# Open-source repositories powering this integration.
repos:
  - label: "provider-seaweedfs"
    url: "https://github.com/openeverest/provider-seaweedfs"
    description: "The OpenEverest provider that integrates SeaweedFS into the platform, built on the Provider SDK."

# Attribution to the projects that power SeaweedFS on OpenEverest.
powered_by:
  - name: "seaweedfs/seaweedfs"
    url: "https://github.com/seaweedfs/seaweedfs"
    description: "SeaweedFS is the open-source, Apache-2.0 distributed storage system for blobs, objects, files, and data lakes, built for billions of files."
  - name: "seaweedfs/seaweedfs-operator"
    url: "https://github.com/seaweedfs/seaweedfs-operator"
    description: "SeaweedFS instances on OpenEverest are powered by the open-source seaweedfs-operator, which manages the master, volume, filer, and S3 workloads on Kubernetes."

# FAQ: rendered as an accordion and emitted as FAQPage structured data for SEO.
faq:
  - question: "Is SeaweedFS free to run on OpenEverest?"
    answer: "Yes. OpenEverest, SeaweedFS, and the seaweedfs-operator are open-source (Apache-2.0) with no licensing fees, and everything runs on your own Kubernetes cluster, in the cloud or on-premises."
  - question: "Is SeaweedFS a database?"
    answer: "No. SeaweedFS is a distributed file system and object store: masters, volume servers, a filer, and an S3-compatible gateway. It stores blobs, objects, and files, and pairs naturally with the databases OpenEverest already manages."
  - question: "How does OpenEverest run SeaweedFS under the hood?"
    answer: "The [provider-seaweedfs](https://github.com/openeverest/provider-seaweedfs) provider translates an OpenEverest `Instance` into a `Seaweed` custom resource for the open-source [seaweedfs-operator](https://github.com/seaweedfs/seaweedfs-operator), which runs the master, volume, filer, and S3 components. The provider reports endpoints and health back onto the `Instance` and never manages pods directly."
  - question: "What can I use SeaweedFS for?"
    answer: "Any workload that needs S3-compatible storage inside your own infrastructure: a backup target for your databases, dataset and artifact storage for AI pipelines, media files, or serving objects to applications without sending data to a public cloud."
  - question: "Can I store my OpenEverest database backups in SeaweedFS?"
    answer: "Yes. Create a backup storage of type S3 that points at the instance's S3 endpoint with path-style addressing, create the bucket, and attach the storage to your [PostgreSQL](/for/postgresql/) or other instance. Backups then stay in your cluster."
  - question: "How do applications outside the cluster reach S3?"
    answer: "By default the S3 gateway is only reachable inside the cluster. Switch its service to NodePort or LoadBalancer, or enable an Ingress with your host and TLS certificate; OpenEverest then publishes the external endpoint, over HTTPS when you use Ingress TLS, next to the in-cluster one."
  - question: "Is traffic encrypted?"
    answer: "Enable inter-component TLS and the master, volume, filer, and S3 gateway talk to each other over gRPC with mutual TLS, using certificates issued by [cert-manager](https://cert-manager.io). For HTTPS from S3 clients, terminate TLS at an Ingress - the in-cluster S3 service itself serves plain HTTP for now."
  - question: "Which SeaweedFS versions are supported?"
    answer: "The provider currently ships SeaweedFS 4.47 in a standalone topology that provisions the master, volume, filer, and S3 components. See the [provider repository](https://github.com/openeverest/provider-seaweedfs) for the current version matrix."
  - question: "Is the provider ready for production?"
    answer: "Not yet. The provider is an early-stage MVP: schemas and chart defaults still change between versions and there is no supported upgrade path. Backups of SeaweedFS itself, monitoring, and S3 access credentials are not configured by the provider yet, so keep the gateway on a private network. Watch the [provider repository](https://github.com/openeverest/provider-seaweedfs) for status updates."

# Optional override of the closing call-to-action text.
cta_description: "Deploy OpenEverest on any Kubernetes cluster and run your first S3-compatible object store in minutes."

# Trademark attribution, rendered at the bottom of the page.
trademark_note: "SeaweedFS is a trademark of its respective owners. OpenEverest is not affiliated with, endorsed by, or sponsored by the SeaweedFS project. These names are used for identification purposes only."
---
