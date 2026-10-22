---
title: "A System 1 for Your Platform: OpenJev on KServe and OpenEverest"
date: 2026-10-22T00:00:00
draft: false
image:
    url: openjev-cover.jpg
authors:
  - spron-in
tags:
  - blog
  - kserve
  - ai
  - llm
  - kubernetes
  - provider
  - agents
summary: "OpenJev is an open-weights decision model: you ask a typed question, it answers with a probability for every option in one forward pass. I ran it on a $0.67/hour GPU with OpenEverest and KServe, let it triage 299 real KServe issues and diagnose 19 broken pods, and published it on the Envoy AI Gateway with API keys and token quotas. Here is what it got right, what it got confidently wrong, and the prompt fix that made things worse."
---

Watch an AI agent work for a while and count what it actually does. Very little of it is writing essays. Most of it is small decisions: is this a bug or a question, which team owns it, is this pod healthy, is it safe to retry, should I page someone. Hundreds of them, each blocking the next step.

Today we mostly make those decisions with a chat model. We write a prompt, ask for JSON, parse the text, hope the label is one of ours, and wait a second or two for each answer. It works, but it is a strange fit. It's like asking a professor to write an essay every time you need a yes or a no.

Daniel Kahneman called the fast, intuitive part of the mind *System 1* and the slow, deliberate part *System 2*. Chat models are System 2. TypeSafe's [Jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev) or open-weight [OpenJev](https://huggingface.co/openjev/openjev) are attempts at System 1. Its API endpoint is literally called `/v1/systemone`.

I wanted to know three things:

1. Can I run it on a normal Kubernetes cluster, on a cheap GPU, as just another OpenEverest `Instance`?
2. Is it any good at the decisions a platform team actually makes?
3. Where does fast thinking go wrong?

Every script, manifest and raw result from this post is in [spron-in/blog-data/openjev-kserve-openeverest](https://github.com/spron-in/blog-data/tree/main/openjev-kserve-openeverest).

## What a decision model is

You send OpenJev a *state* (any text: an issue, a log, a ticket) and a map of *questions*. Each question has a type and your own labels:

* `choice`: pick one of up to 52 options
* `noul`: yes or no, as a probability
* `score`: a position on an ordered scale

Here is the first request I sent to my cluster, straight from the model card:

```json
{
  "state": "Customer message: I was charged twice for my order last week and nobody has replied.",
  "questions": {
    "route":   {"type": "choice", "instructions": "Which team should handle this?",
                "criteria": {"billing": null, "shipping": null, "technical": null}},
    "angry":   {"type": "noul",   "instructions": "Is the customer angry?"},
    "urgency": {"type": "score",  "instructions": "How urgent is this?",
                "criteria": ["can wait", "this week", "today", "right now"]}
  }
}
```

And the answer, with nothing to parse:

<div class="oj-box oj-hero"><div class="oj-hero-col"><div class="oj-q">route <span>choice</span></div><div class="oj-bar-row"><span class="oj-bar-k">billing</span><span class="oj-track"><span class="oj-fill" style="width:99.65%"></span></span><span class="oj-bar-v">0.997</span></div><div class="oj-bar-row"><span class="oj-bar-k">shipping</span><span class="oj-track"><span class="oj-fill oj-dim" style="width:1%"></span></span><span class="oj-bar-v">0.002</span></div><div class="oj-bar-row"><span class="oj-bar-k">technical</span><span class="oj-track"><span class="oj-fill oj-dim" style="width:1%"></span></span><span class="oj-bar-v">0.001</span></div></div><div class="oj-hero-col"><div class="oj-q">angry <span>noul</span></div><div class="oj-bar-row"><span class="oj-bar-k">yes</span><span class="oj-track"><span class="oj-fill oj-amber" style="width:76.8%"></span></span><span class="oj-bar-v">0.77</span></div><div class="oj-q" style="margin-top:14px">urgency <span>score = 1.82</span></div><div class="oj-bar-row"><span class="oj-bar-k">can wait</span><span class="oj-track"><span class="oj-fill oj-dim" style="width:6%"></span></span><span class="oj-bar-v">0.06</span></div><div class="oj-bar-row"><span class="oj-bar-k">this week</span><span class="oj-track"><span class="oj-fill oj-dim" style="width:29%"></span></span><span class="oj-bar-v">0.29</span></div><div class="oj-bar-row"><span class="oj-bar-k">today</span><span class="oj-track"><span class="oj-fill" style="width:41.5%"></span></span><span class="oj-bar-v">0.42</span></div><div class="oj-bar-row"><span class="oj-bar-k">right now</span><span class="oj-track"><span class="oj-fill oj-dim" style="width:23%"></span></span><span class="oj-bar-v">0.23</span></div></div></div>

The trick is simple. A language model scores every possible next token before it writes anything. OpenJev gives each of your options a letter, asks the question, and reads the scores of exactly those letters at the first output position. One forward pass, one number per option, and a fixed calibration step turns the numbers into probabilities. The model never generates text, so there is no JSON to break and no long answer to wait for. It was fine-tuned so that this one position carries the decision, and so that shuffling the options rarely changes the answer.

The labels live in the request. A new task is new JSON, not a new model.

## The setup

* Managed Kubernetes 1.36: three 8-vCPU nodes and *one GPU node with an NVIDIA RTX 4000 Ada (20 GB)*, which costs *$0.67 per hour*
* OpenEverest v2.0.0-dev.4
* [`provider-kserve`](https://github.com/openeverest/provider-kserve) 0.4.2, which bundles KServe 0.21, and 0.4.3 for the [AI Gateway part](#opening-the-door-decisions-on-the-envoy-ai-gateway)
* vLLM 0.29.0, the version the OpenJev authors pin
* *OpenJev Flash 9B in FP8*

Why the 9B model? The OpenJev family has a 27B model and a 9B "Flash" model built on Qwen3.5-9B. The 27B needs 29 GB even in FP8, and my card has 20. The 9B in FP8 is 11.9 GB. On the authors' 10,000-question test set it scores 79.4% against 84.1% for the 27B, so it's a bit less accurate. The client code is the same for both, so you can move up later without touching it.

### One Instance, two containers

OpenJev ships in two parts: the model, served by vLLM, and a small Python helper (`shim.py`) that turns `/v1/systemone` requests into letter readouts against vLLM. They have to sit next to each other: the helper calls vLLM on every question.

`provider-kserve` [recently learned](https://github.com/openeverest/provider-kserve/releases/tag/v0.4.0) to serve any container image, and to run a helper container next to it. A container named `transformer-container` gets the Service traffic and reaches the model server over `localhost`. That is exactly the shape OpenJev needs:

<div class="oj-arch"><div class="oj-arch-client">GitHub Action / agent / laptop<br><code>POST /typesafe/v1/systemone</code><br><small>the Instance's API key</small></div><div class="oj-arch-arrow">→</div><div class="oj-arch-gw">Envoy AI Gateway<br><small>TLS · API key · token quota</small></div><div class="oj-arch-arrow">→</div><div class="oj-arch-svc">Service<br><code>openjev-predictor:80</code><br><small>in-cluster callers start here</small></div><div class="oj-arch-arrow">→</div><div class="oj-arch-pod"><div class="oj-arch-title">Pod <small>Instance <code>openjev</code> → InferenceService</small></div><div class="oj-arch-c oj-arch-shim"><b>transformer-container</b> :3000<br>OpenJev helper, <code>shim.py</code><br><small>sha256 pinned, requires its own key</small></div><div class="oj-arch-local">localhost:8080 ↓</div><div class="oj-arch-c oj-arch-vllm"><b>kserve-container</b> :8080<br>vLLM 0.29 · OpenJev Flash 9B FP8<br><small>1 × RTX 4000 Ada · HF cache on a PVC</small></div><div class="oj-arch-np">NetworkPolicy: only :3000 is reachable from other pods</div></div></div>

The whole thing is one `Instance`. Trimmed:

```yaml
apiVersion: core.openeverest.io/v1alpha1
kind: Instance
metadata:
  name: openjev
  namespace: decisions
spec:
  providerRef:
    name: provider-kserve
  topology:
    type: predictor
    parameters:
      externalAccess: EnvoyAIGateway      # publish it on the shared AI Gateway
  components:
    predictor:
      type: modelServer
      resources:
        limits: {cpu: "5", memory: 20Gi}
      parameters:
        image: vllm/vllm-openai:v0.29.0
        command: [vllm, serve]
        args:
          - openjev/OpenJev-Flash-9B-FP8
          - --served-model-name=qwen        # the helper calls the model by this name
          - --max-logprobs=64               # it reads up to 52 option scores
          - --enable-prefix-caching
          - --port=8080
          # ... the rest of the flags from the model card
        port: 8080
        healthPath: /health
        gpuCount: 1
        apiSchema: TypeSafe                 # the helper serves /v1/systemone
        backendAPIKeySecret: openjev-shim   # the Gateway's key for the helper
        config: |
          predictor:
            containers:
              - name: transformer-container
                image: vllm/vllm-openai:v0.29.0   # already has python, openai, transformers
                command: [sh, -c]
                args:
                  - |
                    # download helper/shim.py at a pinned revision, check its sha256, run it
                    exec python3 /tmp/shim.py --host 0.0.0.0 --port 3000
                ports: [{containerPort: 3000}]
                env:
                  - {name: VLLM, value: "http://127.0.0.1:8080/v1"}
                  - {name: READOUT_T, value: "1.07"}          # the 9B calibration
                  - {name: READOUT_NOUL_T, value: "1.074766"}
                  - name: SHIM_TOKEN
                    valueFrom: {secretKeyRef: {name: openjev-shim, key: apiKey}}
```

The full manifest is [openjev.yaml](https://github.com/spron-in/blog-data/blob/main/openjev-kserve-openeverest/manifests/openjev.yaml). The three gateway lines get [their own section](#opening-the-door-decisions-on-the-envoy-ai-gateway) below. A few other things in it are worth knowing.

**The helper reuses the vLLM image.** It already has Python, `openai` and `transformers`, and the node has already pulled it. So there's no image to build and push, and no pulling a second 8.7 GB image.

**The helper is pinned by hash.** It is downloaded from the model repository at a fixed revision, and the container refuses to start if its sha256 isn't the one the authors publish. The calibration numbers only hold for that exact file.

**vLLM is not exposed.** vLLM has no authentication. It has to listen on the pod IP for the readiness probe, so before I added a NetworkPolicy any pod in the cluster could call it directly. I checked: `200`. With a [three-line NetworkPolicy](https://github.com/spron-in/blog-data/blob/main/openjev-kserve-openeverest/manifests/networkpolicy.yaml) that only allows port 3000, the same request times out, and the helper still answers. Probes come from the node and keep working. Do this before you hand the endpoint to anyone.

**The weights live on a PVC,** so a restarted pod doesn't download 12 GB again.

Then:

```bash
kubectl apply -f manifests/namespace.yaml
kubectl -n decisions create secret generic openjev-shim --from-literal=apiKey="$(openssl rand -hex 24)"
kubectl apply -f manifests/openjev.yaml -f manifests/networkpolicy.yaml
```

From `apply` to the first answer took **5 minutes 51 seconds**:

<div class="oj-box"><div class="oj-timeline"><span style="flex:28" class="oj-t0" title="Attach the PVC">28 s</span><span style="flex:96" class="oj-t1" title="Pull vllm/vllm-openai:v0.29.0, 8.7 GB">pull image · 1m36s</span><span style="flex:95" class="oj-t2" title="Download 11.9 GB of weights, load them in 34 s">weights · 1m35s</span><span style="flex:131" class="oj-t3" title="Profile, KV cache, torch.compile, CUDA graphs, API server">engine init · 2m11s</span></div><div class="oj-legend-row"><span>volume</span><span>8.7 GB image</span><span>11.9 GB from Hugging Face</span><span>compile, KV cache, CUDA graphs</span></div></div>

The GPU ends up with 11.4 GiB of weights and 4.2 GiB of KV cache: room for 112,000 tokens. One thing in the vLLM log is worth knowing if you use Ada-generation cards:

```text
Your GPU does not have native support for FP8 computation but FP8 quantization is being used.
Weight-only FP8 compression will be used leveraging the Marlin kernel.
```

The RTX 4000 Ada can do FP8 math, but vLLM's kernels for this block-quantized checkpoint need Hopper or newer. So the weights are stored in FP8 and the math runs in 16-bit. It fits and it works. It's just not as fast as on an H100.

## How fast is System 1 on a small GPU?

Before trusting it with anything, I measured it from a pod inside the cluster. Each case below is one question per request, run one after another ([bench.py](https://github.com/spron-in/blog-data/blob/main/openjev-kserve-openeverest/scripts/bench.py)).

<div class="oj-box"><div class="oj-row"><span class="oj-label">Short text, 3 options <small>~70 tokens</small></span><span class="oj-track"><span class="oj-fill" style="width:4%"></span></span><span class="oj-val">67 ms</span></div><div class="oj-row"><span class="oj-label">1k-token state, new question, <b>cached</b></span><span class="oj-track"><span class="oj-fill" style="width:4.2%"></span></span><span class="oj-val">70 ms</span></div><div class="oj-row"><span class="oj-label">4k-token state, new question, <b>cached</b></span><span class="oj-track"><span class="oj-fill" style="width:12.4%"></span></span><span class="oj-val">204 ms</span></div><div class="oj-row"><span class="oj-label">1k-token state, first read</span><span class="oj-track"><span class="oj-fill oj-amber" style="width:28.5%"></span></span><span class="oj-val">471 ms</span></div><div class="oj-row"><span class="oj-label">4k-token state, first read</span><span class="oj-track"><span class="oj-fill oj-red" style="width:100%"></span></span><span class="oj-val">1,653 ms</span></div><div class="oj-note">Median of 20 to 50 requests. The model card reports about 40 ms for a short decision on an H100.</div></div>

Two things stand out.

**Reading is expensive, asking is cheap.** The first read of a 4k-token page costs 1.6 seconds. Every question after that, about the same page, costs 0.2 seconds, because vLLM's prefix cache already holds the page. Throughput showed the same thing: for fresh 1k-token states it stayed between *2.1 and 2.4 decisions per second* whether I sent 1, 4, 8 or 16 requests in parallel. The GPU is busy reading, not deciding.

**So ask many questions per state.** One request can carry many questions about the same state. Here is a fresh 1k-token state with more and more questions:

<div class="oj-box"><div class="oj-row"><span class="oj-label">1 question</span><span class="oj-track"><span class="oj-fill" style="width:23%"></span></span><span class="oj-val">437 ms</span></div><div class="oj-row"><span class="oj-label">4 questions</span><span class="oj-track"><span class="oj-fill" style="width:31.6%"></span></span><span class="oj-val">596 ms</span></div><div class="oj-row"><span class="oj-label">8 questions</span><span class="oj-track"><span class="oj-fill" style="width:67%"></span></span><span class="oj-val">1,266 ms</span></div><div class="oj-row"><span class="oj-label">16 questions</span><span class="oj-track"><span class="oj-fill" style="width:100%"></span></span><span class="oj-val">1,889 ms</span></div><div class="oj-note">Four questions cost 1.4 times one question, not 4 times.</div></div>

In money, at $0.67 per hour: short decisions run back to back cost about *1.3 cents per 1,000*. Decisions that need a fresh 1k-token read cost about *8 cents per 1,000*. That's cheap enough to call on every event, in a loop, without thinking about it. Which is the whole point of System 1.

## Experiment 1: triaging 299 real KServe issues

I took real, closed issues from [kserve/kserve](https://github.com/kserve/kserve). KServe maintainers label every issue `kind/bug`, `kind/feature` or `kind/question`, so there is a ground truth. I sampled 100 bugs, 100 features and 99 questions.

There was a catch. KServe's issue templates write `/kind bug` into the body and add headings like *"What steps did you take and what happened"*. Leave those in and any model gets the answer for free. So [prepare_issues.py](https://github.com/spron-in/blog-data/blob/main/openjev-kserve-openeverest/scripts/prepare_issues.py) removes `/kind` lines, template headings, bracketed hints and empty environment fields, then checks that none are left. What remains is what people actually wrote.

Each issue gets four questions in *one* request: the kind (scored against the label), the area of KServe, whether a maintainer would need to ask for more information, and a priority from "nice to have" to "critical".

### Be the triager

Before the numbers, try it yourself. Read the issue, pick a label, then see what OpenJev and the maintainers said.

<div class="oj-box" id="oj-quiz"><noscript>This quiz needs JavaScript.</noscript></div>

### The score

OpenJev matched the maintainers' label on *237 of 299 issues: 79.3%*, with no examples and no training. Where it disagreed:

<div class="oj-table"><table><thead><tr><th>label ↓ / OpenJev →</th><th>bug</th><th>feature</th><th>question</th><th>recall</th></tr></thead><tbody><tr><td>bug</td><td class="oj-diag">72</td><td>9</td><td>19</td><td>72%</td></tr><tr><td>feature</td><td>4</td><td class="oj-diag">85</td><td>11</td><td>85%</td></tr><tr><td>question</td><td>14</td><td>5</td><td class="oj-diag">80</td><td>81%</td></tr></tbody></table></div>

Almost all of the confusion is bug vs question. That is also where humans argue: is "I can't get X working" a defect in KServe or a problem with your setup?

A triage bot doesn't have to label everything. The probabilities let you choose: label automatically when OpenJev is confident, and leave the rest for a person. Move the slider:

<div class="oj-box" id="oj-thr"><noscript>This chart needs JavaScript.</noscript></div>

At 0.90, the bot labels *53%* of the issues on its own at *91%* accuracy. The other 47% go to a human, as they would anyway. That trade-off is the reason to want probabilities instead of a JSON string from a chat model.

Are the probabilities honest? Mostly. When OpenJev said 0.90 or more, it was right 91% of the time, against an average stated 96%. In the middle it is overconfident: answers given at 0.8 to 0.9 were right 74% of the time. The expected calibration error is 0.08. Calibration was fitted on the authors' data, not on GitHub issues, so pick your threshold from your own data. A few hundred labelled examples is enough.

### When the model "fails", read the label

Then I looked at the 14 issues where OpenJev disagreed with the label *with 90% or more confidence*, the worst-looking errors. I reread every one. It's a judgement call, but this is how they came out:

<div class="oj-verdicts"><div class="oj-verdict oj-v-model"><b>8</b><span>OpenJev reads it better</span></div><div class="oj-verdict oj-v-amb"><b>6</b><span>genuinely ambiguous</span></div><div class="oj-verdict oj-v-label"><b>0</b><span>the label is clearly right</span></div></div>

<details class="oj-details"><summary>See the 14 issues</summary><ul><li><a href="https://github.com/kserve/kserve/issues/3763">#3763</a> <i>Can't find version compatibility matrix</i>. Label <code>bug</code>, OpenJev <code>question</code> 0.99. It ends with "Please help!".</li><li><a href="https://github.com/kserve/kserve/issues/3032">#3032</a> <i>GPU Metrics using Prometheus and Grafana</i>. Label <code>feature</code>, OpenJev <code>question</code> 0.99. "How can I scrape GPU metrics… Could anyone kindly help?"</li><li><a href="https://github.com/kserve/kserve/issues/2572">#2572</a> <i>How to health check model server with multiple pods</i>. Label <code>feature</code>, OpenJev <code>question</code> 0.98.</li><li><a href="https://github.com/kserve/kserve/issues/1474">#1474</a> <i>Latest ready inference service is showing the non-working update</i>. Label <code>question</code>, OpenJev <code>bug</code> 0.98. A crashing revision is reported as Ready.</li><li><a href="https://github.com/kserve/kserve/issues/2119">#2119</a> <i>Unable to delete inferenceservice</i>. Label <code>question</code>, OpenJev <code>bug</code> 0.97.</li><li><a href="https://github.com/kserve/kserve/issues/1645">#1645</a> <i>Does KFServing support inferencing about the entire dataset?</i> Label <code>feature</code>, OpenJev <code>question</code> 0.96.</li><li><a href="https://github.com/kserve/kserve/issues/2276">#2276</a> <i>Deployments managed by InferenceService are not updating status at all!</i> Label <code>question</code>, OpenJev <code>bug</code> 0.96.</li><li><a href="https://github.com/kserve/kserve/issues/2554">#2554</a> <i>Does KServe not support using pvc in custom images?</i> Label <code>bug</code>, OpenJev <code>question</code> 0.90.</li><li class="oj-amb-li"><a href="https://github.com/kserve/kserve/issues/2667">#2667</a> pip install fails inside Kubeflow. Label <code>bug</code>, OpenJev <code>question</code> 0.95. Could be either.</li><li class="oj-amb-li"><a href="https://github.com/kserve/kserve/issues/3148">#3148</a> Upgrade openapi-generator. Label <code>bug</code>, OpenJev <code>feature</code> 0.94. A chore.</li><li class="oj-amb-li"><a href="https://github.com/kserve/kserve/issues/1606">#1606</a> .pkl files not supported in the v2 sklearn server. Label <code>feature</code>, OpenJev <code>bug</code> 0.93.</li><li class="oj-amb-li"><a href="https://github.com/kserve/kserve/issues/3554">#3554</a> "Add ability to InferenceGraph…" with a body that reports a bug. Label <code>bug</code>, OpenJev <code>feature</code> 0.92.</li><li class="oj-amb-li"><a href="https://github.com/kserve/kserve/issues/3784">#3784</a> Bump vLLM to support new models. Label <code>bug</code>, OpenJev <code>feature</code> 0.91.</li><li class="oj-amb-li"><a href="https://github.com/kserve/kserve/issues/2770">#2770</a> Throughput lower than plain Triton. Label <code>question</code>, OpenJev <code>bug</code> 0.91.</li></ul></details>

Labels are written by tired people picking a template at 2 a.m. A confident disagreement is often a free label audit.

### The tempting fix that made it worse

Since the criteria live in the request, the obvious next step is to improve them. So I did what everyone does: I read the misses and rewrote the descriptions.

To keep myself honest, I split the data first. I only looked at the misses in the first 99 issues (the *dev* set) and wrote v2 from those. The misses showed a convention in the KServe repo: dependency bumps and deprecations are filed as bugs, and trouble with your own install is a question. v2 wrote that down. I also tried v0, the bare labels with no descriptions at all. Then I ran all three on every issue:

<div class="oj-table"><table><thead><tr><th>criteria</th><th>dev (99)</th><th>held-out test (200)</th></tr></thead><tbody><tr><td><b>v0</b>: labels only, <code>{"bug": null, …}</code></td><td>78.8%</td><td>75.0%</td></tr><tr><td><b>v1</b>: one plain sentence per label</td><td>81.8%</td><td><b>78.0%</b></td></tr><tr><td><b>v2</b>: v1 plus the conventions from the dev misses</td><td><b>83.8%</b></td><td class="oj-bad">73.5%</td></tr></tbody></table></div>

Descriptions help: +3 points over bare labels. But v2, which looked better on the issues I had studied, *lost 4.5 points on the ones I hadn't*. The longer, cleverer criteria fixed the cases I was looking at and moved others the wrong way. With a chat model and no held-out set, I would have shipped v2 and felt good about it.

Labels in the request are powerful, and they are code. Version them, and test every change on examples you didn't write it for.

## Experiment 2: on call for broken pods

GitHub triage is a nice demo. The decisions a platform team makes at 3 a.m. are another matter. So I broke things on purpose.

I deployed 12 small workloads into an `incidents` namespace ([incidents.yaml](https://github.com/spron-in/blog-data/blob/main/openjev-kserve-openeverest/manifests/incidents.yaml)), each broken in one known way: out of memory, an image that doesn't exist, a missing ConfigMap, a database that's down, four GPUs on a one-GPU cluster, a probe on the wrong port, a PVC on a StorageClass that doesn't exist, an entrypoint that isn't in the image, and so on. Plus one healthy nginx as a control. The real cause is on a Deployment label that never reaches the model.

For each pod, [incident_triage.py](https://github.com/spron-in/blog-data/blob/main/openjev-kserve-openeverest/scripts/incident_triage.py) builds the state an on-call engineer would look at first: the real `kubectl describe pod` output and the last log lines. Then it asks five questions in one request: the root cause (9 options), who has to act, whether a restart would fix it, whether to page someone now, and how bad it is for users.

The first run got *11 of 12* right. The one miss was the most interesting result of the whole experiment: the *healthy* pod was called `bad-probe`, with 94% confidence.

Here is what it saw, at the end of `kubectl describe`:

```text
    Ready:          True
    Restart Count:  0
...
  Normal   Started    3m11s  kubelet  Container started
  Warning  Unhealthy  3m11s  kubelet  Readiness probe failed: Get "http://10.2.1.10:80/":
                                      dial tcp 10.2.1.10:80: connect: connection refused
```

nginx hadn't bound its port yet when the first readiness probe fired. It happens to a lot of healthy pods. Any SRE skims past it: Ready, zero restarts, an old warning from startup. OpenJev saw a red `Warning Unhealthy` and jumped. That is System 1 exactly: quick, usually right, and fooled by one scary-looking line.

I wrote the SRE's rule of thumb into the question (v2): *judge the pod by its current state, not by one-off events from container start-up*. Having just learned my lesson about overfitting, I didn't trust it. So I wrote *7 more broken workloads I hadn't seen* ([incidents-heldout.yaml](https://github.com/spron-in/blog-data/blob/main/openjev-kserve-openeverest/manifests/incidents-heldout.yaml)): two more healthy services, a missing Secret, a slow memory leak, a private-registry image, a Kafka consumer that can't resolve its broker, and a pod asking for 24 CPUs. Then I ran both versions on all 19.

Switch between v1 and v2, and click a card for details:

<div class="oj-box" id="oj-inc"><noscript>This board needs JavaScript.</noscript></div>

v1 scored **17 of 19**. The new healthy `api-gateway` failed in exactly the same way as `web-frontend`, so this is a pattern, not bad luck. v2 got **19 of 19**, held-out cases included.

Look at the confidence, though. With v2 the two pods with a startup blip are called healthy at only *0.51* and *0.63*. The healthy Redis, which had no blip, gets 0.96. With a threshold of 0.8, an agent would send those two to a human. That is the right outcome: the evidence really is mixed, and the model says so.

The side questions held up too. "Would restarting the pod fix it?" stayed below 0.5 for every incident, and it's right: none of these failures is fixed by a restart. Scheduling and storage went to the platform team, and so did the Kafka consumer that can't find its broker, which is fair: someone has to fix the broker. Everything else went to the app team. Each pod took 0.9 to 2.2 seconds for all five questions (median about 1.5), with states of 500 to 2,600 tokens, measured from my laptop through a port-forward.

## Experiment 3: a triage bot for our own repository

The last test is the one I want to keep running. OpenEverest has a `needs-triage` label and, like most projects, a set of labels with descriptions someone wrote years ago:

```text
bug            Something isn't working
enhancement    New feature or request
question       Further information is requested
chore          For tasks that don't affect the end-user directly.
provider       Provider - representation of new database, storage or AI tech
ops            Various operations related tasks - devops, SRE, observability, etc
```

Those descriptions *are* the criteria. [triage_bot.py](https://github.com/spron-in/blog-data/blob/main/openjev-kserve-openeverest/scripts/triage_bot.py) reads the label list from GitHub, turns it into OpenJev questions without any prompt writing, and only applies a label when OpenJev is at least 85% sure. I ran it in dry-run mode on the 30 newest `needs-triage` issues in [openeverest/openeverest](https://github.com/openeverest/openeverest/issues):

<div class="oj-table"><table><thead><tr><th>issue</th><th>kind</th><th>area</th><th>bot would add</th></tr></thead><tbody><tr><td>#3400 provider-runtime reconciles (and finalizes) Instances of other providers</td><td>bug 0.97</td><td>provider 0.96</td><td><code>bug</code> <code>provider</code></td></tr><tr><td>#3399 [UI] Import a database from an external backup</td><td>enhancement 0.90</td><td>ui 0.94</td><td><code>enhancement</code> <code>ui</code></td></tr><tr><td>#3292 [Chore] Add unit test suite for pkg/version_service/client</td><td>chore 0.96</td><td>database 0.32</td><td><code>chore</code></td></tr><tr><td>#3233 docs(ui-generator): broken CEL TOC anchor</td><td>documentation 0.94</td><td>ui 0.93</td><td><code>documentation</code> <code>ui</code></td></tr><tr><td>#3364 UI: filter or warn when schedule time retention is unsupported</td><td>enhancement 0.78</td><td>ui 0.74</td><td><i>left for a human</i></td></tr><tr><td>#3284 provider-runtime: remove pruneEmptyStructs once SMD#305 is released</td><td>chore 0.74</td><td>provider 0.77</td><td><i>left for a human</i></td></tr></tbody></table></div>

Across the 30 issues, the kind was confident enough to apply on 26 and the area on only 11. No issue was flagged as needing more information from the reporter. That's how it should be: areas overlap and the label descriptions are vague, so the bot leaves those to a human. It took 0.4 to 1.1 seconds per issue.

To run it for real, start in dry-run mode, compare with what maintainers do for a couple of weeks, then pick the threshold. And it should run where issues happen: in a GitHub Action, not on my laptop. That means the decision API has to leave the cluster.

## Opening the door: decisions on the Envoy AI Gateway

Leaving the cluster means TLS, a key for each consumer, and a cap on what each key can spend. `provider-kserve` already does all of that for OpenAI-style models through the shared [Envoy AI Gateway](https://github.com/openeverest/provider-kserve#envoy-ai-gateway). The question was whether it could do the same for an API that isn't OpenAI's.

It turned out the hard part was already done. Envoy AI Gateway 1.2 understands the TypeSafe System One API natively: it routes `/typesafe/v1/systemone`, reads `model` from the body, and meters `usage.input_tokens`. The only gap was in the provider, which knew just one schema. So I [added a second one](https://github.com/openeverest/provider-kserve/pull/106), released in `provider-kserve` 0.4.3. On the Instance it's three lines:

```yaml
spec:
  topology:
    parameters:
      externalAccess: EnvoyAIGateway
  components:
    predictor:
      parameters:
        apiSchema: TypeSafe                 # the API the image serves
        backendAPIKeySecret: openjev-shim   # the Gateway's key for the helper
```

The provider creates the route, an `AIServiceBackend` with the `TypeSafe` schema, and a key for the Instance. The Instance's connection Secret switches to the public address:

```text
uri:      https://104-105-24-24.ip.linodeusercontent.com/typesafe
model:    openjev
username: k_zzy7qn3agi44rkn6      # key ID
password: <the API key>
```

There are two keys in play. The client's key is for the Gateway; the Gateway checks it and removes it before forwarding. The helper has its own key (`SHIM_TOKEN`), so nobody can skip the Gateway by calling the helper inside the cluster. `backendAPIKeySecret` is how the Gateway gets that second key. Click through what happens to one request:

<div class="oj-steps"><input type="radio" name="oj-g" id="oj-g1" checked><input type="radio" name="oj-g" id="oj-g2"><input type="radio" name="oj-g" id="oj-g3"><input type="radio" name="oj-g" id="oj-g4"><input type="radio" name="oj-g" id="oj-g5"><input type="radio" name="oj-g" id="oj-g6"><div class="oj-stepbar"><label for="oj-g1" data-step="1">1 · send</label><label for="oj-g2" data-step="2">2 · key</label><label for="oj-g3" data-step="3">3 · model</label><label for="oj-g4" data-step="4">4 · quota</label><label for="oj-g5" data-step="5">5 · helper</label><label for="oj-g6" data-step="6">6 · meter</label></div><div class="oj-step" data-step="1"><p class="oj-out">client → <code>POST https://…/typesafe/v1/systemone</code></p><p>The client sends the decision with <code>"model": "openjev"</code> and <code>Authorization: Bearer &lt;the Instance's API key&gt;</code>, over TLS to the Gateway's LoadBalancer.</p></div><div class="oj-step" data-step="2"><p class="oj-out">no key or an unknown key → <b class="oj-bad">401</b></p><p>Envoy checks the key against every Instance key, which the provider renders into one <code>SecurityPolicy</code> on the shared Gateway. It strips any client-supplied key ID header and sets its own.</p></div><div class="oj-step" data-step="3"><p class="oj-out">a valid key for another model → <b class="oj-bad">403</b></p><p>The AI Gateway reads <code>model</code> from the body, and the key may only call the model it was issued for. A key for an embedding model can't spend decisions, and the other way around.</p></div><div class="oj-step" data-step="4"><p class="oj-out">budget used up → <b class="oj-bad">429</b></p><p>With a rate-limit backend (here, a small Valkey), the key's hourly token budget for this model is checked before the request goes on.</p></div><div class="oj-step" data-step="5"><p class="oj-out">Gateway → <code>POST http://openjev-predictor/v1/systemone</code> → <b class="oj-good">200</b></p><p>The client's key is removed. The <code>BackendSecurityPolicy</code> adds the helper's own key, and the request reaches the helper on <code>/v1/systemone</code>. Without that policy the helper answers 401. I checked by removing it.</p></div><div class="oj-step" data-step="6"><p class="oj-out"><code>usage.input_tokens: 239</code> → charged to the key</p><p>On the way back, the Gateway records the tokens per key and model in its metrics, and charges them against the key's quota.</p></div></div>

Then I ran the [checks](https://github.com/spron-in/blog-data/blob/main/openjev-kserve-openeverest/scripts/gateway_e2e.sh) from my laptop, over the internet, using nothing but the connection Secret:

```text
$ ./scripts/gateway_e2e.sh
gateway: https://104-105-24-24.ip.linodeusercontent.com/typesafe (via 104.105.24.24:443), model: openjev
no API key                -> 401 (want 401)
key for another model     -> 403 (want 403)
valid key                 -> 200 in 1.007773s (want 200)
  route  : billing {'billing': 0.9965, 'shipping': 0.0024, 'technical': 0.0011}
  angry  : 0.7866
  urgency: 1.7767 {'0': 0.0651, '1': 0.315, '2': 0.398, '3': 0.2219}
  usage  : {'input_tokens': 239, 'output_tokens': 0}
```

Then I gave the key a budget of 600 tokens per hour ([gateway_quota.sh](https://github.com/spron-in/blog-data/blob/main/openjev-kserve-openeverest/scripts/gateway_quota.sh)):

```text
tokenLimitPerHour=600
request 1 -> 200 (tokens charged so far: 239)
request 2 -> 200 (tokens charged so far: 478)
request 3 -> 200 (tokens charged so far: 717)
request 4 -> 429 (tokens charged so far: 717)
```

The request that crosses the limit still goes through, because tokens are charged after the answer. Every one of them shows up in the Gateway's metrics, labelled with the key:

```text
gen_ai_client_token_usage_sum{gen_ai_operation_name="systemone", gen_ai_provider_name="typesafe",
  gen_ai_request_model="openjev", gen_ai_token_type="input", openeverest_key_id="k_zzy7qn3agi44rkn6"} 478
```

And the cost of all this, measured from inside the cluster with short decisions: *68 ms* direct to the helper, *72 ms* through the Gateway, TLS included. Four milliseconds for keys, quotas and metering is a good deal. The triage bot can now run in a GitHub Action with one secret, its own budget, and nothing else exposed.

## What I'd tell a platform team

* **Use it as System 1, not instead of System 2.** OpenJev is great at "pick one of these" on every event, in a loop. When it isn't sure, hand the case to a bigger model or a human. The probability tells you when.
* **Treat criteria like code.** Keep them in Git, keep a held-out set, and run it on every change. My "improved" criteria lost 4.5 points, and I only noticed because I had a held-out set.
* **Ask many questions about one state.** On this GPU, reading 1,000 tokens takes 470 ms and each extra question about them about 70 ms.
* **Watch out for scary-looking lines.** Logs and events are full of warnings that don't matter. Say in the question what counts: the current state, not history.
* **Check the license.** The weights are *CC BY-NC 4.0*, free for research and non-commercial use. For commercial use, the authors offer a commercial license. The helper and serving files are Apache 2.0.
* **Put the Gateway in front, keep vLLM private.** Outside callers go through the Envoy AI Gateway with their own key and budget. Inside, a NetworkPolicy hides vLLM, and the helper requires its own key, so the Gateway can't be bypassed. Pin the helper hash.

## Rough edges

<details class="oj-card"><summary><span class="oj-badge">OpenEverest</span> The Instance said Ready six minutes too early</summary><p>Twenty seconds after <code>kubectl apply</code>, both the Instance phase and the InferenceService showed <code>Ready</code>, while the pod was still pulling an 8.7 GB image. The Instance's <code>PodsReady</code> condition was correct the whole time. If you automate on top of it, wait for <code>PodsReady</code> or for the pod itself. It's on our list.</p></details>

<details class="oj-card"><summary><span class="oj-badge">Hardware</span> Ada GPUs run FP8 as weight-only</summary><p>On an RTX 4000 Ada, vLLM uses the Marlin weight-only FP8 path for this checkpoint. Accuracy is the same, but the math runs at 16-bit speed. If you need lower latency on long states, a Hopper-class GPU is the upgrade. Per decision, the small card is already cheap.</p></details>

<details class="oj-card"><summary><span class="oj-badge">Air-gapped</span> The helper downloads itself at start</summary><p>The helper container fetches <code>shim.py</code> and the tokenizer from Hugging Face. That's fine with egress. In an air-gapped cluster, build a small image with both baked in and point <code>transformer-container</code> at it. Nothing else changes.</p></details>

## What's next

Two things I want to build on top of this. The first is duplicate detection: [Milvus on OpenEverest](/blog/milvus-on-openeverest/) finds the five most similar old issues, and OpenJev decides which one, if any, is the same problem. Retrieval is good at "similar". A decision model is good at "same". The second is a remediation loop for the incident namespace: OpenJev decides, a human approves above one threshold, the agent acts on its own above a higher one, and every decision is logged so it can be audited later.

If you try OpenJev or another decision model on OpenEverest, I'd love to hear what you used it for.

## Try It Yourself

* **Everything from this post:** manifests, scripts and raw results in [spron-in/blog-data/openjev-kserve-openeverest](https://github.com/spron-in/blog-data/tree/main/openjev-kserve-openeverest).
* **Install:** Follow the [quick install guide](https://openeverest.io/documentation/2.0.0-dev.4/quick-install.html) to get OpenEverest v2 running, then add [`provider-kserve`](https://github.com/openeverest/provider-kserve).
* **KServe on OpenEverest:** [what you can serve and how](/for/kserve/), and the [decision model example](https://github.com/openeverest/provider-kserve/blob/main/examples/instance-predictor-decision-model.yaml) with the AI Gateway.
* **OpenJev:** the [model card](https://huggingface.co/openjev/openjev) and the [Flash 9B card](https://huggingface.co/openjev/OpenJev-Flash-9B).
* **Chat:** Join the conversation in the CNCF Slack (channel: [#openeverest-users](https://cloud-native.slack.com/archives/C09RRGZL2UX)).

<div style="display:flex;gap:12px;margin:24px 0 40px;flex-wrap:wrap;">
  <a href="https://openeverest.io/documentation/2.0.0-dev.4/quick-install.html" target="_blank" rel="noopener noreferrer" style="display:inline-flex;align-items:center;gap:8px;background-color:#0aa66e;color:#fff;text-decoration:none;padding:10px 20px;border-radius:6px;font-weight:600;font-size:15px;">
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>
    Try OpenEverest
  </a>
  <a href="https://cloud-native.slack.com/archives/C09RRGZL2UX" target="_blank" rel="noopener noreferrer" style="display:inline-flex;align-items:center;gap:8px;background-color:#4A154B;color:#fff;text-decoration:none;padding:10px 20px;border-radius:6px;font-weight:600;font-size:15px;">
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 122.8 122.8"><path d="M25.8 77.6c0 7.1-5.8 12.9-12.9 12.9S0 84.7 0 77.6s5.8-12.9 12.9-12.9h12.9v12.9zm6.5 0c0-7.1 5.8-12.9 12.9-12.9s12.9 5.8 12.9 12.9v32.3c0 7.1-5.8 12.9-12.9 12.9s-12.9-5.8-12.9-12.9V77.6z" fill="#e01e5a"/><path d="M45.2 25.8c-7.1 0-12.9-5.8-12.9-12.9S38.1 0 45.2 0s12.9 5.8 12.9 12.9v12.9H45.2zm0 6.5c7.1 0 12.9 5.8 12.9 12.9s-5.8 12.9-12.9 12.9H12.9C5.8 58.1 0 52.3 0 45.2s5.8-12.9 12.9-12.9h32.3z" fill="#36c5f0"/><path d="M97 45.2c0-7.1 5.8-12.9 12.9-12.9s12.9 5.8 12.9 12.9-5.8 12.9-12.9 12.9H97V45.2zm-6.5 0c0 7.1-5.8 12.9-12.9 12.9s-12.9-5.8-12.9-12.9V12.9C64.7 5.8 70.5 0 77.6 0s12.9 5.8 12.9 12.9v32.3z" fill="#2eb67d"/><path d="M77.6 97c7.1 0 12.9 5.8 12.9 12.9s-5.8 12.9-12.9 12.9-12.9-5.8-12.9-12.9V97h12.9zm0-6.5c-7.1 0-12.9-5.8-12.9-12.9s5.8-12.9 12.9-12.9h32.3c7.1 0 12.9 5.8 12.9 12.9s-5.8 12.9-12.9 12.9H77.6z" fill="#ecb22e"/></svg>
    Join Slack
  </a>
  <a href="https://github.com/openeverest/provider-kserve" target="_blank" rel="noopener noreferrer" style="display:inline-flex;align-items:center;gap:8px;background-color:#24292f;color:#fff;text-decoration:none;padding:10px 20px;border-radius:6px;font-weight:600;font-size:15px;">
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 16 16" fill="#fff"><path d="M8 .25a7.75 7.75 0 1 0 0 15.5A7.75 7.75 0 0 0 8 .25zm0 1.5a6.25 6.25 0 0 1 1.97 12.18c-.31.06-.42-.13-.42-.3v-1.05c0-.36-.01-1.02-.49-1.4 1.62-.18 2.5-.88 2.5-2.57 0-.57-.2-1.1-.53-1.49.05-.14.23-.7-.05-1.47 0 0-.44-.14-1.44.54a5.02 5.02 0 0 0-2.62 0C5.93 6.6 5.49 6.74 5.49 6.74c-.28.77-.1 1.33-.05 1.47-.33.39-.53.92-.53 1.49 0 1.69.88 2.39 2.5 2.57-.31.27-.43.67-.47 1.04-.42.19-1.5.52-2.16-.62 0 0-.39-.71-1.13-.76 0 0-.72-.01-.05.45 0 0 .48.23.82 1.08 0 0 .43 1.32 2.49.87v.75c0 .17-.11.36-.42.3A6.25 6.25 0 0 1 8 1.75z"/></svg>
    Star the Provider
  </a>
</div>

<style>
.oj-box{margin:1.5rem 0;border:1px solid rgba(127,127,127,0.25);border-radius:12px;padding:16px 18px;}
.oj-hero{display:flex;flex-wrap:wrap;gap:12px 32px;}
.oj-hero-col{flex:1 1 260px;}
.oj-q{font-family:ui-monospace,Menlo,monospace;font-size:13px;font-weight:700;color:#0f172a;margin-bottom:6px;}
.oj-q span{font-weight:500;color:#6b7280;margin-left:6px;}
.oj-bar-row,.oj-row{display:flex;align-items:center;gap:10px;padding:3px 0;font-size:14px;}
.oj-bar-k{flex:0 0 140px;color:#374151;}
.oj-bar-k em{font-style:normal;font-size:11px;font-weight:700;color:#fff;background:#6366f1;border-radius:4px;padding:1px 5px;margin-left:4px;}
.oj-label{flex:0 0 280px;color:#374151;}
.oj-label small{color:#9ca3af;margin-left:4px;}
.oj-track{flex:1;height:14px;background:rgba(127,127,127,0.12);border-radius:7px;overflow:hidden;}
.oj-fill{display:block;height:100%;background:#0aa66e;border-radius:7px;min-width:3px;transition:width .25s ease;}
.oj-fill.oj-dim{background:#94a3b8;}
.oj-fill.oj-amber{background:#f59e0b;}
.oj-fill.oj-red{background:#dc2626;}
.oj-fill.oj-blue{background:#1a8cff;}
.oj-bar-v,.oj-val{flex:0 0 64px;text-align:right;font-variant-numeric:tabular-nums;font-weight:600;}
.oj-note{margin-top:10px;padding-top:8px;border-top:1px solid rgba(127,127,127,0.2);font-size:12px;color:#6b7280;}
.oj-arch{display:flex;flex-wrap:wrap;align-items:center;gap:10px;margin:1.5rem 0;font-size:13px;line-height:1.45;}
.oj-arch code{font-size:12px;}
.oj-arch-client,.oj-arch-svc{border:1px solid rgba(127,127,127,0.3);border-radius:10px;padding:10px 12px;background:#f8fafc;text-align:center;}
.oj-arch-arrow{font-size:22px;color:#9ca3af;}
.oj-arch-gw{border:1px solid #f59e0b;border-radius:10px;padding:10px 12px;background:#fff4e0;color:#92400e;text-align:center;font-weight:600;}
.oj-arch-gw small{font-weight:500;}
.oj-arch-svc small,.oj-arch-client small{color:#6b7280;}
.oj-arch-pod{flex:1 1 300px;border:2px dashed #6366f1;border-radius:12px;padding:10px 12px;}
.oj-arch-title{font-weight:700;color:#312e81;margin-bottom:8px;}
.oj-arch-title small{font-weight:500;color:#6b7280;}
.oj-arch-c{border-radius:8px;padding:8px 10px;}
.oj-arch-shim{background:#e8f7f0;border:1px solid #0aa66e;color:#065f46;}
.oj-arch-vllm{background:#eef0ff;border:1px solid #6366f1;color:#312e81;}
.oj-arch-local{text-align:center;color:#6b7280;font-size:12px;padding:4px 0;}
.oj-arch-np{margin-top:8px;font-size:12px;color:#b45309;}
.oj-timeline{display:flex;gap:3px;}
.oj-timeline span{display:flex;align-items:center;justify-content:center;height:40px;border-radius:6px;font-size:13px;font-weight:600;white-space:nowrap;overflow:hidden;}
.oj-t0{background:#e5e7eb;color:#374151;}
.oj-t1{background:#e8f2ff;color:#0b4f99;}
.oj-t2{background:#fff4e0;color:#92400e;}
.oj-t3{background:#eef0ff;color:#312e81;}
.oj-legend-row{display:flex;justify-content:space-between;gap:8px;margin-top:6px;font-size:12px;color:#6b7280;}
.oj-table{margin:1.5rem 0;overflow-x:auto;border:1px solid rgba(127,127,127,0.25);border-radius:12px;}
.oj-table table{width:100%;border-collapse:collapse;font-size:14px;margin:0;}
.oj-table th,.oj-table td{padding:9px 14px;text-align:left;border-bottom:1px solid rgba(127,127,127,0.18);}
.oj-table tr:last-child td{border-bottom:0;}
.oj-table th{background:rgba(127,127,127,0.06);font-weight:600;}
.oj-diag{background:#e8f7f0;font-weight:700;color:#065f46;}
.oj-bad{color:#b91c1c;font-weight:700;}
.oj-verdicts{display:flex;gap:12px;flex-wrap:wrap;margin:1.5rem 0 .75rem;}
.oj-verdict{flex:1 1 150px;border-radius:12px;padding:14px 16px;text-align:center;}
.oj-verdict b{display:block;font-size:34px;line-height:1.1;}
.oj-verdict span{font-size:13px;}
.oj-v-model{background:#e8f7f0;color:#065f46;}
.oj-v-amb{background:#fff4e0;color:#92400e;}
.oj-v-label{background:#f3f4f6;color:#374151;}
.oj-details{margin:0 0 1.5rem;border:1px solid rgba(127,127,127,0.25);border-radius:12px;padding:10px 16px;font-size:14px;}
.oj-details summary{cursor:pointer;font-weight:600;}
.oj-details li{margin:6px 0;}
.oj-details li.oj-amb-li{color:#6b7280;}
.oj-steps{margin:1.5rem 0;border:1px solid rgba(127,127,127,0.25);border-radius:12px;overflow:hidden;}
.oj-steps>input{position:absolute;opacity:0;pointer-events:none;}
.oj-stepbar{display:flex;flex-wrap:wrap;border-bottom:1px solid rgba(127,127,127,0.25);background:rgba(127,127,127,0.06);}
.oj-stepbar label{flex:1;white-space:nowrap;text-align:center;padding:11px 6px;font-size:14px;font-weight:600;color:#6b7280;cursor:pointer;user-select:none;border-bottom:2px solid transparent;}
.oj-stepbar label:hover{color:#0f172a;}
.oj-step{display:none;padding:14px 20px;font-size:15px;}
.oj-step p{margin:.45rem 0;}
.oj-out{font-family:ui-monospace,Menlo,monospace;font-size:13px;background:rgba(127,127,127,0.07);border-radius:6px;padding:6px 10px;}
.oj-good{color:#047857;font-weight:700;}
#oj-g1:checked~.oj-stepbar label[data-step="1"],#oj-g2:checked~.oj-stepbar label[data-step="2"],#oj-g3:checked~.oj-stepbar label[data-step="3"],
#oj-g4:checked~.oj-stepbar label[data-step="4"],#oj-g5:checked~.oj-stepbar label[data-step="5"],#oj-g6:checked~.oj-stepbar label[data-step="6"]{color:#0aa66e;border-bottom-color:#0aa66e;background:#fff;}
#oj-g1:checked~.oj-step[data-step="1"],#oj-g2:checked~.oj-step[data-step="2"],#oj-g3:checked~.oj-step[data-step="3"],
#oj-g4:checked~.oj-step[data-step="4"],#oj-g5:checked~.oj-step[data-step="5"],#oj-g6:checked~.oj-step[data-step="6"]{display:block;}
.oj-card{margin:10px 0;border:1px solid rgba(127,127,127,0.25);border-radius:12px;padding:10px 16px;font-size:15px;}
.oj-card summary{cursor:pointer;font-weight:600;}
.oj-card p{margin:.6rem 0 .3rem;}
.oj-badge{display:inline-block;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.04em;padding:2px 8px;border-radius:999px;background:#eef0ff;color:#312e81;margin-right:8px;}
.oj-btn{display:inline-block;border:1px solid rgba(127,127,127,0.35);background:#fff;border-radius:8px;padding:7px 14px;font-size:14px;font-weight:600;cursor:pointer;margin:4px 6px 4px 0;color:#0f172a;}
.oj-btn:hover{border-color:#0aa66e;color:#0aa66e;}
.oj-btn:disabled{cursor:default;opacity:.55;}
.oj-btn.oj-on{background:#0aa66e;border-color:#0aa66e;color:#fff;opacity:1;}
.oj-btn.oj-pick{background:#6366f1;border-color:#6366f1;color:#fff;opacity:1;}
.oj-quiz-meta{display:flex;justify-content:space-between;flex-wrap:wrap;gap:6px;font-size:12px;color:#6b7280;margin-bottom:8px;}
.oj-quiz-title{font-size:17px;font-weight:700;margin:2px 0 6px;color:#0f172a;}
.oj-quiz-text{font-size:14px;line-height:1.5;color:#374151;background:rgba(127,127,127,0.06);border-left:3px solid #cbd5e1;border-radius:4px;padding:8px 12px;margin:0 0 10px;}
.oj-reveal{margin-top:12px;padding-top:12px;border-top:1px solid rgba(127,127,127,0.2);}
.oj-reveal p{margin:.4rem 0;font-size:14px;}
.oj-side{display:flex;flex-wrap:wrap;gap:6px 18px;font-size:13px;color:#4b5563;margin-top:6px;}
.oj-comment{font-size:14px;background:#fff7ed;border-left:3px solid #f59e0b;border-radius:4px;padding:8px 12px;margin-top:10px;}
.oj-thr-head{display:flex;flex-wrap:wrap;gap:10px 24px;align-items:center;margin-bottom:10px;}
.oj-thr-head input{flex:1 1 220px;accent-color:#0aa66e;}
.oj-kpis{display:flex;flex-wrap:wrap;gap:10px;margin:10px 0;}
.oj-kpi{flex:1 1 140px;border-radius:10px;padding:10px 12px;background:rgba(127,127,127,0.06);}
.oj-kpi b{display:block;font-size:24px;font-variant-numeric:tabular-nums;}
.oj-kpi span{font-size:12px;color:#6b7280;}
.oj-strip{display:flex;flex-wrap:wrap;gap:2px;margin-top:8px;}
.oj-strip i{display:block;width:9px;height:14px;border-radius:2px;background:#d1d5db;}
.oj-strip i.ok{background:#0aa66e;}
.oj-strip i.bad{background:#dc2626;}
.oj-strip-legend{display:flex;flex-wrap:wrap;gap:6px 16px;margin-top:8px;font-size:12px;color:#4b5563;}
.oj-strip-legend i{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:6px;vertical-align:-1px;}
.oj-inc-head{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:8px;margin-bottom:10px;}
.oj-inc-score{font-size:14px;color:#374151;}
.oj-inc-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(175px,1fr));gap:8px;}
.oj-inc{border:1px solid rgba(127,127,127,0.3);border-left-width:4px;border-radius:8px;padding:8px 10px;font-size:13px;cursor:pointer;background:#fff;transition:box-shadow .15s;}
.oj-inc:hover{box-shadow:0 2px 8px rgba(0,0,0,.08);}
.oj-inc.ok{border-left-color:#0aa66e;}
.oj-inc.bad{border-left-color:#dc2626;background:#fef2f2;}
.oj-inc.unsure{border-left-color:#f59e0b;}
.oj-inc b{display:block;font-size:14px;color:#0f172a;}
.oj-inc .st{color:#6b7280;font-size:12px;}
.oj-inc .dx{margin-top:4px;font-family:ui-monospace,Menlo,monospace;font-size:12px;}
.oj-inc .ho{display:inline-block;font-size:10px;font-weight:700;color:#0b4f99;background:#e8f2ff;border-radius:4px;padding:0 5px;margin-left:4px;vertical-align:1px;}
.oj-inc-detail{grid-column:1/-1;border:1px solid rgba(127,127,127,0.25);border-radius:10px;padding:12px 14px;background:rgba(127,127,127,0.04);}
.oj-inc-detail h4{margin:0 0 6px;font-size:15px;}
</style>

<script>
(function () {
  var D = {"curve":[[0.8841,1],[0.9401,1],[0.9656,1],[0.9779,1],[0.9877,1],[0.8819,1],[0.9789,1],[0.9483,1],[0.576,1],[0.8239,1],[0.936,1],[0.7149,1],[0.9051,1],[0.525,1],[0.6941,0],[0.921,1],[0.8773,1],[0.8686,0],[0.9911,1],[0.8532,1],[0.9839,1],[0.9871,1],[0.9558,1],[0.9967,1],[0.9721,1],[0.9398,1],[0.5547,0],[0.8297,0],[0.9829,1],[0.9879,1],[0.8736,1],[0.8331,1],[0.9363,1],[0.9693,1],[0.7476,1],[0.9603,1],[0.8098,1],[0.8641,1],[0.6121,0],[0.9786,1],[0.9862,1],[0.9372,1],[0.4945,0],[0.7116,1],[0.9943,1],[0.983,1],[0.9312,1],[0.9532,1],[0.9042,0],[0.9176,1],[0.8055,1],[0.9811,1],[0.9222,1],[0.4961,1],[0.9447,1],[0.983,1],[0.8525,1],[0.9691,1],[0.926,1],[0.9363,1],[0.7942,0],[0.9954,1],[0.965,1],[0.7381,1],[0.8708,1],[0.964,1],[0.9905,1],[0.8232,0],[0.7104,1],[0.7672,1],[0.9609,0],[0.8794,1],[0.8027,1],[0.7788,1],[0.6893,1],[0.7926,1],[0.9626,1],[0.8559,1],[0.6059,0],[0.6499,0],[0.9898,1],[0.7132,0],[0.9759,0],[0.8353,1],[0.5914,1],[0.7568,1],[0.9417,1],[0.8846,1],[0.9233,1],[0.8808,1],[0.9366,0],[0.9602,1],[0.9811,1],[0.8935,0],[0.5538,1],[0.9456,1],[0.9643,0],[0.9865,1],[0.9875,0],[0.886,1],[0.9773,1],[0.9591,1],[0.6356,1],[0.6106,1],[0.9042,1],[0.8524,1],[0.9183,0],[0.9934,1],[0.7329,1],[0.7962,1],[0.6103,1],[0.9792,1],[0.7532,0],[0.9364,1],[0.989,1],[0.7282,0],[0.9882,1],[0.9366,1],[0.7437,1],[0.6567,0],[0.5782,1],[0.7325,1],[0.7846,0],[0.6858,1],[0.9383,1],[0.9377,1],[0.9071,0],[0.6318,1],[0.5615,1],[0.6519,0],[0.8627,0],[0.9696,1],[0.962,1],[0.5855,1],[0.5242,0],[0.5466,1],[0.8472,1],[0.9779,1],[0.9838,1],[0.9675,1],[0.7532,0],[0.8863,0],[0.9609,1],[0.9879,1],[0.9841,1],[0.5108,1],[0.9858,1],[0.9154,1],[0.9912,1],[0.8463,0],[0.9463,1],[0.5161,0],[0.6825,0],[0.8996,1],[0.9073,1],[0.9553,1],[0.6905,0],[0.9776,1],[0.9629,1],[0.9662,1],[0.8318,1],[0.9858,1],[0.5242,1],[0.6366,1],[0.9291,1],[0.9824,1],[0.9652,1],[0.969,1],[0.6528,1],[0.9747,1],[0.9838,1],[0.9788,1],[0.9527,1],[0.5716,1],[0.94,1],[0.9797,1],[0.5855,0],[0.8713,1],[0.8137,1],[0.9452,1],[0.8658,1],[0.9363,1],[0.9935,1],[0.827,1],[0.9776,1],[0.9209,1],[0.8318,1],[0.9021,1],[0.9845,1],[0.7761,0],[0.9904,1],[0.9606,1],[0.9962,1],[0.9347,1],[0.9169,1],[0.929,1],[0.6108,0],[0.665,0],[0.5214,1],[0.6217,1],[0.9851,1],[0.8788,1],[0.7883,0],[0.9491,1],[0.7594,0],[0.4958,1],[0.99,1],[0.9643,1],[0.7159,1],[0.9397,1],[0.5199,0],[0.6386,1],[0.9753,1],[0.9268,1],[0.9843,1],[0.9626,1],[0.5544,1],[0.4941,1],[0.9479,1],[0.9824,1],[0.6848,1],[0.9312,1],[0.9756,1],[0.818,0],[0.9719,1],[0.9513,1],[0.982,0],[0.712,1],[0.9866,0],[0.9125,1],[0.9891,1],[0.9813,1],[0.9788,1],[0.9509,0],[0.962,1],[0.9553,1],[0.8617,0],[0.978,1],[0.9854,1],[0.9059,0],[0.78,1],[0.936,1],[0.7507,0],[0.7962,1],[0.5504,0],[0.9134,1],[0.5629,0],[0.5459,0],[0.6858,0],[0.8297,1],[0.917,1],[0.9398,1],[0.7815,0],[0.6081,1],[0.9857,1],[0.7856,1],[0.9937,1],[0.8154,0],[0.8716,1],[0.9877,1],[0.8819,0],[0.9782,1],[0.599,1],[0.8691,1],[0.9097,1],[0.9721,1],[0.9708,1],[0.8063,1],[0.6059,1],[0.929,0],[0.8869,1],[0.9703,0],[0.8954,1],[0.9669,1],[0.6862,0],[0.7565,1],[0.9944,1],[0.6339,1],[0.5516,0],[0.9254,1],[0.8205,1],[0.8831,1],[0.8433,1],[0.8422,0],[0.7846,0],[0.9738,1],[0.9509,1],[0.9155,1],[0.9725,1],[0.5048,1],[0.8145,0],[0.8975,1],[0.5279,1],[0.6874,1],[0.8851,0],[0.9662,1],[0.9952,1],[0.9131,1],[0.9411,1]],"quiz":[{"n":3706,"url":"https://github.com/kserve/kserve/issues/3706","title":"ResponseStartTimeoutSeconds does not honor TimeoutSeconds specified by user","text":"Currently the new Knative setting `ResponseStartTimeoutSeconds` is not exposed to the kserve user, however when TimeoutSeconds default in Knative is set to be 60s and user overrides to 600s, the `ResponseStartTimeoutSeconds` is set to 60s which is unexpected and the requests time out much earlier than it should be. - Knative Version: 1.13 - KServe Version: 0.13 - Cloud Environment:[k8s_istio/istio_dex/gcp_basic_auth/\u2026","label":"bug","kind":{"bug":0.962,"feature":0.0273,"question":0.0107},"area":["networking",0.4833],"needs_info":0.1021,"priority":1.424},{"n":2863,"url":"https://github.com/kserve/kserve/issues/2863","title":"Allow using SSL between transformer and predictor","text":"Currently the transformer is hard-coded to [use `http` to communicate with the predictor](https://github.com/kserve/kserve/blob/master/python/kserve/kserve/model.py#L36). We should add an extra `use_ssl` property to the `Model` that will enable connecting to the predictor via HTTPS. By default this property would be `false`.","label":"feature","kind":{"bug":0.0051,"feature":0.9871,"question":0.0077},"area":["python",0.5007],"needs_info":0.0505,"priority":0.9352},{"n":2167,"url":"https://github.com/kserve/kserve/issues/2167","title":"How can Custom Predictors load models in model storage?","text":"I want to customize the predictor by putting the mar file in the model storage. [code] How do you load and use the model in the load method when you use the predictor for custom? For example, I want to load model of model store into `self.model` [code]","label":"question","kind":{"bug":0.0038,"feature":0.0123,"question":0.9839},"area":["storage",0.6014],"needs_info":0.4192,"priority":0.7482},{"n":2548,"url":"https://github.com/kserve/kserve/issues/2548","title":"Istio 503","text":"I make an image myself and deploy it through KServe, but when I access isvc through istio, istio gives a 503 status code. The specific error is [code] I want to be able to access my isvc through istio When I used KFServing 0.6.1 before, it was working fine. When I upgraded KFServing to KServe 0.9.0rc, it gave the above error. - Istio Version: 1.9.4 - Knative Version: v1.4.0 - KFServing Version: 0.9.0rc - Kfdef:[k8s_i\u2026","label":"bug","kind":{"bug":0.4958,"feature":0.0083,"question":0.4958},"area":["networking",0.8638],"needs_info":0.7678,"priority":1.6098},{"n":3763,"url":"https://github.com/kserve/kserve/issues/3763","title":"Can't find version compatibility matrix for KServe","text":"I am trying to find compatibility matrix for KServe + K8S + KNative. There is this compatibility matrix: https://kserve.github.io/website/latest/admin/serverless/serverless/#recommended-version-matrix But there is no information how to choose KServe version itself. Please help!","label":"bug","kind":{"bug":0.0043,"feature":0.0082,"question":0.9875},"area":["docs",0.7373],"needs_info":0.0299,"priority":0.7078},{"n":3784,"url":"https://github.com/kserve/kserve/issues/3784","title":"Bump vLLM version in huggingface_server to v0.5.1","text":"Bump vLLM version in huggingface_server to v0.5.1 so that kserve supports new gemma2 models through vllm","label":"bug","kind":{"bug":0.0518,"feature":0.9071,"question":0.041},"area":["llm",0.6164],"needs_info":0.0369,"priority":0.7553}],"incidents":[{"app":"api-gateway","status":"Running \u00b7 restarts 0","truth":"healthy","held_out":true,"v1":{"cause":[["bad-probe",0.936],["healthy",0.04],["dependency-down",0.009]],"owner":"app-team","restart":0.4459,"page":0.1125,"severity":0.7723,"ms":1463},"v2":{"cause":[["healthy",0.512],["bad-probe",0.456],["dependency-down",0.01]],"owner":"app-team","restart":0.4192,"page":0.1238,"severity":0.7184,"ms":1458}},{"app":"auth-svc","status":"Running \u00b7 restarts 0","truth":"bad-probe","held_out":false,"v1":{"cause":[["bad-probe",0.989],["missing-config",0.003],["bad-command",0.003]],"owner":"app-team","restart":0.1125,"page":0.1494,"severity":2.0016,"ms":1933},"v2":{"cause":[["bad-probe",0.98],["missing-config",0.006],["healthy",0.006]],"owner":"app-team","restart":0.1021,"page":0.1494,"severity":1.9672,"ms":1903}},{"app":"billing-api","status":"CreateContainerConfigError \u00b7 restarts 0","truth":"missing-config","held_out":true,"v1":{"cause":[["missing-config",0.994],["unschedulable",0.002],["image-pull",0.001]],"owner":"app-team","restart":0.0115,"page":0.2522,"severity":2.5967,"ms":1296},"v2":{"cause":[["missing-config",0.995],["unschedulable",0.003],["image-pull",0.001]],"owner":"app-team","restart":0.0109,"page":0.2322,"severity":2.6016,"ms":1187}},{"app":"cart-cache","status":"Running \u00b7 restarts 0","truth":"healthy","held_out":true,"v1":{"cause":[["healthy",0.957],["bad-probe",0.013],["missing-config",0.01]],"owner":"nobody","restart":0.1125,"page":0.0158,"severity":0.2444,"ms":1470},"v2":{"cause":[["healthy",0.961],["bad-probe",0.009],["missing-config",0.009]],"owner":"nobody","restart":0.1125,"page":0.0142,"severity":0.2444,"ms":1545}},{"app":"checkout-api","status":"CrashLoopBackOff \u00b7 restarts 7","truth":"out-of-memory","held_out":false,"v1":{"cause":[["out-of-memory",0.989],["bad-probe",0.003],["bad-command",0.002]],"owner":"app-team","restart":0.062,"page":0.5,"severity":2.2664,"ms":1426},"v2":{"cause":[["out-of-memory",0.982],["bad-probe",0.006],["healthy",0.004]],"owner":"app-team","restart":0.1638,"page":0.5808,"severity":2.3071,"ms":1631}},{"app":"etl-runner","status":"Pending \u00b7 restarts 0","truth":"unschedulable","held_out":false,"v1":{"cause":[["unschedulable",0.992],["missing-config",0.002],["image-pull",0.001]],"owner":"platform-team","restart":0.0559,"page":0.2732,"severity":2.2691,"ms":872},"v2":{"cause":[["unschedulable",0.994],["missing-config",0.001],["image-pull",0.001]],"owner":"platform-team","restart":0.0686,"page":0.2522,"severity":2.2578,"ms":905}},{"app":"events-consumer","status":"CrashLoopBackOff \u00b7 restarts 6","truth":"dependency-down","held_out":true,"v1":{"cause":[["dependency-down",0.981],["bad-probe",0.006],["bad-command",0.004]],"owner":"platform-team","restart":0.0686,"page":0.5541,"severity":2.3741,"ms":1669},"v2":{"cause":[["dependency-down",0.967],["bad-probe",0.01],["healthy",0.01]],"owner":"platform-team","restart":0.062,"page":0.5271,"severity":2.4398,"ms":1742}},{"app":"geo-api","status":"ImagePullBackOff \u00b7 restarts 0","truth":"image-pull","held_out":true,"v1":{"cause":[["image-pull",0.994],["unschedulable",0.003],["missing-config",0.001]],"owner":"app-team","restart":0.0455,"page":0.3425,"severity":2.7185,"ms":1908},"v2":{"cause":[["image-pull",0.995],["unschedulable",0.003],["missing-config",0.001]],"owner":"app-team","restart":0.0455,"page":0.393,"severity":2.7276,"ms":1518}},{"app":"inventory-svc","status":"CrashLoopBackOff \u00b7 restarts 7","truth":"dependency-down","held_out":false,"v1":{"cause":[["dependency-down",0.993],["bad-probe",0.003],["missing-config",0.001]],"owner":"app-team","restart":0.0269,"page":0.5,"severity":2.7374,"ms":1321},"v2":{"cause":[["dependency-down",0.984],["bad-probe",0.007],["healthy",0.003]],"owner":"app-team","restart":0.0559,"page":0.5271,"severity":2.7249,"ms":1246}},{"app":"llm-batch","status":"Pending \u00b7 restarts 0","truth":"unschedulable","held_out":false,"v1":{"cause":[["unschedulable",0.997],["storage",0.001],["out-of-memory",0.0]],"owner":"platform-team","restart":0.0559,"page":0.1361,"severity":2.0213,"ms":910},"v2":{"cause":[["unschedulable",0.998],["missing-config",0.0],["bad-probe",0.0]],"owner":"platform-team","restart":0.0559,"page":0.1125,"severity":2.0842,"ms":944}},{"app":"metrics-agent","status":"CrashLoopBackOff \u00b7 restarts 7","truth":"bad-command","held_out":false,"v1":{"cause":[["bad-command",0.958],["missing-config",0.026],["bad-probe",0.004]],"owner":"app-team","restart":0.0369,"page":0.2953,"severity":2.0751,"ms":1563},"v2":{"cause":[["bad-command",0.951],["missing-config",0.027],["bad-probe",0.005]],"owner":"app-team","restart":0.0333,"page":0.2953,"severity":2.0992,"ms":1513}},{"app":"ml-scorer","status":"CrashLoopBackOff \u00b7 restarts 6","truth":"out-of-memory","held_out":true,"v1":{"cause":[["out-of-memory",0.991],["bad-probe",0.003],["unschedulable",0.002]],"owner":"app-team","restart":0.1361,"page":0.3425,"severity":2.1543,"ms":2162},"v2":{"cause":[["out-of-memory",0.98],["healthy",0.006],["bad-probe",0.005]],"owner":"app-team","restart":0.0759,"page":0.3185,"severity":2.2542,"ms":1741}},{"app":"notifier","status":"CrashLoopBackOff \u00b7 restarts 7","truth":"missing-config","held_out":false,"v1":{"cause":[["missing-config",0.994],["bad-probe",0.002],["dependency-down",0.001]],"owner":"app-team","restart":0.0196,"page":0.4729,"severity":2.2947,"ms":1428},"v2":{"cause":[["missing-config",0.993],["bad-probe",0.002],["healthy",0.001]],"owner":"app-team","restart":0.0186,"page":0.4729,"severity":2.2968,"ms":1428}},{"app":"orders-api","status":"CreateContainerConfigError \u00b7 restarts 0","truth":"missing-config","held_out":false,"v1":{"cause":[["missing-config",0.995],["unschedulable",0.002],["storage",0.001]],"owner":"app-team","restart":0.023,"page":0.1638,"severity":2.6194,"ms":1261},"v2":{"cause":[["missing-config",0.994],["unschedulable",0.003],["storage",0.001]],"owner":"app-team","restart":0.023,"page":0.1792,"severity":2.6194,"ms":1289}},{"app":"payments-worker","status":"ImagePullBackOff \u00b7 restarts 0","truth":"image-pull","held_out":false,"v1":{"cause":[["image-pull",0.995],["unschedulable",0.003],["missing-config",0.001]],"owner":"app-team","restart":0.0686,"page":0.2522,"severity":2.5706,"ms":1372},"v2":{"cause":[["image-pull",0.995],["unschedulable",0.003],["missing-config",0.001]],"owner":"app-team","restart":0.0686,"page":0.2322,"severity":2.5706,"ms":1369}},{"app":"pdf-render","status":"Pending \u00b7 restarts 0","truth":"unschedulable","held_out":true,"v1":{"cause":[["unschedulable",0.996],["out-of-memory",0.001],["missing-config",0.001]],"owner":"platform-team","restart":0.062,"page":0.2732,"severity":2.3402,"ms":1417},"v2":{"cause":[["unschedulable",0.996],["missing-config",0.001],["out-of-memory",0.001]],"owner":"platform-team","restart":0.0505,"page":0.2322,"severity":2.1912,"ms":1547}},{"app":"reports-db","status":"Pending \u00b7 restarts 0","truth":"storage","held_out":false,"v1":{"cause":[["storage",0.965],["unschedulable",0.027],["missing-config",0.003]],"owner":"platform-team","restart":0.0196,"page":0.2732,"severity":2.5447,"ms":1543},"v2":{"cause":[["storage",0.972],["unschedulable",0.021],["missing-config",0.003]],"owner":"platform-team","restart":0.0207,"page":0.2732,"severity":2.55,"ms":1537}},{"app":"search-api","status":"CrashLoopBackOff \u00b7 restarts 9","truth":"bad-probe","held_out":false,"v1":{"cause":[["bad-probe",0.741],["bad-command",0.144],["dependency-down",0.05]],"owner":"app-team","restart":0.1238,"page":0.2732,"severity":2.6345,"ms":2084},"v2":{"cause":[["bad-probe",0.849],["bad-command",0.058],["dependency-down",0.036]],"owner":"app-team","restart":0.1494,"page":0.2322,"severity":2.6306,"ms":2098}},{"app":"web-frontend","status":"Running \u00b7 restarts 0","truth":"healthy","held_out":false,"v1":{"cause":[["bad-probe",0.928],["healthy",0.05],["dependency-down",0.008]],"owner":"app-team","restart":0.4192,"page":0.1021,"severity":0.5657,"ms":1266},"v2":{"cause":[["healthy",0.628],["bad-probe",0.35],["dependency-down",0.007]],"owner":"app-team","restart":0.4192,"page":0.0926,"severity":0.5097,"ms":1262}}]};
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]; }); }
  function bars(probs, mark, cls, markText) {
    return Object.keys(probs).sort(function (a, b) { return probs[b] - probs[a]; }).map(function (k, i) {
      var v = probs[k];
      return '<div class="oj-bar-row"><span class="oj-bar-k">' + esc(k) + (mark === k ? ' <em>' + (markText || 'label') + '</em>' : '') + '</span>' +
        '<span class="oj-track"><span class="oj-fill ' + (i === 0 ? (cls || '') : 'oj-dim') + '" style="width:' + Math.max(v * 100, 0.8) + '%"></span></span>' +
        '<span class="oj-bar-v">' + v.toFixed(2) + '</span></div>';
    }).join('');
  }
  function top(probs) { return Object.keys(probs).reduce(function (a, b) { return probs[a] >= probs[b] ? a : b; }); }

  // Be the triager
  var COMMENTS = {
    2548: "A coin flip: 0.4958 for bug, 0.4958 for question. Exactly the kind of issue a threshold should hand to a human.",
    3763: "Labelled bug, but the author ends with \u201cPlease help!\u201d. OpenJev's 0.99 for question is hard to argue with.",
    3784: "A dependency bump. KServe files these as bugs, OpenJev reads it as a feature request. Both are defensible."
  };
  var quiz = document.getElementById('oj-quiz');
  if (quiz) {
    var qi = 0, you = 0, model = 0, answered = 0;
    var renderQuiz = function () {
      var q = D.quiz[qi];
      quiz.innerHTML = '<div class="oj-quiz-meta"><span>Issue ' + (qi + 1) + ' of ' + D.quiz.length + ' \u00b7 <a href="' + q.url + '" target="_blank" rel="noopener">kserve/kserve#' + q.n + '</a></span>' +
        '<span>You matched the label ' + you + '/' + answered + ' \u00b7 OpenJev ' + model + '/' + answered + '</span></div>' +
        '<div class="oj-quiz-title">' + esc(q.title) + '</div><div class="oj-quiz-text">' + esc(q.text) + '</div>' +
        '<div>' + ['bug', 'feature', 'question'].map(function (k) { return '<button class="oj-btn" data-k="' + k + '">' + k + '</button>'; }).join('') + '</div>' +
        '<div class="oj-reveal-slot"></div>';
      Array.prototype.forEach.call(quiz.querySelectorAll('button[data-k]'), function (b) {
        b.addEventListener('click', function () { reveal(b.getAttribute('data-k')); });
      });
    };
    var reveal = function (guess) {
      var q = D.quiz[qi], pred = top(q.kind);
      answered += 1; you += guess === q.label ? 1 : 0; model += pred === q.label ? 1 : 0;
      Array.prototype.forEach.call(quiz.querySelectorAll('button[data-k]'), function (b) {
        b.disabled = true; if (b.getAttribute('data-k') === guess) b.classList.add('oj-pick');
      });
      quiz.querySelector('.oj-quiz-meta span:last-child').textContent = 'You matched the label ' + you + '/' + answered + ' \u00b7 OpenJev ' + model + '/' + answered;
      var html = '<div class="oj-reveal"><p>Maintainers labelled it <b>' + q.label + '</b>. You said <b>' + guess + '</b>. OpenJev:</p>' +
        bars(q.kind, q.label, pred === q.label ? '' : 'oj-amber') +
        '<div class="oj-side"><span>area: <b>' + esc(q.area[0]) + '</b> ' + q.area[1].toFixed(2) + '</span><span>needs more info: <b>' + q.needs_info.toFixed(2) + '</b></span>' +
        '<span>priority: <b>' + q.priority.toFixed(1) + '</b> of 3</span><span>all four from one request</span></div>' +
        (COMMENTS[q.n] ? '<div class="oj-comment">' + COMMENTS[q.n] + '</div>' : '') +
        '<div style="margin-top:10px"><button class="oj-btn oj-next">' + (qi + 1 < D.quiz.length ? 'Next issue \u2192' : 'Start over') + '</button></div></div>';
      quiz.querySelector('.oj-reveal-slot').innerHTML = html;
      quiz.querySelector('.oj-next').addEventListener('click', function () {
        qi += 1; if (qi >= D.quiz.length) { qi = 0; you = 0; model = 0; answered = 0; } renderQuiz();
      });
    };
    renderQuiz();
  }

  // Confidence threshold
  var thr = document.getElementById('oj-thr');
  if (thr) {
    var rows = D.curve.slice().sort(function (a, b) { return b[0] - a[0]; });
    thr.innerHTML = '<div class="oj-thr-head"><label for="oj-thr-in"><b>Auto-label when OpenJev is at least <span id="oj-thr-v"></span> sure</b></label>' +
      '<input id="oj-thr-in" type="range" min="0.34" max="0.99" step="0.01" value="0.90"></div>' +
      '<div class="oj-kpis"><div class="oj-kpi"><b id="oj-k-cov"></b><span>labelled automatically</span></div><div class="oj-kpi"><b id="oj-k-acc"></b><span>accuracy of those labels</span></div>' +
      '<div class="oj-kpi"><b id="oj-k-bad"></b><span>wrong labels that ship</span></div><div class="oj-kpi"><b id="oj-k-hum"></b><span>left for a human</span></div></div>' +
      '<div class="oj-strip" id="oj-strip"></div><div class="oj-strip-legend"><span><i style="background:#0aa66e"></i>auto, matches the label</span>' +
      '<span><i style="background:#dc2626"></i>auto, disagrees with the label</span><span><i style="background:#d1d5db"></i>sent to a human</span><span>one square per issue, most confident first</span></div>';
    var strip = document.getElementById('oj-strip');
    strip.innerHTML = rows.map(function () { return '<i></i>'; }).join('');
    var cells = strip.children, input = document.getElementById('oj-thr-in');
    var update = function () {
      var t = parseFloat(input.value), n = 0, ok = 0;
      rows.forEach(function (r, i) {
        var auto = r[0] >= t; cells[i].className = auto ? (r[1] ? 'ok' : 'bad') : '';
        if (auto) { n += 1; ok += r[1]; }
      });
      document.getElementById('oj-thr-v').textContent = t.toFixed(2);
      document.getElementById('oj-k-cov').textContent = Math.round(100 * n / rows.length) + '% (' + n + ')';
      document.getElementById('oj-k-acc').textContent = n ? (100 * ok / n).toFixed(1) + '%' : '\u2014';
      document.getElementById('oj-k-bad').textContent = n - ok;
      document.getElementById('oj-k-hum').textContent = rows.length - n;
    };
    input.addEventListener('input', update); update();
  }

  // Incident board
  var inc = document.getElementById('oj-inc');
  if (inc) {
    var policy = 'v1', open = null;
    var renderInc = function () {
      var correct = D.incidents.filter(function (x) { return x[policy].cause[0][0] === x.truth; }).length;
      var html = '<div class="oj-inc-head"><div><button class="oj-btn' + (policy === 'v1' ? ' oj-on' : '') + '" data-p="v1">v1: original question</button>' +
        '<button class="oj-btn' + (policy === 'v2' ? ' oj-on' : '') + '" data-p="v2">v2: judge the current state</button></div>' +
        '<div class="oj-inc-score"><b>' + correct + ' / ' + D.incidents.length + '</b> root causes correct \u00b7 <span style="color:#f59e0b">amber</span> = correct but below 0.8, would go to a human</div></div><div class="oj-inc-grid">';
      D.incidents.forEach(function (x, i) {
        var r = x[policy], c = r.cause[0], ok = c[0] === x.truth;
        html += '<div class="oj-inc ' + (!ok ? 'bad' : (c[1] < 0.8 ? 'unsure' : 'ok')) + '" data-i="' + i + '"><b>' + esc(x.app) + (x.held_out ? '<span class="ho">held-out</span>' : '') + '</b>' +
          '<span class="st">' + esc(x.status) + '</span><div class="dx">' + (ok ? '\u2713 ' : '\u2717 ') + esc(c[0]) + ' ' + c[1].toFixed(2) + '</div></div>';
        if (open === i) {
          var probs = {}; r.cause.forEach(function (kv) { probs[kv[0]] = kv[1]; });
          html += '<div class="oj-inc-detail"><h4>' + esc(x.app) + ' \u00b7 real cause: <code>' + esc(x.truth) + '</code></h4>' + bars(probs, x.truth, ok ? '' : 'oj-red', 'truth') +
            '<div class="oj-side"><span>who acts: <b>' + esc(r.owner) + '</b></span><span>restart helps: <b>' + r.restart.toFixed(2) + '</b></span>' +
            '<span>page now: <b>' + r.page.toFixed(2) + '</b></span><span>severity: <b>' + r.severity.toFixed(1) + '</b> of 3</span><span>' + (r.ms / 1000).toFixed(1) + ' s for 5 questions</span></div></div>';
        }
      });
      inc.innerHTML = html + '</div>';
      Array.prototype.forEach.call(inc.querySelectorAll('button[data-p]'), function (b) {
        b.addEventListener('click', function () { policy = b.getAttribute('data-p'); renderInc(); });
      });
      Array.prototype.forEach.call(inc.querySelectorAll('.oj-inc'), function (el) {
        el.addEventListener('click', function () { var i = +el.getAttribute('data-i'); open = open === i ? null : i; renderInc(); });
      });
    };
    renderInc();
  }
})();
</script>
