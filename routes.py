from sys import prefix
from fastapi import FastAPI, Request, Response, Body, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import List, Union
from gobgp_api_unicast import AddPath, DelPath, ListPath
from models import PxDataClass, PathDataClass, FlowSpecDataClass

app = FastAPI()

## mongo start
# first we'll be using fake data thus we could develop the frontend part of app without access to the real switchfabric
# to store and retrieve such date mongodb is being used
import motor.motor_asyncio

@app.on_event("startup")
async def create_db_client():
    mdbclient = motor.motor_asyncio.AsyncIOMotorClient()
    app.db = mdbclient.sdbgp
    app.unicast = app.db.unicast
    app.flowspec = app.db.flowspec

@app.on_event("shutdown")
async def shutdown_db_client():
    # stop your client here
    #app.db.logout()
    pass

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
### MongoDB API Section ###

@app.get("/mongo/unicast", response_model=List[PathDataClass])
async def getPxAll():
    prefixes = []
        
    async for px in app.unicast.find({}):
        px.pop("_id")        
        prefixes.append(PathDataClass(**px))
    
    return prefixes

@app.get("/mongo/flowspec", response_model=List[FlowSpecDataClass])
async def getFlowspecAll():
    prefixes = []
        
    async for px in app.flowspec.find({}):
        px.pop("_id")        
        prefixes.append(FlowSpecDataClass(**px))
    
    return prefixes


@app.get("/mongo/unicast/{src}", response_model=PathDataClass)  
async def getPx(src: str):
    if (px := await app.unicast.find_one({"src": src})) is not None:
        px.pop("_id")
        return PathDataClass(**px)
    raise HTTPException(status_code=404, detail=f"Prefix with ID: {src} not found")

@app.get("/mongo/flowspec/{src:path}", response_model=FlowSpecDataClass)  
async def getFlowspec(src: str):
    if (px := await app.flowspec.find_one({"src": src})) is not None:
        px.pop("_id")
        return FlowSpecDataClass(**px)
    raise HTTPException(status_code=404, detail=f"Policy with ID: {src} not found")


@app.post("/mongo/unicast")
async def createPx(px: PathDataClass = Body(...)):        
    await app.unicast.insert_one(jsonable_encoder(px))
    return JSONResponse(status_code=status.HTTP_201_CREATED)

@app.post("/mongo/flowspec")
async def createFlowspec(px: FlowSpecDataClass = Body(...)):       
    await app.flowspec.insert_one(jsonable_encoder(px))    
    return JSONResponse(status_code=status.HTTP_201_CREATED)


@app.post("/mongo/unicast/bulk")
async def createBulkPx(pxlist: List[PathDataClass]):
    pxlist = jsonable_encoder(pxlist)    
    
    for px in pxlist:
        new_px = await app.unicast.insert_one(px)      

    return JSONResponse(status_code=status.HTTP_201_CREATED, content="Ok")



@app.put("/mongo/unicast/{src}", response_description="Update prefix", response_model=PathDataClass)
async def updatePx(src: str, px: PathDataClass = Body(...)):
    px = jsonable_encoder(px)
    
    if (existed_px := await app.unicast.find_one({"src": src})) is not None:        
        update_res = await app.unicast.update_one({"_id": existed_px["_id"] }, {"$set": px})
        if update_res.modified_count == 1:
            result = await app.unicast.find_one({"src": src})
        else: 
            result = existed_px
        result.pop("_id")
    else: 
        raise HTTPException(status_code=404, detail=f"Prefix {px['src']} not found")
    
    print(result)
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

@app.put("/mongo/flowspec/{src:path}", response_description="Update flowspec policy", response_model=FlowSpecDataClass)
async def updateFlowspec(src: str, px: FlowSpecDataClass = Body(...)):
    px = jsonable_encoder(px)    

    if (existed_px := await app.flowspec.find_one({"src": src})) is not None:        
        update_res = await app.flowspec.update_one({"_id": existed_px["_id"] }, {"$set": px})
        if update_res.modified_count == 1:
            result = await app.flowspec.find_one({"src": src})
        else: 
            result = existed_px
        result.pop("_id")
    else: 
        raise HTTPException(status_code=404, detail=f"Policy with src:{px['src']} not found")
    
    print(result)
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)


@app.delete("/mongo/unicast/{src}", response_description="Delete Prefix")
async def deletePx(src: str):
    delete_res = await app.unicast.delete_one({"src": src})
    if delete_res.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Prefix {src} not found")

@app.delete("/mongo/flowspec/{src:path}", response_description="Delete flowspec policy")
async def deleteFlowspec(src: str):
    delete_res = await app.flowspec.delete_one({"src": src})
    if delete_res.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Flowspec policy with src:{src} not found")


### GoBGP API Section ###
@app.post("/gobgp/unicast/add") # adds prefix into gobgp
async def gobgp_addpath(px: PathDataClass = Body(...)):
    AddPath(px)


@app.post("/gobgp/unicast/del") # deletes prefix from gobgp
async def gobgp_delpath(px: PathDataClass = Body(...)):
    DelPath(px)


@app.get("/gobgp/unicast/list") # returns all the prefixes from within gobgp
async def gobgp_listall():    
    result = ListPath()
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)


@app.get("/gobgp/unicast/delallfromdb") # Deletes all the prefixes from GoBGP existing in Mongo 
async def gobgp_dumpAll():
    async for px in app.unicast.find({}):   
        px.pop("_id")     
        DelPath(PathDataClass(**px))


@app.get("/gobgp/unicast/delallrib") # Deletes all the prefixes from GoBGP
async def gobgp_delallrib():
    paths = ListPath()
    if paths:
        for px in paths:                                    
            DelPath(PathDataClass(**px))
            

### GoBGP to/from Mongo API section ###
@app.get("/gobgp/unicast/db2rib") # Puts all the prefixes from Mongo to GoBGP
async def gobgp_db2rib():
    async for px in app.unicast.find({}): 
        px.pop("_id")       
        AddPath(PathDataClass(**px))


@app.get("/gobgp/unicast/rib2db") # Loads all the prefixes from GoBGP to Mongo
async def gobgp_rib2db():    
    paths = ListPath()
    if paths:
        await app.unicast.drop({})
        for path in paths:                        
            new_px = await app.unicast.insert_one(path)             
    return JSONResponse(status_code=status.HTTP_200_OK, content="OK")       


@app.get("/gobgp/unicast/cleardb") # Loads all the prefixes from GoBGP to Mongo
async def gobgp_cleardb():    
    await app.unicast.drop({})    
    return JSONResponse(status_code=status.HTTP_200_OK, content="OK")       
