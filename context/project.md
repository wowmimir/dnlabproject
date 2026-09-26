# Project Context & End Goal

**The Idea:** IPFS Cluster decides which peers hold pinned data, but never verifies whether replicas are physically spread out, or whether a peer's claimed location is even true. We implement FDAR: CRUSH-style hierarchical placement guaranteeing replicas never share a declared failure domain, plus a latency-based plausibility check verifying claimed location against real measured network behavior before trusting it.

Tested on real peers across campus buildings and a distant node, backed by simulation. Results show verification meaningfully improves safety at real geographic distance, with a characterized, honest limitation at short range.

## The Core Gaps

*   Random placement in hash-space doesn't mean physical diversity. Copies can be "randomly" spread in a DHT's internal ID space while still landing in the same building, data center, or power grid.
*   Existing placement algorithms (CRUSH, Cassandra, Copysets) guarantee diversity — but only if their map is true. None of them verify the location data they're given.
*   Location-verification techniques (proof-of-location, distance-bounding) exist separately, but have never been combined with a placement algorithm. Verification tools check a claim; they don't feed that check into deciding where data goes. This is the core gap.
*   IPFS Cluster has an even more open version of this gap than Filecoin. Filecoin at least proves a copy exists; IPFS Cluster doesn't even guarantee that, let alone where it is.
*   The verification approach has a real, measurable range limit. It only reliably works above a certain distance threshold (~500km in our model); below that, it can't distinguish a true claim from a false one.
*   The same range-limit pattern shows up independently in unrelated, freshly published work (the IEEE ICSA 2026 witnessing-zone paper), at a completely different physical scale — suggesting this isn't a flaw specific to our implementation, but a general property of distance-based verification.

## Research References

*   E. Brito, F. Castillo, A. Hadachi, U. Norbisrath, J. Heiss, "Decentralized Proof-of-Location for Content Provenance: Towards Capture-Time Authenticity," *Companion Proceedings of the 23rd IEEE International Conference on Software Architecture (ICSA 2026), 5th International Workshop on Architecting and Engineering Digital Twins (AEDT 2026)*, 2026.
*   F. Castillo, O. Castillo, E. Brito, S. Espinola, "Trustworthy Decentralized Autonomous Machines: A New Paradigm in Automation Economy," *2025 IEEE International Conference on Blockchain and Cryptocurrency (ICBC), Workshop on Decentralized Physical Infrastructure Networks (DePIN 2025)*, 2025, pp. 1–7.

## Team Modules & AI Delegation Context

This project is divided into four interdependent modules. When assisting with this project, ensure outputs align strictly with the boundaries of the specific module being worked on:

*   **M1 (Current Focus): Physical Topology & Failure-Domain Modeling Engine.** Ingests flat peer claims and generates a strictly typed, hierarchical JSON failure-domain map.
*   **M2: CRUSH-style FDAR Placement Engine.** Takes the M1 JSON map and deterministically distributes replicas across the domains.
*   **M3: Latency-based Location Verification.** Pings the nodes in the M1 map to verify claimed locations against speed-of-light constraints.
*   **M4: Verification-Aware Placement & Dynamic Reconfiguration.** Updates the M1 map based on M3's test results, forcing M2 to re-route data if a location is spoofed.

### M1 Deliverables

*   Python-based topology ingestion engine (using Pydantic).
*   Automated generation of a CRUSH-compatible JSON directed acyclic graph (DAG).
*   Visual architecture diagrams modeling honest, Sybil, and short-range threshold scenarios for lab presentation.