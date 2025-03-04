from http import HTTPStatus
from http.client import HTTPResponse

from fastapi import Depends, FastAPI, HTTPException
from pydantic import IPvAnyAddress
from sqlalchemy.orm import Session

from ipdata.app.utils import create_ip_data_schema, delete_ip_schema, get_ip_data_schema, create_ip_data_manually_schema
from ipdata.db import get_db
from ipdata.schemas.ipdata import IPDataCreateSchema, IPDataReturnSchema, IPDataCreateManuallySchema

app = FastAPI()


@app.post("/ipdata/", response_model=IPDataReturnSchema, description="Create IP data based on external API response")
def create_ip_data(ip_create: IPDataCreateSchema, db: Session = Depends(get_db())):
    return create_ip_data_schema(ip_create, db)


@app.post("/ipdata/manual", response_model=IPDataReturnSchema, description="Manually create IP data based on request")
def create_ip_data_manually(ip_data: IPDataCreateManuallySchema, db: Session = Depends(get_db())):
    return create_ip_data_manually_schema(ip_data, db)


@app.get("/ipdata/{ip}", response_model=IPDataReturnSchema, description="Get IP data based on IP address")
def get_ip_data(ip: IPvAnyAddress, db: Session = Depends(get_db())):
    return get_ip_data_schema(ip, db)


@app.delete("/ipdata/{ip}", description="Delete IP data")
def delete_ip_data(ip: IPvAnyAddress, db: Session = Depends(get_db())):
    return delete_ip_schema(ip, db)
