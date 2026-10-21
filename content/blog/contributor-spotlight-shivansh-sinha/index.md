---
title: "Contributor Spotlight: Shivansh Sinha"
date: 2026-10-21T06:00:00
draft: false
image:
    url: contrib-spotlight-cover.png
    attribution:
authors:
  - spron-in
tags:
  - community
  - open-source
  - spotlight
  - kubernetes
  - databases
summary: "Meet Shivansh Sinha — a DevOps and backend engineer in Bengaluru who started by filing bugs against the OpenEverest v2 dev builds, and kept going until he was fixing them himself."
---

Some contributors arrive with a feature request. Shivansh Sinha arrived with a bug report. Then he came back with another one, and another, and eventually with the code to fix them.

<img src="headshot.png" alt="OpenEverest Contributor - Shivansh Sinha photo" style="max-width: 480px; width: 100%; height: auto;">

Shivansh is a DevOps and backend engineer based in Bengaluru, India. Until recently he was a founding engineer at CapMob, a fintech startup in the UAE, where he owned the backend and the AWS infrastructure end to end: ECS Fargate, an ALB and Aurora Postgres across two regions, a migration to Terraform, the CI/CD pipeline, and a move of services from Next.js to Go.

### Learning by building

Shivansh has been contributing to open source for about a year and a half, mostly in the Kubernetes and CNCF ecosystem. He likes working close to the system. Instead of collecting certificates, he'd rather build something, watch where it breaks, and figure out why.

### How he found OpenEverest

He first heard about OpenEverest from seniors who kept praising the community and the way the maintainers work. He wanted to see for himself, so he picked up the early OpenEverest v2 developer builds and started testing them. Every new dev release gave him more to find, and he's still finding things in v2.0.0-dev.4.

His bug reports tend to land where things quietly go wrong: install and upgrade correctness. A `helm upgrade` that [didn't apply schema changes](https://github.com/openeverest/provider-percona-postgresql/issues/17) to the live Provider object. An Instance created outside the provider's namespace that [silently hung](https://github.com/openeverest/provider-percona-postgresql/issues/18), with cleanup deadlocking on finalizers. A CRD generation step that [pointed at a non-existent ref](https://github.com/openeverest/helm-charts/issues/90) and shipped stale CRDs. An `everestctl extension uninstall` that [reported success](https://github.com/openeverest/openeverest/issues/2970) while leaving an orphaned resource behind.

"Contributing has felt fun, with such a supportive community and maintainers," he says.

### From bug reports to pull requests

It didn't take long for the reports to turn into fixes, often for the very bugs he had filed himself:

- He noticed that `Instance.status.components` was never populated, so a stuck component looked exactly like a healthy one ([openeverest#3247](https://github.com/openeverest/openeverest/issues/3247)). He then wired component statuses through the provider runtime in [openeverest#3252](https://github.com/openeverest/openeverest/pull/3252).
- After reporting that Instances outside the release namespace hung forever, he taught the PostgreSQL provider to watch Instances in all namespaces in [provider-percona-postgresql#21](https://github.com/openeverest/provider-percona-postgresql/pull/21).
- He found that the `go mod tidy` check in the core repository's CI had silently stopped running, and brought it back to life in [openeverest#2962](https://github.com/openeverest/openeverest/pull/2962).
- In the Helm charts, he added `httpProxy`/`httpsProxy`/`noProxy` support to chart hook Jobs across six library templates ([helm-charts#77](https://github.com/openeverest/helm-charts/pull/77)), which matters to anyone installing OpenEverest behind a corporate proxy. He also fixed Helm version drift and step ordering in the release workflow ([helm-charts#82](https://github.com/openeverest/helm-charts/pull/82)).

He's been working on the providers too. For the ClickHouse provider, he added a unit-test job and gated chainsaw integration tests to CI ([provider-altinity-clickhouse#21](https://github.com/openeverest/provider-altinity-clickhouse/pull/21)), and built a `BackupProvider` implementation that maps the v2 `BackupStorage` S3 contract onto clickhouse-backup ([provider-altinity-clickhouse#22](https://github.com/openeverest/provider-altinity-clickhouse/pull/22)). For the KubeAI provider, he's building a curated LLM catalog shipped as Helm-installed `InstancePreset`s ([provider-kubeai#8](https://github.com/openeverest/provider-kubeai/pull/8)), work that began with him pushing for a v2 CRD release that included `InstancePreset` in the first place ([openeverest#2615](https://github.com/openeverest/openeverest/issues/2615)).

Right now he's building the [OpenSearch provider](https://github.com/openeverest/provider-opensearch) with us, feature by feature: getting CI green on the first run, rejecting unsafe changes such as version downgrades, major-version jumps, and storage class changes during validation, and pinning the operator image.

He also wrote [High Availability PostgreSQL: From Zero to Cluster](https://openeverest.io/blog/ha-postgresql-openeverest/) for this blog. He deployed a three-node PostgreSQL cluster on OpenEverest v2, killed the primary, and timed how fast it recovered. Very much on brand.

### Beyond the terminal

Away from the keyboard, Shivansh is happiest on a football turf. His ideal evening is a two-hour session in Bengaluru, played purely for the fun of it. It's a long stretch away from screens, and he looks forward to it.

He also plays guitar, mostly for himself and his friends. No audience, no stage, just the instrument and some time to spend with it.

And he writes. Shivansh blogs about what he builds and learns, and the HA PostgreSQL post came out of that habit. For someone who learns by breaking things, writing is how he makes sure the lessons stick.

---

Thank you for all the bugs, Shivansh, and for fixing so many of them. Connect with him on [GitHub](https://github.com/shivansh-source).

To get involved with OpenEverest yourself:

<div style="display:flex;gap:12px;margin-top:24px;flex-wrap:wrap;">
  <a href="https://cloud-native.slack.com/archives/C09RRGZL2UX" target="_blank" rel="noopener noreferrer" style="display:inline-flex;align-items:center;gap:8px;background-color:#4A154B;color:#fff;text-decoration:none;padding:10px 20px;border-radius:6px;font-weight:600;font-size:15px;">
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 122.8 122.8"><path d="M25.8 77.6c0 7.1-5.8 12.9-12.9 12.9S0 84.7 0 77.6s5.8-12.9 12.9-12.9h12.9v12.9zm6.5 0c0-7.1 5.8-12.9 12.9-12.9s12.9 5.8 12.9 12.9v32.3c0 7.1-5.8 12.9-12.9 12.9s-12.9-5.8-12.9-12.9V77.6z" fill="#e01e5a"/><path d="M45.2 25.8c-7.1 0-12.9-5.8-12.9-12.9S38.1 0 45.2 0s12.9 5.8 12.9 12.9v12.9H45.2zm0 6.5c7.1 0 12.9 5.8 12.9 12.9s-5.8 12.9-12.9 12.9H12.9C5.8 58.1 0 52.3 0 45.2s5.8-12.9 12.9-12.9h32.3z" fill="#36c5f0"/><path d="M97 45.2c0-7.1 5.8-12.9 12.9-12.9s12.9 5.8 12.9 12.9-5.8 12.9-12.9 12.9H97V45.2zm-6.5 0c0 7.1-5.8 12.9-12.9 12.9s-12.9-5.8-12.9-12.9V12.9C64.7 5.8 70.5 0 77.6 0s12.9 5.8 12.9 12.9v32.3z" fill="#2eb67d"/><path d="M77.6 97c7.1 0 12.9 5.8 12.9 12.9s-5.8 12.9-12.9 12.9-12.9-5.8-12.9-12.9V97h12.9zm0-6.5c-7.1 0-12.9-5.8-12.9-12.9s5.8-12.9 12.9-12.9h32.3c7.1 0 12.9 5.8 12.9 12.9s-5.8 12.9-12.9 12.9H77.6z" fill="#ecb22e"/></svg>
    Join Slack
  </a>
  <a href="https://github.com/openeverest/openeverest" target="_blank" rel="noopener noreferrer" style="display:inline-flex;align-items:center;gap:8px;background-color:#24292f;color:#fff;text-decoration:none;padding:10px 20px;border-radius:6px;font-weight:600;font-size:15px;">
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 16 16" fill="#fff"><path d="M8 .25a7.75 7.75 0 1 0 0 15.5A7.75 7.75 0 0 0 8 .25zm0 1.5a6.25 6.25 0 0 1 1.97 12.18c-.31.06-.42-.13-.42-.3v-1.05c0-.36-.01-1.02-.49-1.4 1.62-.18 2.5-.88 2.5-2.57 0-.57-.2-1.1-.53-1.49.05-.14.23-.7-.05-1.47 0 0-.44-.14-1.44.54a5.02 5.02 0 0 0-2.62 0C5.93 6.6 5.49 6.74 5.49 6.74c-.28.77-.1 1.33-.05 1.47-.33.39-.53.92-.53 1.49 0 1.69.88 2.39 2.5 2.57-.31.27-.43.67-.47 1.04-.42.19-1.5.52-2.16-.62 0 0-.39-.71-1.13-.76 0 0-.72-.01-.05.45 0 0 .48.23.82 1.08 0 0 .43 1.32 2.49.87v.75c0 .17-.11.36-.42.3A6.25 6.25 0 0 1 8 1.75z"/></svg>
    Star the Repo
  </a>
</div>