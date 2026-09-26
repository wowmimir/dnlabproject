# FDAR IPFS Cluster Engine (DePIN / PoL)

> **Failure-Domain & Location-Verification Aware Placement Engine for IPFS Cluster**

This repository serves as the central hub and single source of truth for the **FDAR (Failure-Domain Aware Replication)** IPFS Cluster architecture research project.

---

## 📌 Executive Summary

Standard IPFS Cluster distributes replicas across hash-space, which does not guarantee physical diversity. Replicas can end up co-located within the same power grid, building, or rack. While existing placement algorithms (CRUSH, Cassandra, Copysets) enforce failure-domain separation, they rely strictly on **unverified self-reported node metadata**.

**FDAR solves this by uniting two components:**
1. **CRUSH-style Hierarchical Placement:** Guarantees replicas never share a declared failure domain.
2. **Latency-based Plausibility Verification:** Verifies self-reported location claims against real network speed-of-light constraints before placing data.

> **Honest Limitation:** Physical distance verification operates reliably down to a defined physical boundary (~500km threshold in our model). Nodes within this threshold cannot be distinguished from spoofed local claims and are explicitly modeled as `unverifiable_short_range`.

---

## 🏗️ Repository Architecture & Module Ownership

This repository is structured as a **decoupled multi-module master project**. Each module operates independently within its own directory, using its own virtual environment and toolchain, while communicating asynchronously via shared file contracts.

### 🧭 Strict Module Work Directives

**These rules are mandatory for all contributors and AI agents.**

1. **Work only inside your own module folder.**  
   Stay strictly within your assigned module directory, e.g. `m1_topology/`, `m2_placement/`, `m3_verification/`, or `m4_reconfiguration/`. Do not edit files in another module unless you have been explicitly authorized by that module’s owner.

2. **Update the global tracker and relevant `.gitignore` files.**  
   When your module changes status, completes tasks, or introduces generated files, update the global tracker in `context/` and the appropriate `.gitignore` files. Keep the tracker accurate and current. If the repo currently uses root-level `tracker.md`, treat it as the global tracker equivalent.

3. **Work on module-specific branches.**  
   Use dedicated `m1-*`, `m2-*`, `m3-*`, and `m4-*` branches. Do not commit directly to `main`. Open PRs for review. This is required to prevent cross-module merge chaos and keep ownership boundaries clean.

4. **DO NOT TOUCH THE GLOBAL `PROJECT.MD` FILE INSIDE `context/`.**  
   The global project context file is read-only for module work unless a human explicitly requests a project-wide change. Propose changes through an issue or PR instead of editing it directly.

5. **DO NOT TOUCH THE GLOBAL README.**  
   The root `README.md` is project-wide documentation. Module work must not modify it unless explicitly authorized by the project owner. If documentation changes are needed, raise a proposal or PR.

6. **ALL SHARED THINGS MUST BE UPDATED ACCORDINGLY AND STRICTLY.**  
   Any change to `shared/outputs/` or `shared/schemas/` must be reflected immediately and precisely. Never silently change a shared schema, output format, or contract. Update the schema, regenerate outputs, and notify all affected module owners.

```text
dnlab/                          <-- MASTER REPOSITORY ROOT
├── README.md                   <-- Primary project documentation & onboarding
├── project_context.md          <-- Core technical context & research references
├── tracker.md                  <-- Progress tracker, milestones & AI guardrails
│
├── shared/                     <-- INTER-MODULE CONTRACTS & DATA
│   ├── schemas/                <-- Data models & Pydantic JSON schema exports
│   └── outputs/                <-- Output files passed between modules
│
├── m1_topology/                <-- MODULE 1: Topology Engine (Python / uv)
│   ├── README.md               <-- M1 execution & schema details
│   ├── pyproject.toml / uv.lock
│   └── src/
│       ├── models.py           <-- Core Pydantic Failure-Domain Schemas
│       └── main.py             <-- Builds hierarchy & outputs topology JSON
│
├── m2_placement/               <-- MODULE 2: CRUSH Placement Engine
│   ├── README.md               <-- Ingests shared/outputs/topology_map.json
│   └── src/
│
├── m3_verification/            <-- MODULE 3: Speed-of-Light Latency Verifier
│   ├── README.md               <-- Conducts active network measurements
│   └── src/
│
└── m4_reconfiguration/         <-- MODULE 4: Dynamic Re-routing Engine
    ├── README.md               <-- Updates topology based on M3 ping results
    └── src/
```