from typing import Optional

from pydantic import BaseModel, IPvAnyAddress


class LanguagesData(BaseModel):
    code: str
    name: str
    native: str


class LocationData(BaseModel):
    geoname_id: int
    capital: str
    languages: list[LanguagesData]
    country_flag: str
    country_flag_emoji: str
    country_flag_emoji_unicode: str
    calling_code: str
    is_eu: bool


class IPData(BaseModel):
    ip: IPvAnyAddress
    type: str
    continent_code: str
    continent_name: str
    country_code: str
    country_name: str
    region_code: str
    region_name: str
    city: str
    zip: str
    latitude: float
    longitude: float
    msa: Optional[str]
    dma: Optional[str]
    radius: Optional[float]
    ip_routing_type: str
    connection_type: str
    location: LocationData
