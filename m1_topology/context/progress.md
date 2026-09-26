# Module 1 (M1) Progress Tracker

**Current Status:** M1 Core Engine Implementation Complete. Awaiting visual diagram generation and lab report finalization. Hand-off to M2 (JSON Map) is ready.

## Completed Tasks
- [x] Initialized Python environment using `uv` package manager.
- [x] Installed and configured Pydantic for strict schema validation.
- [x] Defined the Failure-Domain Schema (`src/models.py`), mapping theoretical DePIN/PoL concepts to standard CRUSH terminology.
- [x] Built the Hierarchy Engine (`src/main.py`) to parse flat peer claims and dynamically construct a nested JSON tree (Root → Region → ASN → Witnessing Zone → Rack).
- [x] Implemented automated flagging for the ~500km distance limitation, explicitly tagging localized nodes as `unverifiable_short_range`.

## Pending Tasks (M1)
- [ ] Draw network state scenario diagrams (Honest, Sybil, Short-Range) for the lab presentation.
- [ ] Draft the lab report methodology, benchmarking, and discussion sections.

---

## Decisions Taken & Contradiction Log (AI Context Guardrails)

* **Tech Stack Pivot:** Initially considered TypeScript/TypeBox for schema validation, but decisively pivoted to Python with Pydantic. Python is the industry standard for this type of research data modeling and allows seamless integration for the downstream modules. 
  * **AI Directive:** Do not suggest JavaScript/TypeScript solutions for the core engine moving forward.

* **Nomenclature Shift:** Standard CRUSH maps use the bucket term "Datacenter." We explicitly replaced this with "Witnessing Zone" in the codebase to natively align with the Brito et al. (2026) Proof-of-Location architecture. 
  * **AI Directive:** Always use `witnessing_zone` in schemas and JSON outputs, never datacenter.

* **Handling the 500km Threshold:** Rather than treating short-range indistinguishability as a system "failure" or throwing an error, we explicitly model it as a valid state. Nodes inside this threshold are tagged `unverifiable_short_range`. 
  * **AI Directive:** This tag does not mean the node is malicious; it means the CRUSH placement engine (M2) must logically assume they could share a failure domain and place backup replicas elsewhere.

* **Module Boundaries:** M1 is strictly responsible for building the map and defining the theoretical verification states. 
  * **AI Directive:** Do not write active pinging/latency measurement code in M1. That is strictly the domain of M3.