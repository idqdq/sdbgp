from fastapi import FastAPI, Request, Response, Body, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import List
from gobgp_api import AddPath, DelPath, ListPath
from models import PxDataClass, PathDataClass

app = FastAPI()

## mongo start
# first we'll be using fake data thus we could develop the frontend part of app without access to the real switchfabric
# to store and retrieve such date mongodb is being used
import motor.motor_asyncio

@app.on_event("startup")
async def create_db_client():
    mdbclient = motor.motor_asyncio.AsyncIOMotorClient()
    app.db = mdbclient.sdbgp

@app.on_event("shutdown")
async def shutdown_db_client():
    # stop your client here
    app.db.close()

## mongo end

## CORS
origins = [    
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
## CORS end

## FastAPI Routes
@app.get("/px", response_model=List[PathDataClass])
async def getPrefixesAll():
    prefixes = []
        
    async for px in app.db.px.find({}):
        px.pop("_id")
        #print(px)
        prefixes.append(PathDataClass(**px))
    
    return prefixes


@app.get("/px/{ip}", response_model=PathDataClass)  
async def getPrefix(ip: str):
    if (px := await app.db.px.find_one({"ip": ip})) is not None:
        px.pop("_id")
        return PathDataClass(**px)

    raise HTTPException(status_code=404, detail=f"Prefix with ID: {id} not found")


@app.post("/px")
async def createPx(px: PathDataClass = Body(...)):
    px = jsonable_encoder(px)    
    
    new_px = await app.db.px.insert_one(px)
    created_px = await app.db.px.find_one({"_id": new_px.inserted_id})
    created_px.pop("_id")

    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_px)

@app.post("/px/bulk")
async def createBulkPx(pxlist: List[PathDataClass]):
    pxlist = jsonable_encoder(pxlist)    
    
    for px in pxlist:
        new_px = await app.db.px.insert_one(px)      

    return JSONResponse(status_code=status.HTTP_201_CREATED, content="Ok")

@app.put("/px/{ip}", response_description="Update prefix", response_model=PathDataClass)
async def updatePx(ip: str, px: PxDataClass = Body(...)):
    px = jsonable_encoder(px)
    # update model shoudn't include _id because mongo will not allow mutate _id in update procedure 
    # so we have to create another data class for the update or just get rid of _id from the existed model 
    px.pop("_id") 
    
    if (existed_px := await app.db.px.find_one({"ip": ip})) is not None:        
        update_res = await app.db.px.update_one({"_id": existed_px["_id"] }, {"$set": px})
        if update_res.modified_count == 1:
            result = await app.db.px.find_one({"ip": ip})
        else: 
            result = existed_px
        result.pop("_id")
    else: 
        raise HTTPException(status_code=404, detail=f"Prefix {px['ip']} not found")
    
    print(result)
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)
  

@app.delete("/px/{ip}", response_description="Delete Prefix")
async def deletePx(ip: str):
    delete_res = await app.db.px.delete_one({"ip": ip})
    if delete_res.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Prefix {ip} not found")


### GoBGP API Section ###
@app.post("/gobgp/add") # adds prefix into gobgp
async def gobgp_addpath(px: PathDataClass = Body(...)):
    AddPath(px)


@app.post("/gobgp/del") # deletes prefix from gobgp
async def gobgp_delpath(px: PathDataClass = Body(...)):
    DelPath(px)


@app.get("/gobgp/list") # returns all the prefixes from within gobgp
async def gobgp_listall():    
    result = ListPath()
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)


@app.get("/gobgp/delallfromdb") # Deletes all the prefixes from GoBGP existing in Mongo 
async def gobgp_dumpAll():
    async for px in app.db.px.find({}):   
        px.pop("_id")     
        DelPath(PathDataClass(**px))


@app.get("/gobgp/delallrib") # Deletes all the prefixes from GoBGP
async def gobgp_delallrib():
    paths = ListPath()
    if paths:
        for px in paths:                                    
            DelPath(PathDataClass(**px))
            

### GoBGP to/from Mongo API section ###
@app.get("/gobgp/db2rib") # Puts all the prefixes from Mongo to GoBGP
async def gobgp_db2rib():
    async for px in app.db.px.find({}): 
        px.pop("_id")       
        AddPath(PathDataClass(**px))


@app.get("/gobgp/rib2db") # Loads all the prefixes from GoBGP to Mongo
async def gobgp_rib2db():    
    paths = ListPath()
    if paths:
        await app.db.px.drop({})
        for path in paths:                        
            new_px = await app.db.px.insert_one(path)             
    return JSONResponse(status_code=status.HTTP_200_OK, content="OK")       


@app.get("/gobgp/cleardb") # Loads all the prefixes from GoBGP to Mongo
async def gobgp_cleardb():    
    await app.db.px.drop({})    
    return JSONResponse(status_code=status.HTTP_200_OK, content="OK")       
