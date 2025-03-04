RESPONSE_INVALID_IP_ADDRESS = {
    "success": False,
    "error": {
        "code": 106,
        "type": "invalid_ip_address",
        "info": "The IP Address supplied is invalid.",
    },
}


RESPONSE_OK = {
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
        "languages": [
            {"code": "cs", "name": "Czech", "native": "Čeština"},
            {"code": "sk", "name": "Slovak", "native": "Slovenčina"},
        ],
        "country_flag": "https://assets.ipstack.com/flags/cz.svg",
        "country_flag_emoji": "🇨🇿",
        "country_flag_emoji_unicode": "U+1F1E8 U+1F1FF",
        "calling_code": "420",
        "is_eu": True,
    },
}

RESPONSE_OK2 = {
    "ip": "172.68.213.128",
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
        "languages": [
            {"code": "cs", "name": "Czech", "native": "Čeština"},
            {"code": "sk", "name": "Slovak", "native": "Slovenčina"},
        ],
        "country_flag": "https://assets.ipstack.com/flags/cz.svg",
        "country_flag_emoji": "🇨🇿",
        "country_flag_emoji_unicode": "U+1F1E8 U+1F1FF",
        "calling_code": "420",
        "is_eu": True,
    },
}


RESPONSE_INVALID_ACCESS_KEY = {
    "success": False,
    "error": {
        "code": 101,
        "type": "invalid_access_key",
        "info": "You have not supplied a valid API Access Key. [Technical Support: support@apilayer.com]",
    },
}

RESPONSE_LIMIT_REACHED = {
    "success": False,
    "error": {
        "code": 104,
        "type": "monthly_limit_reached",
        "info": "Your monthly API request volume has been reached. Please upgrade your plan.",
    },
}


RESPONSE_NO_INFO = {
    "ip": "255.68.213.121",
    "type": "ipv4",
    "continent_code": None,
    "continent_name": None,
    "country_code": None,
    "country_name": None,
    "region_code": None,
    "region_name": None,
    "city": None,
    "zip": None,
    "latitude": 0.0,
    "longitude": 0.0,
    "msa": None,
    "dma": None,
    "radius": None,
    "ip_routing_type": None,
    "connection_type": None,
    "location": {
        "geoname_id": None,
        "capital": None,
        "languages": None,
        "country_flag": None,
        "country_flag_emoji": None,
        "country_flag_emoji_unicode": None,
        "calling_code": None,
        "is_eu": None,
    },
}
