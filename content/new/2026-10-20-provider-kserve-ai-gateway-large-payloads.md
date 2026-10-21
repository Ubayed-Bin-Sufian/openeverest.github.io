---
title: "provider-kserve AI Gateway now supports large AI payloads"
date: 2026-10-20T07:26:14
draft: false
topics:
 - ai-gateway
 - kserve
 - releases
link: https://github.com/openeverest/provider-kserve/releases/tag/v0.4.2
summary: The AI Gateway in provider-kserve no longer rejects batched embeddings, long RAG prompts, or long completions; its Envoy buffer limit is now configurable and defaults to 50 MiB.
---

The AI Gateway shipped with provider-kserve now handles large AI payloads end to end: batched embeddings requests, long RAG prompts, and long non-streaming completions pass through without errors. The Gateway's Envoy `ClientTrafficPolicy` is always rendered with a configurable `connection.bufferLimit` (new `aiGateway.bufferLimit` value, default 50 MiB), so responses and requests larger than Envoy's old 32 KiB default are no longer cut off.

Previously, the Gateway buffered whole request and response bodies to read the model name and token usage, and anything over 32 KiB was rejected — a 32-input `/v1/embeddings` batch returned HTTP 500 (`response_payload_too_large`), and long prompts failed with 413.

The fix is available in provider-kserve v0.4.2 and applies on upgrade or reinstall via Helm. To learn more, visit the [v0.4.2 release notes](https://github.com/openeverest/provider-kserve/releases/tag/v0.4.2).