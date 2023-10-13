import os

 

os.environ["SQLALCHEMY_WARN_20"] = "1"
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import List
from math import radians, sin, cos, sqrt, atan2


class AddressResponse(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float

 

 

DATABASE_URL = "sqlite:///./test.db"

 

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

 

app = FastAPI()

 

# Defining the Address model
class Address(Base):
    _tablename_ = "addresses"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    latitude = Column(Float)
    longitude = Column(Float)

 


Base.metadata.create_all(bind=engine)

 


class AddressCreate(BaseModel):
    name: str
    latitude: float
    longitude: float

 


class AddressInRadius(BaseModel):
    latitude: float
    longitude: float
    radius: float

 

 

 

@app.post("/addresses/", response_model=AddressResponse)
async def create_address(address: AddressCreate):
    db_address = Address(**address.dict())
    db = SessionLocal()
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    db.close()
    return db_address

 

@app.put("/addresses/{address_id}", response_model=AddressResponse)
async def update_address(address_id: int, address: AddressCreate):
    db = SessionLocal()
    db_address = db.query(Address).filter(Address.id == address_id).first()
    if db_address is None:
        db.close()
        raise HTTPException(status_code=404, detail="Address not found")
    for key, value in address.dict().items():
        setattr(db_address, key, value)
    db.commit()
    db.refresh(db_address)
    db.close()
    return db_address

 

@app.delete("/addresses/{address_id}", response_model=AddressResponse)
async def delete_address(address_id: int):
    db = SessionLocal()
    db_address = db.query(Address).filter(Address.id == address_id).first()
    if db_address is None:
        db.close()
        raise HTTPException(status_code=404, detail="Address not found")
    db.delete(db_address)
    db.commit()
    db.close()
    return db_address

 

@app.get("/addresses/", response_model=List[AddressResponse])
async def get_addresses(skip: int = 0, limit: int = 100):
    db = SessionLocal()
    addresses = db.query(Address).offset(skip).limit(limit).all()
    db.close()
    return addresses

 

@app.post("/addresses/in_radius/", response_model=List[AddressResponse])
async def get_addresses_in_radius(coords: AddressInRadius):
    db = SessionLocal()

 

    # Converting latitude and longitude to radians for calculation
    lat1 = radians(coords.latitude)
    lon1 = radians(coords.longitude)

 

  
    earth_radius = 6371.0

 

    addresses = []
    for address in db.query(Address).all():
        lat2 = radians(address.latitude)
        lon2 = radians(address.longitude)

 

      
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2)*2 + cos(lat1) * cos(lat2) * sin(dlon / 2)*2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = earth_radius * c

 

        # Checking if the calculated distance is within the specified radius
        if distance <= coords.radius:
            addresses.append(address)

 

    db.close()
    return addresses

 

if _name_ == "_main_":
    import uvicorn

 

    os.environ["SQLALCHEMY_WARN_20"] = "1"  
    uvicorn.run(app, host="127.0.0.1", port=4001)