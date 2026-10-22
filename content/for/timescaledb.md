---
title: "TimescaleDB"
technology: "TimescaleDB"
summary: "Run TimescaleDB for time-series and real-time analytics on any Kubernetes cluster. OpenEverest provisions PostgreSQL through the CloudNativePG provider and enables TimescaleDB, Apache 2.0 or Community edition, with a single toggle."
logo: "/images/for/timescaledb/logo.svg"
tagline: "Time-series PostgreSQL, Apache 2.0 or Community edition."
weight: 12
draft: false

# Reuses the PostgreSQL screenshots under static/images/for/postgresql/ until
# TimescaleDB-specific ones are available.
slides:
  - image: "/images/for/postgresql/for-postgresql-0.png"
    title: "Guided Provisioning"
    description: "Create a PostgreSQL 18 database with the CloudNativePG provider from the OpenEverest UI, then enable TimescaleDB while provisioning it."
  - image: "/images/for/postgresql/for-postgresql-2.png"
    title: "CloudNativePG Advanced Configuration"
    description: "Tune storage and PostgreSQL settings for your time-series workload through the CloudNativePG provider without writing Kubernetes manifests."
  - image: "/images/for/postgresql/for-postgresql-3.png"
    title: "Cluster Overview"
    description: "Review cluster health, connection details, replicas, and resources. TimescaleDB is created in the application database and ready to use."

# Key capabilities. `icon` maps to layouts/partials/feature-icon.html keywords.
capabilities:
  - icon: "database-engines"
    title: "Two TimescaleDB Editions"
    description: "Choose TimescaleDB under the Apache 2.0 license, or the Community edition with compression, continuous aggregates, and data retention policies."
  - icon: "config"
    title: "One-Toggle Setup"
    description: "Enable TimescaleDB when you create the database. OpenEverest mounts the extension image, preloads the library, and runs CREATE EXTENSION for you."
  - icon: "scaling"
    title: "High Availability"
    description: "Run TimescaleDB on PostgreSQL clusters with replicas and CloudNativePG-managed failover."
  - icon: "backup"
    title: "Backups & PITR"
    description: "Back up TimescaleDB like any PostgreSQL database, with scheduled backups and point-in-time recovery to S3-compatible storage."
  - icon: "storage"
    title: "Room for Time-Series Data"
    description: "Pick the storage class, add a separate WAL volume, and expand volumes as your hypertables grow."
  - icon: "private-deploy"
    title: "Telemetry Off by Default"
    description: "TimescaleDB runs on your own Kubernetes infrastructure with telemetry disabled out of the box."

# Open-source repositories powering this integration.
repos:
  - label: "provider-cloudnative-pg"
    url: "https://github.com/AdityaPimpalkar/provider-cloudnative-pg"
    description: "The OpenEverest provider that provisions PostgreSQL through CloudNativePG and enables TimescaleDB and other extensions."
  - label: "solanicaio/postgresql-extensions"
    url: "https://github.com/solanicaio/postgresql-extensions"
    description: "PostgreSQL extension images for Kubernetes ImageVolumes, including the TimescaleDB Community edition image."

powered_by:
  - name: "timescale/timescaledb"
    url: "https://github.com/timescale/timescaledb"
    description: "TimescaleDB is a PostgreSQL extension for high-performance real-time analytics on time-series and event data."
  - name: "cloudnative-pg/cloudnative-pg"
    url: "https://github.com/cloudnative-pg/cloudnative-pg"
    description: "The CloudNativePG operator manages PostgreSQL clusters on Kubernetes, including replication, failover, and extension images."

# FAQ: rendered as an accordion and emitted as FAQPage structured data for SEO.
faq:
  - question: "How does OpenEverest run TimescaleDB?"
    answer: "TimescaleDB is a PostgreSQL extension. OpenEverest runs it on PostgreSQL clusters provisioned through the [CloudNativePG provider](https://github.com/AdityaPimpalkar/provider-cloudnative-pg): enable the TimescaleDB toggle when you create the database, and the provider mounts the extension image, preloads it, and creates the extension in the application database."
  - question: "What is the difference between the Apache 2.0 and Community editions?"
    answer: "The Apache 2.0 edition contains the open-source core of TimescaleDB, including hypertables. The Community edition adds features under the [Timescale License (TSL)](https://github.com/timescale/timescaledb/blob/main/tsl/LICENSE-TIMESCALE), such as native compression, continuous aggregates, and compression, retention, and refresh policies."
  - question: "Can I use the TimescaleDB Community edition for any workload?"
    answer: "No. The Timescale License is not an open-source license. You can use the Community edition internally or under a license from Timescale, but the TSL prohibits offering TimescaleDB to third parties as a database service. Enabling it means you accept the TSL. OpenEverest and the provider remain Apache 2.0."
  - question: "Which PostgreSQL and Kubernetes versions are required?"
    answer: "TimescaleDB requires PostgreSQL 18, and the Community edition requires PostgreSQL 18.6 or later. The extension is mounted as an image volume, so Kubernetes needs ImageVolume support: version 1.35 or later, or 1.33 and 1.34 with the ImageVolume feature gate enabled."
  - question: "Can I enable TimescaleDB on an existing database?"
    answer: "No. TimescaleDB is preloaded by PostgreSQL, so it can only be enabled when the database is created, and it cannot be disabled afterward. Only one edition can be enabled per database."
  - question: "Is TimescaleDB free to run on OpenEverest?"
    answer: "OpenEverest is open source with no licensing fees, and the Apache 2.0 edition of TimescaleDB is free to use. The Community edition is free to use under the terms of the Timescale License."

# Trademark attribution for the upstream projects named on this page.
trademark_note: "TimescaleDB and Timescale are trademarks of Timescale, Inc. (Tiger Data). PostgreSQL and CloudNativePG are trademarks or names of their respective owners. OpenEverest is not affiliated with, endorsed by, or sponsored by these organizations."
---

> TimescaleDB is available through the CloudNativePG provider. It is not available in the Percona PostgreSQL provider.
