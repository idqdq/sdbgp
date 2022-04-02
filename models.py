## custom data class with the mongo specific ObjectId 
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from bson import ObjectId
from ipaddress import IPv4Address

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class PxDataClass(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    # mandatory data
    ip: IPv4Address
    mask_cidr: int = Field(32, ge=16, le=32)  # default mask = 32
    next_hop: str = "null"
    # optional data

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "ip": "1.2.3.4",
                "mask_cidr": "32",
                "next_hop": "1.1.1.1"
            }
        }

    @validator("next_hop")
    def v_next_hop(cls, v):
        if v != "null":
            assert IPv4Address(v), "next hop should be a valid IPv4 address"            
        return v


class PathDataClass(BaseModel):
    ip: str
    mask_cidr: int = Field(32, ge=16, le=32)
    next_hop: str

    class Config:
        schema_extra = {
            "example": {
                "ip": "1.2.3.4",
                "mask_cidr": "32",
                "next_hop": "1.1.1.1"
            }
        }

class FlowSpecDataClass(BaseModel):
    src: str
    src_prefix_len: int
    dst: Optional[str] = ''
    dst_prefix_len: Optional[int] = 0
    src_ports: Optional[str] = ''
    dst_ports: Optional[str] = ''
    protocols: Optional[List[str]] = ''
    rate_limit: int = 0

    class Config:
        schema_extra = {
            "example": {
                "src": "1.2.3.4",
                "src_prefix_len": "32",
                "dst": "10.20.30.0",
                "dst_prefix_len": "24",
                "src_ports": "1024-65535",
                "dst_ports": "80, 443, 5000-6000",
                "protocols": ["tcp", "udp"],
                "rate_limit": 0
            }
        }

