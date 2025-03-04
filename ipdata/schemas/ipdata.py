from pydantic import BaseModel, Field, IPvAnyAddress
from pydantic.config import ConfigDict

from ipdata.services.ip_client.base_ip_client import IPData
from ipdata.services.ip_client.data import LocationData


class IPDataCreateSchema(BaseModel):
    ip: IPvAnyAddress = Field(IPvAnyAddress, examples=["172.68.213.129"])


class LocationDataWithSimpleLanguages(LocationData):
    languages: list[str]


class IPDataSchema(IPData):
    location: LocationDataWithSimpleLanguages


class IPDataCreateManuallySchema(IPDataSchema): ...


class IPDataReturnSchema(IPDataSchema):

    model_config = ConfigDict(
        from_attributes=True,
    )
