import json
from typing import List
from models import ClaimedLocation, TopologyBucket, PeerNode, BucketType, VerificationState

def build_topology_tree(claims: List[ClaimedLocation]) -> TopologyBucket:
    """Constructs a CRUSH-style hierarchy from flat peer claims."""
    
    root = TopologyBucket(id="default_root", type=BucketType.ROOT, verification_state=VerificationState.VERIFIED)

    def get_or_create_bucket(parent: TopologyBucket, bucket_id: str, b_type: BucketType) -> TopologyBucket:
        for child in parent.children:
            if isinstance(child, TopologyBucket) and child.id == bucket_id and child.type == b_type:
                return child
        
        new_bucket = TopologyBucket(id=bucket_id, type=b_type)
        parent.children.append(new_bucket)
        return new_bucket

    for claim in claims:
        # Traverse and build the tree branches
        region = get_or_create_bucket(root, claim.region, BucketType.REGION)
        asn = get_or_create_bucket(region, claim.asn, BucketType.ASN)
        zone = get_or_create_bucket(asn, claim.witnessing_zone, BucketType.WITNESSING_ZONE)
        rack = get_or_create_bucket(zone, claim.rack, BucketType.RACK)
        
        # Add the leaf node
        node = PeerNode(peer_id=claim.peer_id, weight=claim.weight)
        rack.children.append(node)
        
        # Scenario Logic: Flagging the Short-Range Limit
        # If we see specific localized zones, we flag them so the CRUSH placement engine knows 
        # it cannot guarantee safety within this specific domain.
        if "local_campus" in zone.id.lower():
            zone.verification_state = VerificationState.UNVERIFIABLE_SHORT_RANGE

    return root

if __name__ == "__main__":
    # Scenario A & C: Mixed network with global nodes and a localized campus cluster
    raw_network_data = [
        ClaimedLocation(peer_id="QmGlobal1", region="EU", asn="AS16509", witnessing_zone="Frankfurt-1", rack="RowA"),
        ClaimedLocation(peer_id="QmGlobal2", region="US", asn="AS15169", witnessing_zone="NY-Core", rack="RowB"),
        
        # These two are inside the 500km threshold and will be flagged as unverifiable
        ClaimedLocation(peer_id="QmLocal1", region="EU", asn="AS3209", witnessing_zone="Local_Campus_A", rack="Lab1"),
        ClaimedLocation(peer_id="QmLocal2", region="EU", asn="AS3209", witnessing_zone="Local_Campus_A", rack="Lab2"),
    ]

    topology = build_topology_tree(raw_network_data)
    
    # Export for M2 (CRUSH Placement Engine)
    output_filename = "topology_map.json"
    
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(topology.model_dump_json(indent=2))
        
    print(f"Topology map successfully exported to {output_filename}")