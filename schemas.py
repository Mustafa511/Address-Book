from pydantic import BaseModel


# Request body models
class AddressBook(BaseModel):
    latitude: float
    longitude: float
    name: str

class Coordinates(BaseModel):
    latitude: float
    longitude: float

class LocationByName(BaseModel):
    place_1: str
    place_2: str


class LocationByCoordinates(BaseModel):
    place_1_latitude: float
    place_1_longitude: float
    place_2_latitude: float
    place_2_longitude: float


# Response body models
class AddressBookResponse(BaseModel):
    aid: int
    latitude: float
    longitude: float
    name: str

    class Config:
        orm_mode = True

class DistanceResponse(BaseModel):
    distance: float

    class Config:
        orm_mode = True


class LocationsResponse(BaseModel):
    aid: int
    name: str
    distance: float

    class Config:
        orm_mode = True
