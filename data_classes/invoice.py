from dataclasses import dataclass, field, asdict
from typing import List, Optional
import json


@dataclass
class HopHint:
    node_id: str
    chan_id: str
    fee_base_msat: int
    fee_proportional_millionths: int
    cltv_expiry_delta: int

    @classmethod
    def from_json(cls, data: dict) -> "HopHint":
        return cls(**data)

    def to_json(self) -> dict:
        return asdict(self)


@dataclass
class RouteHint:
    hop_hints: List[HopHint] = field(default_factory=list)

    @classmethod
    def from_json(cls, data: dict) -> "RouteHint":
        hop_hints = [HopHint.from_json(hh) for hh in data.get("hop_hints", [])]
        return cls(hop_hints=hop_hints)

    def to_json(self) -> dict:
        return {"hop_hints": [hh.to_json() for hh in self.hop_hints]}

@dataclass
class CustomRecordsEntry:
    key: int
    value: bytes
    @classmethod
    def from_json(cls, data: dict) -> "CustomRecordsEntry":
        return cls(**data)
    def to_json(self) -> dict:
        return asdict(self)
    
@dataclass
class AMP:
    root_share: str
    set_id: str
    child_index: int
    hash: str
    preimage: str

    @classmethod
    def from_json(cls, data: dict) -> "AMP":
        return cls(**data)
    
    def to_json(self) -> dict:
        return asdict(self)
    
@dataclass
class Htlc:
    chan_id: Optional[str] = None
    amt_msat: Optional[int] = None
    accept_time: Optional[str] = None
    resolve_time: Optional[str] = None
    accept_height: Optional[int] = None
    htlc_index: Optional[int] = None
    expiry_height: Optional[int] = None
    state: Optional[str] = None
    custom_records: List[CustomRecordsEntry] = field(default_factory=list)
    mpp_total_amt_msat: Optional[str] = None
    amp: Optional[AMP] = None 
    custom_channel_data: Optional[str] = None


    @classmethod
    def from_json(cls, data: dict) -> "Htlc":
        return cls(**data)

    def to_json(self) -> dict:
        return asdict(self)


@dataclass
class Feature:
    key: str
    value: bool

    @classmethod
    def from_json(cls, data: dict) -> "Feature":
        return cls(**data)

    def to_json(self) -> dict:
        return asdict(self)


@dataclass
class AmpInvoiceState:
    state: str
    timestamp: str

    @classmethod
    def from_json(cls, data: dict) -> "AmpInvoiceState":
        return cls(**data)

    def to_json(self) -> dict:
        return asdict(self)

@dataclass
class AmpInvoiceStateEntry:
    key: str
    value: AmpInvoiceState

    @classmethod
    def from_json(cls, data:dict) -> "AmpInvoiceStateEntry":
     return cls(key=data['key'],value=AmpInvoiceState.from_json(data=data['value']))
    
    def to_json(self) -> dict:
     return asdict(self)
@dataclass
class BlindedPathConfig:
    min_num_real_hops: int
    num_hops: int
    max_num_paths: int
    node_ommision_list: list

    @classmethod
    def from_json(cls, data: dict) -> "BlindedPathConfig":
        return cls(**data)

    def to_json(self) -> dict:
        return asdict(self)


@dataclass
class Invoice:
    memo: str
    r_preimage: str
    r_hash: str
    value: int
    settled: bool
    creation_date: str
    payment_request: str
    expiry: int
    cltv_expiry: int
    state: str

    # Optional or nested fields
    value_msat: Optional[int] = None
    settle_date: Optional[str] = None
    description_hash: Optional[str] = None
    fallback_addr: Optional[str] = None
    route_hints: Optional[List[RouteHint]] = field(default_factory=list)
    private: Optional[bool] = None
    add_index: Optional[int] = None
    settle_index: Optional[int] = None
    amt_paid: Optional[int] = None
    amt_paid_sat: Optional[int] = None
    amt_paid_msat: Optional[int] = None
    htlcs: Optional[List[Htlc]] = field(default_factory=list)
    features: Optional[List[Feature]] = field(default_factory=list)
    is_keysend: Optional[bool] = None
    payment_addr: Optional[str] = None
    is_amp: Optional[bool] = None
    amp_invoice_state: Optional[AmpInvoiceStateEntry] = None
    is_blinded: Optional[bool] = None
    blinded_path_config: Optional[BlindedPathConfig] = None

    @classmethod
    def from_json(cls, data: dict) -> "Invoice":
        return cls(
            memo=data["memo"],
            r_preimage=data["r_preimage"],
            r_hash=data["r_hash"],
            value=data["value"],
            settled=data["settled"],
            creation_date=data["creation_date"],
            payment_request=data["payment_request"],
            expiry=data["expiry"],
            cltv_expiry=data["cltv_expiry"],
            state=data["state"],
            value_msat=data.get("value_msat"),
            settle_date=data.get("settle_date"),
            description_hash=data.get("description_hash"),
            fallback_addr=data.get("fallback_addr"),
            route_hints=[RouteHint.from_json(rh) for rh in data.get("route_hints", [])],
            private=data.get("private"),
            add_index=data.get("add_index"),
            settle_index=data.get("settle_index"),
            amt_paid=data.get("amt_paid"),
            amt_paid_sat=data.get("amt_paid_sat"),
            amt_paid_msat=data.get("amt_paid_msat"),
            htlcs=[Htlc.from_json(htlc) for htlc in data.get("htlcs", [])],
            features=[feat for feat in data.get("features", [])],
            is_keysend=data.get("is_keysend"),
            payment_addr=data.get("payment_addr"),
            is_amp=data.get("is_amp"),
            amp_invoice_state=AmpInvoiceStateEntry.from_json(data["amp_invoice_state"])
            if data.get("amp_invoice_state")
            else None,
            is_blinded=data.get("is_blinded"),
            blinded_path_config=BlindedPathConfig.from_json(data["blinded_path_config"])
            if data.get("blinded_path_config")
            else None,
        )

    def to_json(self) -> dict:
        return {
            "memo": self.memo,
            "r_preimage": self.r_preimage,
            "r_hash": self.r_hash,
            "value": self.value,
            "settled": self.settled,
            "creation_date": self.creation_date,
            "payment_request": self.payment_request,
            "expiry": self.expiry,
            "cltv_expiry": self.cltv_expiry,
            "state": self.state,
            "value_msat": self.value_msat,
            "settle_date": self.settle_date,
            "description_hash": self.description_hash,
            "fallback_addr": self.fallback_addr,
            "route_hints": [rh.to_json() for rh in self.route_hints],
            "private": self.private,
            "add_index": self.add_index,
            "settle_index": self.settle_index,
            "amt_paid": self.amt_paid,
            "amt_paid_sat": self.amt_paid_sat,
            "amt_paid_msat": self.amt_paid_msat,
            "htlcs": [htlc.to_json() for htlc in self.htlcs],
            "features": [feature for feature in self.features],
            "is_keysend": self.is_keysend,
            "payment_addr": self.payment_addr,
            "is_amp": self.is_amp,
            "amp_invoice_state": self.amp_invoice_state.to_json() if self.amp_invoice_state else None,
            "is_blinded": self.is_blinded,
            "blinded_path_config": self.blinded_path_config.to_json() if self.blinded_path_config else None,
        }
