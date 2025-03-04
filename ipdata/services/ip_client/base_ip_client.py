from abc import ABC, abstractmethod

from furl import furl
from requests import Session

from ipdata.services.ip_client.data import IPData


class BaseIPClient(ABC):
    def __init__(self, ip_url: furl):
        self._ip_url = ip_url
        self._session = Session()

    @abstractmethod
    def get_ip_data(self, ip: str) -> IPData: ...
