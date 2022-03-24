## custom data class with the mongo specific ObjectId 
from pydantic import BaseModel, ValidationError, Field, validator
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
