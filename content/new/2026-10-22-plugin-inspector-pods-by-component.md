---
title: "Inspector plugin now groups pods by instance component"
date: 2026-10-22T10:56:55
draft: false
topics:
 - openeverest
 - plugins
 - releases
link: https://github.com/openeverest/plugin-inspector/releases/tag/v0.1.2
summary: The Inspector plugin's pod list is now organized by instance component, with each component's Services shown inline.
---

The Inspector plugin now groups the pods it lists by instance component, so instead of a flat pod list you can see at a glance which pods belong to which part of your instance — and what each component's Services are.

This makes debugging faster: spot a crashed pod in context, check the Services fronting that component, and trace the problem without cross-referencing elsewhere.

The update is available in the OpenEverest Plugin Hub. To learn more, see the [release notes](https://github.com/openeverest/plugin-inspector/releases/tag/v0.1.2).
