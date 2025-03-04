import uuid

from sqlalchemy import (
    BOOLEAN,
    DATETIME,
    FLOAT,
    INTEGER,
    Column,
    ForeignKey,
    ForeignKeyConstraint,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.types import UUID

from ipdata.db import Base


class IPDataModel(Base):
    __tablename__ = "ipdata"
    __table_args__ = (UniqueConstraint("ip"),)

    id = Column(UUID, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    ip = Column(String, index=True, nullable=False)
    type = Column(String)
    continent_code = Column(String)
    continent_name = Column(String)
    country_code = Column(String)
    country_name = Column(String)
    region_code = Column(String)
    region_name = Column(String)
    city = Column(String)
    zip = Column(String)
    latitude = Column(FLOAT)
    longitude = Column(FLOAT)
    msa = Column(String)
    dma = Column(String)
    radius = Column(FLOAT)
    ip_routing_type = Column(String)
    connection_type = Column(String)

    # Foreign keys
    location_id = Column(UUID, ForeignKey("location.id"))


class LocationModel(Base):
    __tablename__ = "location"
    __table_args__ = (UniqueConstraint("geoname_id"),)

    id = Column(UUID, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    geoname_id = Column(INTEGER, index=True, nullable=False)
    capital = Column(String)
    country_flag = Column(String)
    country_flag_emoji = Column(String)
    country_flag_emoji_unicode = Column(String)
    calling_code = Column(String)
    is_eu = Column(BOOLEAN)
    languages = Column(String)
