import json
import sys
from pathlib import Path

try:
    from m4_reconfig.src.models import M3VerificationEvent, VerificationStatus, PinAllocation  # type: ignore[reportMissingImports]
    from m4_reconfig.src.reconfig_engine import TopologyReconfigurator  # type: ignore[reportMissingImports]
except ImportError:
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from m4_reconfig.src.models import M3VerificationEvent, VerificationStatus, PinAllocation  # type: ignore[reportMissingImports]
    from m4_reconfig.src.reconfig_engine import TopologyReconfigurator  # type: ignore[reportMissingImports]

# 1. Mock M1 Topology DAG
mock_m1_topology = {
    "id": "root",
    "type": "root",
    "children": [
        {
            "id": "region-asia-south",
            "type": "region",
            "children": [
                {
                    "id": "wz-campus-zone-1",
                    "type": "witnessing_zone",
                    "children": [
                        {"id": "peer-campus-A", "type": "peer", "weight": 100, "verification_state": "pending"},
                        {"id": "peer-campus-B", "type": "peer", "weight": 100, "verification_state": "pending"}
                    ]
                }
            ]
        },
        {
            "id": "region-europe-west",
            "type": "region",
            "children": [
                {
                    "id": "wz-frankfurt-zone",
                    "type": "witnessing_zone",
                    "children": [
                        {"id": "peer-distant-node", "type": "peer", "weight": 100, "verification_state": "pending"}
                    ]
                }
            ]
        }
    ]
}

# 2. Mock M2 Placement Engine Interface
def mock_m2_placement(topology, cid, num_replicas, exclude_peers):
    """Simulates deterministic CRUSH selection excluding compromised/quarantined peers."""
    candidates = ["peer-distant-node", "peer-campus-B"]
    return [p for p in candidates if p not in exclude_peers][:num_replicas]

# 3. Execution
reconfigurator = TopologyReconfigurator(mock_m1_topology)

# Active pins before verification
active_pins = [
    PinAllocation(cid="QmZtmD2qwv42Uz58Eba9hi", allocated_peers=["peer-campus-A", "peer-distant-node"])
]

# Simulate M3 verification event: campus-A claimed distant region, but ping showed it was spoofed
m3_event = M3VerificationEvent(
    peer_id="peer-campus-A",
    observed_rtt_ms=0.8,
    claimed_distance_km=6500.0,
    status=VerificationStatus.FAILED_SPOOFED,
    reason="Speed of light violation: RTT < theoretical minimum propagation time"
)

# Apply M3 detection and reconcile cluster pin state
reconfigurator.apply_m3_event(m3_event)
report = reconfigurator.reconcile_pins(active_pins, mock_m2_placement, target_replicas=2)

print(report.model_dump_json(indent=2))