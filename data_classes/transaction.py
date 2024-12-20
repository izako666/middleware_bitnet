from dataclasses import asdict, dataclass, field
from typing import List, Dict, Optional





@dataclass
class OutputDetail:
    output_type: str  # OutputScriptType, represented as string
    address: str
    pk_script: str
    output_index: int
    amount: int
    is_our_address: bool

    @classmethod
    def from_json(cls, data: dict) -> "OutputDetail":
        """Create an OutputDetail instance from a JSON dictionary."""
        return cls(**data)

    def to_json(self) -> dict:
        """Convert an OutputDetail instance to a JSON-compatible dictionary."""
        return asdict(self)


# PreviousOutPoint class
@dataclass
class PreviousOutPoint:
    outpoint: str
    is_our_output: bool

    @classmethod
    def from_json(cls, data: dict) -> "PreviousOutPoint":
        """Create a PreviousOutPoint instance from a JSON dictionary."""
        return cls(**data)

    def to_json(self) -> dict:
        """Convert a PreviousOutPoint instance to a JSON-compatible dictionary."""
        return asdict(self)


# Transaction class
@dataclass
class Transaction:
    tx_hash: str
    amount: int
    num_confirmations: int
    block_hash: str
    block_height: int
    time_stamp: int
    total_fees: int
    dest_addresses: Optional[List[str]]  # Marked deprecated, still included
    output_details: List[OutputDetail] = field(default_factory=list)
    raw_tx_hex: str = ''
    label: str = ''
    previous_outpoints: List[PreviousOutPoint] = field(default_factory=list)

    @classmethod
    def from_json(cls, data: dict) -> "Transaction":
        """Create a Transaction instance from a JSON dictionary."""
        output_details = [OutputDetail.from_json(od) for od in data.get("output_details", [])]
        previous_outpoints = [PreviousOutPoint.from_json(po) for po in data.get("previous_outpoints", [])]

        return cls(
            tx_hash=data["tx_hash"],
            amount=data["amount"],
            num_confirmations=data["num_confirmations"],
            block_hash=data["block_hash"],
            block_height=data["block_height"],
            time_stamp=data["time_stamp"],
            total_fees=data["total_fees"],
            dest_addresses=data.get("dest_addresses"),
            output_details=output_details,
            raw_tx_hex=data["raw_tx_hex"],
            label=data["label"],
            previous_outpoints=previous_outpoints,
        )

    def to_json(self) -> dict:
        """Convert a Transaction instance to a JSON-compatible dictionary."""
        return {
            "tx_hash": self.tx_hash,
            "amount": self.amount,
            "num_confirmations": self.num_confirmations,
            "block_hash": self.block_hash,
            "block_height": self.block_height,
            "time_stamp": self.time_stamp,
            "total_fees": self.total_fees,
            "dest_addresses": self.dest_addresses,
            "output_details": [od.to_json() for od in self.output_details],
            "raw_tx_hex": self.raw_tx_hex,
            "label": self.label,
            "previous_outpoints": [po.to_json() for po in self.previous_outpoints],
        }