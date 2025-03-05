from http import HTTPStatus
from typing import Any

import pytest
from fastapi.testclient import TestClient
from requests import Response
from sqlalchemy.orm import Session

from ipdata.models.ip_data import IPDataModel, LocationModel
from ipdata.services.ip_client.data import IPData
from ipdata.services.ip_client.exceptions import IpStackException
from tests.ipdata.responses import RESPONSE_NO_INFO, RESPONSE_OK, RESPONSE_OK2

BASIC_IP_ADDRESS = "172.68.213.129"


def when_user_create_ip_data(client: TestClient, ip_address: str) -> Response:
    response = client.post("/ipdata/", json={"ip": ip_address})
    return response


def when_user_get_ip_data_by_ip(client: TestClient, ip_address: str) -> Response:
    response = client.get(f"/ipdata/{ip_address}")
    return response


def when_user_delete_ip_data_by_ip(client: TestClient, ip_address: str) -> Response:
    response = client.delete(f"/ipdata/{ip_address}")
    return response


def when_user_create_ip_data_manually(client: TestClient, request_body: dict[str, Any]) -> Response:
    response = client.post("/ipdata/manual", json=request_body)
    return response


def then_response_should_be(res_status: HTTPStatus, res: Response) -> None:
    assert res.status_code == res_status, res.text


@pytest.mark.parametrize(
    "ip, api_stack_response",
    [
        ("172.68.213.129", IPData(**RESPONSE_OK)),
        ("192.168.1.0", IPData(**RESPONSE_OK)),
    ],
)
def test_create_ip_data(alice: TestClient, db_session, ip: str, api_stack_response: IPData, mocker):
    mocker.patch("ipdata.services.ip_client.ip_stack_client.IPStackClient.get_ip_data", return_value=api_stack_response)
    res = when_user_create_ip_data(alice, ip_address=ip)

    then_response_should_be(HTTPStatus.OK, res)


@pytest.mark.parametrize("ip", ["wrong.ip", "1.2.3"])
def test_create_ip_data_with_incorrect_ip_should_raise_error(alice: TestClient, db_session, ip: str):
    res = when_user_create_ip_data(alice, ip_address=ip)

    then_response_should_be(HTTPStatus.UNPROCESSABLE_CONTENT, res)


def test_create_ip_data_with_ip_already_exists_in_db_should_raise_error(alice: TestClient, db_session, mocker):
    ip_stack_response = IPData(**RESPONSE_OK)
    mocker.patch("ipdata.services.ip_client.ip_stack_client.IPStackClient.get_ip_data", return_value=ip_stack_response)

    res1 = when_user_create_ip_data(alice, ip_address=BASIC_IP_ADDRESS)
    then_response_should_be(HTTPStatus.OK, res1)

    res2 = when_user_create_ip_data(alice, ip_address=BASIC_IP_ADDRESS)
    then_response_should_be(HTTPStatus.BAD_REQUEST, res2)


def test_create_ip_data_with_ip_no_info_should_raise_bad_request(alice: TestClient, mocker):
    mocker.patch(
        "ipdata.services.ip_client.ip_stack_client.IPStackClient.get_ip_data",
        side_effect=IpStackException(code=999, err_type="no_ip_info", info="This IP address does not have any info."),
    )

    res = when_user_create_ip_data(alice, ip_address=BASIC_IP_ADDRESS)
    then_response_should_be(HTTPStatus.BAD_REQUEST, res)


def test_created_ip_data_record_should_have_proper_values_in_db(db_api: Session, alice, mocker):
    ip_stack_response = IPData(**RESPONSE_OK)
    mocker.patch("ipdata.services.ip_client.ip_stack_client.IPStackClient.get_ip_data", return_value=ip_stack_response)

    res = when_user_create_ip_data(alice, ip_address=BASIC_IP_ADDRESS)
    then_response_should_be(HTTPStatus.OK, res)

    ip_data = db_api.query(IPDataModel).filter(IPDataModel.ip == BASIC_IP_ADDRESS).first()
    assert ip_data is not None

    assert ip_data.ip == BASIC_IP_ADDRESS
    assert ip_data.type == ip_stack_response.type
    assert ip_data.continent_code == ip_stack_response.continent_code
    assert ip_data.continent_name == ip_stack_response.continent_name
    assert ip_data.country_code == ip_stack_response.country_code
    assert ip_data.country_name == ip_stack_response.country_name
    assert ip_data.region_code == ip_stack_response.region_code
    assert ip_data.region_name == ip_stack_response.region_name
    assert ip_data.city == ip_stack_response.city
    assert ip_data.zip == ip_stack_response.zip
    assert ip_data.latitude == ip_stack_response.latitude
    assert ip_data.longitude == ip_stack_response.longitude
    assert ip_data.msa == ip_stack_response.msa
    assert ip_data.dma == ip_stack_response.dma
    assert ip_data.radius == ip_stack_response.radius
    assert ip_data.ip_routing_type == ip_stack_response.ip_routing_type
    assert ip_data.connection_type == ip_stack_response.connection_type

    # assert languages
    db_location = db_api.get(LocationModel, ip_data.location_id)
    assert db_location is not None
    assert db_location.geoname_id == ip_stack_response.location.geoname_id
    assert db_location.capital == ip_stack_response.location.capital
    assert db_location.country_flag == ip_stack_response.location.country_flag
    assert db_location.country_flag_emoji == ip_stack_response.location.country_flag_emoji
    assert db_location.country_flag_emoji_unicode == ip_stack_response.location.country_flag_emoji_unicode
    assert db_location.calling_code == ip_stack_response.location.calling_code
    assert db_location.is_eu == ip_stack_response.location.is_eu
    assert db_location.languages == ";".join([language.code for language in ip_stack_response.location.languages])


def test_create_two_ips_data_records_should_have_the_same_location_record_in_db(
    db_api: Session, alice: TestClient, mocker
) -> None:
    for response in [RESPONSE_OK, RESPONSE_OK2]:
        ip_stack_response = IPData(**response)
        mocker.patch(
            "ipdata.services.ip_client.ip_stack_client.IPStackClient.get_ip_data", return_value=ip_stack_response
        )

        res = when_user_create_ip_data(alice, ip_address=str(ip_stack_response.ip))
        then_response_should_be(HTTPStatus.OK, res)

    assert db_api.query(IPDataModel).count() == 2
    assert db_api.query(LocationModel).count() == 1


def test_get_ip_data_by_ip_should_return_none_if_ip_not_exists_in_db(alice: TestClient) -> None:
    res = when_user_get_ip_data_by_ip(alice, ip_address=BASIC_IP_ADDRESS)
    then_response_should_be(HTTPStatus.NOT_FOUND, res)


def test_get_ip_data_by_ip_should_return_proper_data_if_ip_exists_in_db(alice: TestClient, mocker) -> None:
    ip_stack_response = IPData(**RESPONSE_OK)
    mocker.patch("ipdata.services.ip_client.ip_stack_client.IPStackClient.get_ip_data", return_value=ip_stack_response)

    res1 = when_user_create_ip_data(alice, ip_address=BASIC_IP_ADDRESS)
    then_response_should_be(HTTPStatus.OK, res1)

    res2 = when_user_get_ip_data_by_ip(alice, ip_address=BASIC_IP_ADDRESS)
    then_response_should_be(HTTPStatus.OK, res2)

    res_body = res2.json()

    assert res_body["ip"] == BASIC_IP_ADDRESS
    assert res_body["type"] == ip_stack_response.type
    assert res_body["continent_code"] == ip_stack_response.continent_code
    assert res_body["continent_name"] == ip_stack_response.continent_name
    assert res_body["country_code"] == ip_stack_response.country_code
    assert res_body["country_name"] == ip_stack_response.country_name
    assert res_body["region_code"] == ip_stack_response.region_code
    assert res_body["region_name"] == ip_stack_response.region_name
    assert res_body["city"] == ip_stack_response.city
    assert res_body["zip"] == ip_stack_response.zip
    assert res_body["latitude"] == ip_stack_response.latitude
    assert res_body["longitude"] == ip_stack_response.longitude
    assert res_body["msa"] == ip_stack_response.msa
    assert res_body["dma"] == ip_stack_response.dma
    assert res_body["radius"] == ip_stack_response.radius
    assert res_body["ip_routing_type"] == ip_stack_response.ip_routing_type
    assert res_body["connection_type"] == ip_stack_response.connection_type

    res_body_location = res_body["location"]
    assert res_body_location["geoname_id"] == ip_stack_response.location.geoname_id
    assert res_body_location["capital"] == ip_stack_response.location.capital
    assert res_body_location["country_flag"] == ip_stack_response.location.country_flag
    assert res_body_location["country_flag_emoji"] == ip_stack_response.location.country_flag_emoji
    assert res_body_location["country_flag_emoji_unicode"] == ip_stack_response.location.country_flag_emoji_unicode
    assert res_body_location["calling_code"] == ip_stack_response.location.calling_code
    assert res_body_location["is_eu"] == ip_stack_response.location.is_eu
    assert res_body_location["languages"] == ["cs", "sk"]


def test_delete_ip_data_by_ip_should_raise_not_found_if_ip_not_exists_in_db(alice: TestClient) -> None:
    res = when_user_delete_ip_data_by_ip(alice, ip_address=BASIC_IP_ADDRESS)
    then_response_should_be(HTTPStatus.NOT_FOUND, res)


def test_delete_ip_data_by_ip_should_return_ok_response_if_ip_was_in_db_and_remove_records_in_db(
    alice: TestClient, db_api: Session, mocker
) -> None:
    ip_stack_response = IPData(**RESPONSE_OK)
    mocker.patch("ipdata.services.ip_client.ip_stack_client.IPStackClient.get_ip_data", return_value=ip_stack_response)

    res1 = when_user_create_ip_data(alice, ip_address=BASIC_IP_ADDRESS)
    then_response_should_be(HTTPStatus.OK, res1)

    res2 = when_user_delete_ip_data_by_ip(alice, ip_address=BASIC_IP_ADDRESS)
    then_response_should_be(HTTPStatus.OK, res2)

    ip_data = db_api.query(IPDataModel).filter(IPDataModel.ip == BASIC_IP_ADDRESS).first()
    assert ip_data is None

    location = (
        db_api.query(LocationModel).filter(LocationModel.geoname_id == ip_stack_response.location.geoname_id).first()
    )
    assert location is None


def test_delete_ip_data_by_ip_should_remove_only_one_location_record_if_two_ips_are_using_the_same_location(
    alice: TestClient, db_api: Session, mocker
) -> None:
    for response in [RESPONSE_OK, RESPONSE_OK2]:
        ip_stack_response = IPData(**response)
        mocker.patch(
            "ipdata.services.ip_client.ip_stack_client.IPStackClient.get_ip_data", return_value=ip_stack_response
        )

        res = when_user_create_ip_data(alice, ip_address=str(ip_stack_response.ip))
        then_response_should_be(HTTPStatus.OK, res)

    assert db_api.query(LocationModel).count() == 1

    res = when_user_delete_ip_data_by_ip(alice, ip_address=str(RESPONSE_OK["ip"]))
    then_response_should_be(HTTPStatus.OK, res)

    assert db_api.query(LocationModel).count() == 1


@pytest.mark.parametrize(
    "request_body",
    [
        {},
        {"ip": BASIC_IP_ADDRESS},
        RESPONSE_OK,
    ],
)
def test_create_ip_data_manually_should_return_unprocessable_entity_if_request_is_incorrect(
    alice: TestClient, request_body: dict[str, Any]
) -> None:
    res = when_user_create_ip_data_manually(alice, request_body={})
    then_response_should_be(HTTPStatus.UNPROCESSABLE_CONTENT, res)


def test_create_ip_data_manually_with_proper_request_body_should_add_ip_to_db(
    alice: TestClient, db_session: Session
) -> None:
    request_body = {
        "ip": "172.68.213.129",
        "type": "ipv4",
        "continent_code": "EU",
        "continent_name": "Europe",
        "country_code": "CZ",
        "country_name": "Czechia",
        "region_code": "10",
        "region_name": "Hlavní město Praha",
        "city": "Prague",
        "zip": "106 00",
        "latitude": 50.087799072265625,
        "longitude": 14.420499801635742,
        "msa": None,
        "dma": None,
        "radius": None,
        "ip_routing_type": "fixed",
        "connection_type": "tx",
        "location": {
            "geoname_id": 3067696,
            "capital": "Prague",
            "languages": ["cs", "sk"],
            "country_flag": "https://assets.ipstack.com/flags/cz.svg",
            "country_flag_emoji": "🇨🇿",
            "country_flag_emoji_unicode": "U+1F1E8 U+1F1FF",
            "calling_code": "420",
            "is_eu": True,
        },
    }

    res = when_user_create_ip_data_manually(alice, request_body=request_body)

    then_response_should_be(HTTPStatus.OK, res)
