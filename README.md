# IPData

IPData is a simple web application that provides geolocation data based on IP address or URL. 
The application is built using the Fastapi framework and uses the [ipstack](https://ipstack.com/) API to get geolocation data.

## Main python libraries used
- Fastapi
- SQLAlchemy
- Pydantic
- Uvicorn

## How to run the application
1. Clone the repository
2. Change value of `IP_STACK_ACCESS_KEY` in docker-compose.yml to your ipstack access key 
3. Run `docker compose up`
4. The application will be available at `http://localhost:8000`
5. The API documentation will be available at `http://localhost:8000/docs`

## API Endpoints
- `GET /ipdata/{ip_address}` - Get geolocation data based on IP address
- `POST /ipdata` - Add geolocation data based on IP address. The request body should have the following format:
```json
{
    "ip": "172.68.213.129"
}
```

- `POST /ipdata/manual` - Add geolocation data based on IP address manually. This endpoint should be used if there are some problems with connection to IPStack API.  
The request body should have the following format:
```json
{
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
    "msa": null,
    "dma": null,
    "radius": null,
    "ip_routing_type": "fixed",
    "connection_type": "tx",
    "location": {
        "geoname_id": 3067696,
        "capital": "Prague",
        "languages": [
            "cs",
            "sk"
        ],
        "country_flag": "https://assets.ipstack.com/flags/cz.svg",
        "country_flag_emoji": "🇨🇿",
        "country_flag_emoji_unicode": "U+1F1E8 U+1F1FF",
        "calling_code": "420",
        "is_eu": true
    }
}
```

- `DELETE /ipdata/{ip_address}` - Delete geolocation data based on IP address

## Database
The application uses PostgreSQL as the database. The database schema is created using SQLAlchemy.
There are two tables:
- `ipdata` - stores geolocation data based on IP address
- `location` - stores location data (X ip addresses can have the same location)

## Tests
The application has tests for all endpoints. There are also tests for IPStack client.
To run tests, use the following commands:
```bash
docker compose up -d
docker compose --profile test up pytest
```
Note: Please keep in mind that the tests will use the same database as the application. The database will be cleared before running the tests.


## Additional notes
### Unhappy path scenarios
- If the connection to the IPStack API fails, there will be a 502 (Bad gateway) error at the `POST /ipdata/` endpoint. To create geolocation data manually, use the `POST /ipdata/manual` endpoint. However, the application will be able to get/delete geolocations data based on IP address.
- If the connection to the database fails, there will be a 503 (Service unavailable) error. The application will not be able to serve any data.

### Future improvements
- Add more tests
- Add more IP data clients, for example [ipapi](https://ipapi.com/)
- Add more endpoints to get geolocation data based on URL
- Add OAuth2 authentication at create / delete endpoints
