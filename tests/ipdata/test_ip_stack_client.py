from typing import Any

import furl
import pytest
from pydantic import IPvAnyAddress
from requests import Response

from ipdata.services.ip_client.data import IPData
from ipdata.services.ip_client.exceptions import IpStackException
from ipdata.services.ip_client.ip_stack_client import IPStackClient, IPStackErrorResponse
from tests.ipdata.responses import (
    RESPONSE_INVALID_ACCESS_KEY,
    RESPONSE_INVALID_IP_ADDRESS,
    RESPONSE_LIMIT_REACHED,
    RESPONSE_NO_INFO,
    RESPONSE_OK,
)

IP_STACK_URL = "https://example.com"


class FakeIPStackClient(IPStackClient):
    def __init__(self, ip_url: furl, fake_response: dict[str, Any]) -> None:
        self._fake_response = fake_response
        super().__init__(ip_url)

    def _fetch_from_api(self, ip: str) -> IPData | IPStackErrorResponse:
        return self._determine_response(self._fake_response)


class ErrorIPStackClient(IPStackClient):
    def __init__(self, ip_url: furl, fake_response: Response) -> None:
        self._response = fake_response
        super().__init__(ip_url)

    def _fetch_from_api(self, ip: str) -> IPData | IPStackErrorResponse:
        response = self._response
        response.raise_for_status()
        return self._determine_response(response)


def test_ip_stack_client_should_return_proper_ipdata_object_if_ip_found() -> None:
    client = FakeIPStackClient(IP_STACK_URL, fake_response=RESPONSE_OK)
    ip_data = client.get_ip_data("ok.ip")

    assert isinstance(ip_data, IPData)
    assert ip_data.ip == IPvAnyAddress(RESPONSE_OK["ip"])
    assert ip_data.type == RESPONSE_OK["type"]
    assert ip_data.continent_code == RESPONSE_OK["continent_code"]
    assert ip_data.continent_name == RESPONSE_OK["continent_name"]
    assert ip_data.country_code == RESPONSE_OK["country_code"]
    assert ip_data.country_name == RESPONSE_OK["country_name"]
    assert ip_data.region_code == RESPONSE_OK["region_code"]
    assert ip_data.region_name == RESPONSE_OK["region_name"]
    assert ip_data.city == RESPONSE_OK["city"]
    assert ip_data.zip == RESPONSE_OK["zip"]
    assert ip_data.latitude == RESPONSE_OK["latitude"]
    assert ip_data.longitude == RESPONSE_OK["longitude"]
    assert ip_data.msa == RESPONSE_OK["msa"]
    assert ip_data.dma == RESPONSE_OK["dma"]
    assert ip_data.radius == RESPONSE_OK["radius"]
    assert ip_data.ip_routing_type == RESPONSE_OK["ip_routing_type"]
    assert ip_data.connection_type == RESPONSE_OK["connection_type"]
    assert ip_data.location.geoname_id == RESPONSE_OK["location"]["geoname_id"]
    assert ip_data.location.capital == RESPONSE_OK["location"]["capital"]
    assert len(ip_data.location.languages) == 2
    assert ip_data.location.languages[0].code == RESPONSE_OK["location"]["languages"][0]["code"]
    assert ip_data.location.languages[0].name == RESPONSE_OK["location"]["languages"][0]["name"]
    assert ip_data.location.languages[0].native == RESPONSE_OK["location"]["languages"][0]["native"]
    assert ip_data.location.languages[1].code == RESPONSE_OK["location"]["languages"][1]["code"]
    assert ip_data.location.languages[1].name == RESPONSE_OK["location"]["languages"][1]["name"]
    assert ip_data.location.languages[1].native == RESPONSE_OK["location"]["languages"][1]["native"]
    assert ip_data.location.country_flag == RESPONSE_OK["location"]["country_flag"]
    assert ip_data.location.country_flag_emoji == RESPONSE_OK["location"]["country_flag_emoji"]
    assert ip_data.location.country_flag_emoji_unicode == RESPONSE_OK["location"]["country_flag_emoji_unicode"]
    assert ip_data.location.calling_code == RESPONSE_OK["location"]["calling_code"]
    assert ip_data.location.is_eu == RESPONSE_OK["location"]["is_eu"]


@pytest.mark.parametrize(
    "response, expected_code",
    [
        (RESPONSE_INVALID_ACCESS_KEY, 101),
        (RESPONSE_INVALID_IP_ADDRESS, 106),
        (RESPONSE_LIMIT_REACHED, 104),
        (RESPONSE_NO_INFO, 999),
    ],
)
def test_ip_stack_client_should_raise_invalid_access_key_exception(
    response: dict[str, Any], expected_code: int
) -> None:
    client = FakeIPStackClient(IP_STACK_URL, fake_response=response)

    with pytest.raises(IpStackException) as e:
        client.get_ip_data("whatever")
    assert e.value.code == expected_code
