from enum import Enum
from typing import List, Union
from pydantic import BaseModel, Field

class VerificationState(str, Enum):
    VERIFIED = "verified"
    UNVERIFIABLE_SHORT_RANGE = "unverifiable_short_range"  # The ~500km limit boundary
    UNTRUSTED = "untrusted"
    PENDING_CHECK = "pending_check"

class BucketType(str, Enum):
    ROOT = "root"
    REGION = "region"
    ASN = "asn"
    WITNESSING_ZONE = "witnessing_zone"  # Replaces 'datacenter' to align with the PoL paper
    RACK = "rack"

class PeerNode(BaseModel):
    """The actual Decentralized Autonomous Machine (DAM) holding data."""
    peer_id: str
    weight: float = 1.0  # Storage capacity weight for CRUSH distribution
    type: str = "node"

class TopologyBucket(BaseModel):
    """A physical failure domain that can contain other domains or nodes."""
    id: str
    type: BucketType
    verification_state: VerificationState = VerificationState.PENDING_CHECK
    children: List[Union['TopologyBucket', PeerNode]] = Field(default_factory=list)

class ClaimedLocation(BaseModel):
    """Flat data ingested from the network before validation."""
    peer_id: str
    weight: float = 1.0
    region: str
    asn: str
    witnessing_zone: str
    rack: str