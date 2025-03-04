from typing import Any

import requests.exceptions
from pydantic import BaseModel, ValidationError

from ipdata.services.ip_client.base_ip_client import BaseIPClient
from ipdata.services.ip_client.data import IPData
from ipdata.services.ip_client.exceptions import IpStackException
from ipdata.settings import settings


class IPStackError(BaseModel):
    code: int
    type: str
    info: str


class IPStackErrorResponse(BaseModel):
    success: bool
    error: IPStackError


class IPStackClient(BaseIPClient):
    def get_ip_data(self, ip: str) -> IPData:
        response = self._fetch_from_api(ip)

        if isinstance(response, IPStackErrorResponse):
            raise IpStackException(
                code=response.error.code,
                err_type=response.error.type,
                info=response.error.info,
            )
        return response

    def _fetch_from_api(self, ip: str) -> IPData | IPStackErrorResponse:
        response = self._session.get(
            self._ip_url.join(ip),
            params={"access_key": settings.ip_stack_access_key.get_secret_value()},
        )
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise IpStackException(
                code=e.response.status_code,
                err_type="http_error",
                info=e.response.text,
            )

        return self._determine_response(response.json())

    def _determine_response(
        self,
        response: dict[str, Any],
    ) -> IPData | IPStackErrorResponse:
        try:
            return IPData(**response)
        except ValidationError:
            return self._create_error_response(response)

    @staticmethod
    def _create_error_response(response: dict[str, Any]) -> IPStackErrorResponse:
        try:
            return IPStackErrorResponse(**response)
        except ValidationError:
            return IPStackErrorResponse(
                success=False,
                error=IPStackError(
                    code=999,
                    type="unknown_error",
                    info="Unknown error occurred",
                ),
            )
