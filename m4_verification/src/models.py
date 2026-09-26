from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional


class VerificationStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    FAILED_SPOOFED = "failed_spoofed"
    UNVERIFIABLE_SHORT_RANGE = "unverifiable_short_range"


@dataclass
class M3VerificationEvent:
    """Payload emitted by M3 after latency & RTT distance bounding."""
    peer_id: str
    observed_rtt_ms: float
    claimed_distance_km: float
    status: VerificationStatus
    reason: Optional[str] = None


@dataclass
class PinAllocation:
    """Current state of a CID across the cluster."""
    cid: str
    allocated_peers: List[str]


@dataclass
class MigrationAction:
    cid: str
    source_peer: str
    target_peer: str
    action: str = field(default="repin_and_evict")
    reason: str


@dataclass
class DynamicReconfigReport:
    timestamp: float
    total_compromised_pins: int
    migrations_required: List[MigrationAction]
    quarantined_peers: List[str]