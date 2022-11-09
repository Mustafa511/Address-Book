from typing import List

from fastapi import FastAPI, Depends
from sqlalchemy.exc import DBAPIError, DataError
from sqlalchemy.orm import Session

import database
import models
import schemas
from helper_functions import get_distance

app = FastAPI()
# Creating the database and the table within it if it does not exist
models.Base.metadata.create_all(bind=database.engine)


# Create a new address and inserting it into the database based on the schema
@app.post('/create', description="Add a new address to the database", response_model=schemas.AddressBookResponse)
def add_new_address(request: schemas.AddressBook, db: Session = Depends(database.get_db)):
    new_address = models.AddressBook(latitude=request.latitude, longitude=request.longitude, name=request.name.strip())
    db.add(new_address)
    db.commit()
    db.refresh(new_address)
    return new_address


# Get the distance between two addresses names from the database.
@app.get('/distance/coordinates', description="Get the distance between two coordinates.",
         response_model=float)
def calculate_distance(request: schemas.LocationByCoordinates = Depends()):
    # Calling the helper function to calculate the distance between two coordinates
    distance_kms = get_distance(request.place_1_latitude, request.place_1_longitude, request.place_2_latitude,
                                request.place_2_longitude)
    return round(distance_kms, 2)


# Get the distance between two addresses names from the database.
# This function is assuming that the names are unique.
@app.get('/distance/names', description="Get the distance between two places saved in the database.",
         response_model=float)
def calculate_distance(request: schemas.LocationByName = Depends(), db: Session = Depends(database.get_db)):
    # Calling the helper function to calculate the distance between two coordinates
    geo_1 = db.query(models.AddressBook).filter(models.AddressBook.name == request.place_1).first()
    geo_2 = db.query(models.AddressBook).filter(models.AddressBook.name == request.place_2).first()
    distance_kms = get_distance(geo_1.latitude, geo_1.longitude, geo_2.latitude, geo_2.longitude)
    return round(distance_kms, 2)


# Get all the locations from the database that are within a certain distance from a given location
@app.get('/locations/within',
         description="Get all the locations from the database that are within a certain distance from a given location",
         response_model=List[schemas.LocationsResponse])
def places_within_range(kms: float, coords: schemas.Coordinates = Depends(), db: Session = Depends(database.get_db)):
    # Get all the locations from the database using the coordinates and the distance
    query = f'''SELECT
                    aid, name,round(
                      (6371 * acos (
                      cos ( radians({coords.latitude}) )
                      * cos( radians( latitude ) )
                      * cos( radians( longitude ) - radians({coords.longitude}) )
                      + sin ( radians({coords.latitude}) )
                      * sin( radians( latitude ) )
                    )),2
                    ) AS distance
                FROM addressbook
                WHERE distance <= {kms}
                ORDER BY distance;'''
    result = db.execute(query).fetchall()
    return result[1:]


# Get locations between two coordinates
@app.get('/locations/between', description="Get locations between two coordinates",
         response_model=List[schemas.AddressBookResponse])
def places_between_range(request: schemas.LocationByCoordinates = Depends(), db: Session = Depends(database.get_db)):
    # Get all the locations from the database between two coordinates
    query = f'''SELECT * FROM addressbook
                WHERE latitude BETWEEN {request.place_1_latitude} AND {request.place_2_latitude}
                AND longitude BETWEEN  {request.place_1_longitude} AND {request.place_2_longitude};'''
    result = db.execute(query).fetchall()
    print(f"Result: {result}")
    return result


# Delete a location from the database
@app.delete('/delete/{name}', description="Delete a location from the database", response_model=dict)
def delete(name: str, db: Session = Depends(database.get_db)):
    try:
        item = db.query(models.AddressBook).filter(models.AddressBook.name == name).first()
        if item:
            db.delete(item)
            db.commit()
            return {"message": "Deleted Successfully"}
        return {"message": "Place does not exist"}
    except DataError:
        return {"message": "Not Deleted"}
    except DBAPIError:
        return {"message": "Not Deleted"}


# Update a location in the database
@app.put('/update/{name}', description="Update a location in the database", response_model=dict)
def update(name: str, request: schemas.AddressBook, db: Session = Depends(database.get_db)):
    try:
        item = db.query(models.AddressBook).filter(models.AddressBook.name == name).first()
        if item:
            item.latitude = request.latitude if request.latitude > 0 else item.latitude
            item.longitude = request.longitude if request.longitude > 0 else item.longitude
            item.name = request.name.strip()
            db.commit()
            return {"message": "Updated Successfully"}
        return {"message": "Place does not exist"}
    except DataError:
        return {"message": "Not Updated"}
