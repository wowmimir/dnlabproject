import time
from typing import Dict, Any, List, Tuple
from m4_verification.src.models import (
    M3VerificationEvent,
    VerificationStatus,
    PinAllocation,
    MigrationAction,
    DynamicReconfigReport,
)


class TopologyReconfigurator:
    def __init__(self, base_topology_map: Dict[str, Any]):
        """
        base_topology_map follows M1 DAG format:
        Root -> Region -> ASN -> Witnessing Zone -> Rack -> Peers
        """
        self.topology = base_topology_map
        self.peer_index: Dict[str, Dict[str, Any]] = {}
        self._build_peer_index(self.topology)

    def _build_peer_index(self, node: Dict[str, Any]):
        """Recursively index peers to allow O(1) mutations."""
        if node.get("type") == "peer":
            self.peer_index[node["id"]] = node
            return

        for child in node.get("children", []):
            self._build_peer_index(child)

    def apply_m3_event(self, event: M3VerificationEvent) -> bool:
        """
        Updates the peer state in the topology tree.
        Adjusts CRUSH operational weights:
        - VERIFIED: Weight intact (1.0 or capacity-based)
        - UNVERIFIABLE_SHORT_RANGE: Degraded weight / tagged for M2 conservative multi-zone rule
        - FAILED_SPOOFED: Weight = 0 (quarantined from placement draws)
        """
        peer = self.peer_index.get(event.peer_id)
        if not peer:
            return False

        peer["verification_state"] = event.status.value

        if event.status == VerificationStatus.FAILED_SPOOFED:
            # Completely zero out CRUSH weight so M2 never places replicas here
            peer["weight"] = 0
            peer["quarantined"] = True
        elif event.status == VerificationStatus.UNVERIFIABLE_SHORT_RANGE:
            # Keep active, but flag failure domain boundary
            peer["short_range_flag"] = True
        elif event.status == VerificationStatus.VERIFIED:
            peer["quarantined"] = False

        return True

    def reconcile_pins(
        self,
        current_pins: List[PinAllocation],
        m2_placement_runner,  # Callable to trigger M2 placement algorithm
        target_replicas: int = 3,
    ) -> DynamicReconfigReport:
        """
        Audits active pin allocations against the mutated topology DAG.
        If a replica resides on a FAILED_SPOOFED or compromised peer,
        it calls M2 to re-select a safe peer and generates a migration task.
        """
        migrations: List[MigrationAction] = []
        quarantined = [
            pid for pid, p in self.peer_index.items() if p.get("quarantined", False)
        ]

        for pin in current_pins:
            valid_peers = []
            compromised_peers = []

            for pid in pin.allocated_peers:
                peer = self.peer_index.get(pid)
                if not peer or peer.get("verification_state") == VerificationStatus.FAILED_SPOOFED.value:
                    compromised_peers.append(pid)
                else:
                    valid_peers.append(pid)

            if compromised_peers:
                needed = target_replicas - len(valid_peers)
                # Query M2 placement engine with the updated topology DAG,
                # excluding existing valid peers to find non-colliding failure domains
                replacement_peers = m2_placement_runner(
                    topology=self.topology,
                    cid=pin.cid,
                    num_replicas=needed,
                    exclude_peers=valid_peers,
                )

                for bad_peer, new_peer in zip(compromised_peers, replacement_peers):
                    migrations.append(
                        MigrationAction(
                            cid=pin.cid,
                            source_peer=bad_peer,
                            target_peer=new_peer,
                            reason=f"Peer {bad_peer} flagged as FAILED_SPOOFED by M3",
                        )
                    )

        return DynamicReconfigReport(
            timestamp=time.time(),
            total_compromised_pins=len(migrations),
            migrations_required=migrations,
            quarantined_peers=quarantined,
        )