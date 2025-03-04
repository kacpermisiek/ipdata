from http import HTTPStatus
from uuid import UUID

from fastapi import HTTPException
from furl import furl
from pydantic import IPvAnyAddress
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from ipdata.models.ip_data import IPDataModel, LocationModel
from ipdata.schemas.ipdata import (
    IPDataCreateSchema,
    IPDataReturnSchema,
    LocationDataWithSimpleLanguages,
    IPDataCreateManuallySchema,
)
from ipdata.services.ip_client.data import IPData, LanguagesData, LocationData
from ipdata.services.ip_client.exceptions import IpStackException
from ipdata.services.ip_client.ip_stack_client import IPStackClient
from ipdata.settings import settings


def db_operations_wrapper():
    """
    This is decorator that wraps the function and catches sqlalchemy errors.
    :return:
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except OperationalError:
                raise HTTPException(
                    status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                    detail=f"Service is unavailable. Please try again later.",
                )

        return wrapper

    return decorator


@db_operations_wrapper()
def get_ip_data_schema(ip: IPvAnyAddress, db: Session) -> IPDataReturnSchema:
    ip_data = get_ip_data_by_ip(db, ip)
    if not ip_data:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="IP not found in the database")

    location = get_location_by_id(db, ip_data.location_id)
    return ip_data_entity_to_schema(ip_data, location)


@db_operations_wrapper()
def create_ip_data_schema(ip_create: IPDataCreateSchema, db: Session) -> IPDataReturnSchema:
    ip_exists_in_db = get_ip_data_by_ip(db, ip_create.ip)
    if ip_exists_in_db:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="IP already exists in the database")

    try:
        ip_data: IPData = IPStackClient(furl(settings.ip_stack_url)).get_ip_data(str(ip_create.ip))
    except IpStackException as e:
        raise get_exception_based_on_status_code(e.code)

    location = add_location_to_db(db, ip_data.location)
    ip_data_entity = create_ip_data_entity(ip_data, location, db)

    return ip_data_entity_to_schema(ip_data_entity, location)


@db_operations_wrapper()
def create_ip_data_manually_schema(ip_data: IPDataCreateManuallySchema, db: Session) -> IPDataReturnSchema:
    ip_exists_in_db = get_ip_data_by_ip(db, ip_data.ip)
    if ip_exists_in_db:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="IP already exists in the database")

    location = add_location_to_db(db, ip_data.location)
    ip_data_entity = create_ip_data_entity(ip_data, location, db)

    return ip_data_entity_to_schema(ip_data_entity, location)


@db_operations_wrapper()
def delete_ip_schema(ip: IPvAnyAddress, db: Session) -> HTTPStatus.OK:
    ip_data = get_ip_data_by_ip(db, ip)
    if not ip_data:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="IP not found in the database")

    location = get_location_by_id(db, ip_data.location_id)

    if not location_used_by_others(location, db):
        db.delete(location)

    db.delete(ip_data)
    db.commit()
    return HTTPStatus.OK


def get_ip_data_by_ip(db: Session, ip: IPvAnyAddress) -> IPDataModel | None:
    return db.query(IPDataModel).filter(IPDataModel.ip == str(ip)).one_or_none()


def get_location_by_geoname_id(db: Session, geoname_id: int) -> LocationModel | None:
    return db.query(LocationModel).filter(LocationModel.geoname_id == geoname_id).one_or_none()


def get_location_by_id(db, location_id: UUID) -> LocationModel | None:
    return db.get(LocationModel, location_id)


def generate_languages_string(languages: list[LanguagesData]) -> str:
    return ";".join([f"{lang.code}" for lang in languages])


def add_location_to_db(db: Session, location: LocationData) -> LocationModel:
    location_in_db = get_location_by_geoname_id(db, location.geoname_id)
    if location_in_db:
        return location_in_db

    else:
        if len(location.languages) > 0 and isinstance(location.languages[0], LanguagesData):
            languages = generate_languages_string(location.languages)
        else:
            languages = location.languages

        location = LocationModel(
            geoname_id=location.geoname_id,
            capital=location.capital,
            country_flag=location.country_flag,
            country_flag_emoji=location.country_flag_emoji,
            country_flag_emoji_unicode=location.country_flag_emoji_unicode,
            calling_code=location.calling_code,
            is_eu=location.is_eu,
            languages=languages,
        )
        db.add(location)
        db.commit()
        db.refresh(location)
        return location


def create_ip_data_entity(ip_data: IPData, location: LocationModel, db: Session):
    ip_data_entity = IPDataModel(
        ip=str(ip_data.ip),
        type=ip_data.type,
        continent_code=ip_data.continent_code,
        continent_name=ip_data.continent_name,
        country_code=ip_data.country_code,
        country_name=ip_data.country_name,
        region_code=ip_data.region_code,
        region_name=ip_data.region_name,
        city=ip_data.city,
        zip=ip_data.zip,
        latitude=ip_data.latitude,
        longitude=ip_data.longitude,
        msa=ip_data.msa,
        dma=ip_data.dma,
        radius=ip_data.radius,
        ip_routing_type=ip_data.ip_routing_type,
        connection_type=ip_data.connection_type,
    )
    ip_data_entity.location_id = location.id
    db.add(ip_data_entity)
    db.commit()
    db.refresh(ip_data_entity)
    return ip_data_entity


def ip_data_entity_to_schema(ip_data_entity: IPDataModel, location: LocationModel) -> IPDataReturnSchema:
    return IPDataReturnSchema(
        ip=IPvAnyAddress(ip_data_entity.ip),
        type=ip_data_entity.type,
        continent_code=ip_data_entity.continent_code,
        continent_name=ip_data_entity.continent_name,
        country_code=ip_data_entity.country_code,
        country_name=ip_data_entity.country_name,
        region_code=ip_data_entity.region_code,
        region_name=ip_data_entity.region_name,
        city=ip_data_entity.city,
        zip=ip_data_entity.zip,
        latitude=ip_data_entity.latitude,
        longitude=ip_data_entity.longitude,
        msa=ip_data_entity.msa,
        dma=ip_data_entity.dma,
        radius=ip_data_entity.radius,
        ip_routing_type=ip_data_entity.ip_routing_type,
        connection_type=ip_data_entity.connection_type,
        location=LocationDataWithSimpleLanguages(
            geoname_id=location.geoname_id,
            capital=location.capital,
            languages=[location for location in location.languages.split(";")],
            country_flag=location.country_flag,
            country_flag_emoji=location.country_flag_emoji,
            country_flag_emoji_unicode=location.country_flag_emoji_unicode,
            calling_code=location.calling_code,
            is_eu=location.is_eu,
        ),
    )


def get_exception_based_on_status_code(code: int) -> HTTPException:
    general_msg = "There is a problem with connection to the external service. Please try again later or try to use POST /ipdata/manual endpoint."
    match code:
        case 101:  # Invalid API Access Key
            return HTTPException(HTTPStatus.BAD_GATEWAY, general_msg)
        case 104:  # Monthly limit reached
            return HTTPException(HTTPStatus.BAD_REQUEST, general_msg)
        case 106:  # Invalid IP address or domain
            return HTTPException(HTTPStatus.BAD_REQUEST, "Invalid IP address or domain")
        case _:
            return HTTPException(HTTPStatus.BAD_GATEWAY, general_msg)


def location_used_by_others(location: LocationModel, db: Session) -> bool:
    return db.query(IPDataModel).filter(IPDataModel.location_id == location.id).count() > 1
