# FDAR IPFS Cluster — Master Project Tracker & Decisions Log

**Overall Status:** Active Development  
**Current Phase:** Phase 1 — M1 Finalization & Hand-off to M2

---

## 🚦 Executive Module Roadmap

```text
[M1: Topology Engine] ──(hand-off via shared/outputs/topology_map.json)──► [M2: Placement Engine]
         │                                                                             │
         ▼                                                                             ▼
[M3: Latency Verification] ──(updates verification_state)──► [M4: Dynamic Reconfiguration]
```

- **Module 1 (M1): Physical Topology & Failure-Domain Engine** — 🟡 *90% Complete*
- **Module 2 (M2): CRUSH-style FDAR Placement Engine** — ⚪ *Not Started (Awaiting M1 Hand-off)*
- **Module 3 (M3): Latency-based Location Verification Engine** — ⚪ *Not Started*
- **Module 4 (M4): Verification-Aware Placement & Dynamic Reconfiguration** — ⚪ *Not Started*

---

## 📌 Detailed Tracker by Module

### Module 1: Physical Topology & Failure-Domain Engine (M1)

**Owner:** M1 Lead  
**Status:** Core Engine Complete | Hand-off Ready

- [x] Initialized Python environment using `uv` package manager.
- [x] Installed and configured Pydantic for strict schema validation.
- [x] Defined the Failure-Domain Schema (`m1_topology/src/models.py`), mapping theoretical DePIN/PoL concepts to standard CRUSH terminology.
- [x] Built the Hierarchy Engine (`m1_topology/src/main.py`) to parse flat peer claims and dynamically construct a nested JSON tree (`Root` → `Region` → `ASN` → `Witnessing Zone` → `Rack`).
- [x] Implemented automated flagging for the ~500km distance limitation, explicitly tagging localized nodes as `unverifiable_short_range`.
- [x] Updated script export to write JSON output directly to `shared/outputs/topology_map.json` for M2 ingestion.
- [ ] Draw network state scenario diagrams (Honest, Sybil, Short-Range) for lab presentation.
- [ ] Draft lab report methodology, benchmarking, and discussion sections.

---

### Module 2: CRUSH-style FDAR Placement Engine (M2)

**Owner:** M2 Lead  
**Status:** Blocked on M1 Diagram/Report Finalization

- [ ] Parse `shared/outputs/topology_map.json` schema into M2 execution environment.
- [ ] Implement deterministic CRUSH selection algorithm for placing data replicas across distinct failure domains.
- [ ] Integrate failure-domain rules ensuring no two replicas share the same parent bucket.
- [ ] Implement fallback handling for `unverifiable_short_range` zones (assume co-location and place backup replicas in distinct physical regions).
- [ ] Unit test placement engine against honest and localized scenario maps.

---

### Module 3: Latency-Based Location Verification (M3)

**Owner:** M3 Lead  
**Status:** Planning

- [ ] Build active RTT (Round Trip Time) latency measurement harness for nodes listed in the topology map.
- [ ] Implement speed-of-light physical distance bounds checking algorithms.
- [ ] Evaluate measured latencies against claimed geographical locations.
- [ ] Update node states to `VERIFIED` or `FAILED_SPOOFED` based on latency threshold checks.
- [ ] Validate distance boundary accuracy around the ~500km range limit.

---

### Module 4: Verification-Aware Placement & Dynamic Reconfiguration (M4)

**Owner:** M4 Lead  
**Status:** Planning

- [ ] Construct dynamic map update engine that ingests M3 verification test results.
- [ ] Build re-routing orchestrator to detect spoofed nodes (`FAILED_SPOOFED`).
- [ ] Trigger M2 placement engine to re-allocate pinned data away from unverified/spoofed domains.
- [ ] Simulate network churn, location spoofing attacks, and dynamic failure recovery.

---

## 🛡️ Decisions Log & AI Context Guardrails

### 1. Tech Stack Decision

- **Decision:** Python with Pydantic for core schemas and logic.
- **Reasoning:** Industry standard for scientific data modeling, rapid prototyping, and seamless data hand-off.
- **AI Directive:** Do not suggest JavaScript/TypeScript solutions for the core engines moving forward.

### 2. Standardized Hierarchy Nomenclature

- **Decision:** Replace standard CRUSH "Datacenter" bucket with "Witnessing Zone".
- **Reasoning:** Aligns natively with Brito et al. (2026) Proof-of-Location terminology.
- **AI Directive:** Always use `witnessing_zone` in schemas, code, and JSON outputs. Never use `datacenter`.

### 3. Short-Range (~500km) Physical Threshold Modeling

- **Decision:** Nodes within ~500km are explicitly tagged `unverifiable_short_range`.
- **Reasoning:** Distance bounding cannot reliably distinguish true claims from false claims under ~500km due to network jitter and speed-of-light limits.
- **AI Directive:** `unverifiable_short_range` is a valid state, not a system failure. M2 must assume short-range nodes might share a failure domain and place backup replicas elsewhere.

### 4. Strict Module Boundaries

- **Decision:** M1 builds the map and defines theoretical states. M3 handles network latency measurements.
- **AI Directive:** Do not write active pinging or latency measurement code in M1. Keep network measurement logic strictly inside `m3_verification/`.