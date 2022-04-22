from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI, Response, Request, Depends, Body, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import List
from datetime import datetime, timedelta
from gobgp_api_flowspec import AddPathFlowSpec, DelPathFlowSpec, ListPathFlowSpec
from gobgp_api_unicast import AddPathUnicast, DelPathUnicast, ListPathUnicast
from models import PathDataClass, FlowSpecDataClass, UserBase, UserIn, UserInDB
from config import Settings
from auth import authenticate, create_access_token, get_current_user, get_password_hash

app = FastAPI()
settings = Settings()

## mongo start
@app.on_event("startup")
async def create_db_client():
    app.mdbclient = AsyncIOMotorClient(f"mongodb://{settings.MONGO_HOST}:{settings.MONGO_PORT}")    
    app.db = app.mdbclient.sdbgp    

@app.on_event("shutdown")
async def shutdown_db_client():
    # stop your client here    
    # app.mbclient.close()
    pass
## mongo end


## CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],        
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )    

print(settings)
## CORS end


## FastAPI Routes
### Auth Section
# takes a data object and returns a JWT token 
@app.post("/token")
async def gettoken(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):            
    user = await authenticate(request, user=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")  # 3
    
    access_token_expires = timedelta(days=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(data=user, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/signin")
async def signin(data: UserIn):      
    if await app.db.user.find_one({"user":data.user}) is not None:
        raise HTTPException(status_code=400,
                            detail="The user {data.user} already exists in the system",)

    newuser = UserInDB(user=data.user, 
            hashed_password=get_password_hash(data.password), 
            created=datetime.utcnow(),
            is_superuser=data.is_superuser)

    await app.db.user.insert_one(jsonable_encoder(newuser))
    if await app.db.user.find_one({"user":newuser.user}) is not None:
        return {"message": "user created"}
    
    raise HTTPException(status_code=404, detail=f"can't create user {data.user}. probably due to DB error")


@app.get("/me", response_model=UserBase)
async def read_users_me(current_user: UserBase = Depends(get_current_user)):
    return current_user


### MongoDB API Section ###
@app.get("/mongo/unicast", response_model=List[PathDataClass])
async def getPxAll():
    prefixes = []
        
    async for px in app.db.unicast.find({}):
        px.pop("_id")        
        prefixes.append(PathDataClass(**px))
    
    return prefixes

@app.get("/mongo/flowspec", response_model=List[FlowSpecDataClass])
async def getFlowspecAll():
    prefixes = []
        
    async for px in app.db.flowspec.find({}):
        px.pop("_id")        
        prefixes.append(FlowSpecDataClass(**px))
    
    return prefixes  


@app.get("/mongo/unicast/{src}", response_model=PathDataClass)  
async def getPx(src: str):
    if (px := await app.db.unicast.find_one({"src": src})) is not None:
        px.pop("_id")
        return PathDataClass(**px)
    raise HTTPException(status_code=404, detail=f"Prefix with ID: {src} not found")

@app.get("/mongo/flowspec/{src:path}", response_model=FlowSpecDataClass)  
async def getFlowspec(src: str):
    if (px := await app.db.flowspec.find_one({"src": src})) is not None:
        px.pop("_id")
        return FlowSpecDataClass(**px)
    raise HTTPException(status_code=404, detail=f"Policy with ID: {src} not found")


@app.post("/mongo/unicast")
async def createPx(px: PathDataClass = Body(...)):        
    await app.db.unicast.insert_one(jsonable_encoder(px))
    return JSONResponse(status_code=status.HTTP_201_CREATED)

@app.post("/mongo/flowspec")
async def createFlowspec(px: FlowSpecDataClass = Body(...)):       
    await app.db.flowspec.insert_one(jsonable_encoder(px))    
    return JSONResponse(status_code=status.HTTP_201_CREATED)


@app.post("/mongo/unicast/bulk")
async def createBulkPx(pxlist: List[PathDataClass]):
    pxlist = jsonable_encoder(pxlist)    
    
    for px in pxlist:
        new_px = await app.db.unicast.insert_one(px)      

    return JSONResponse(status_code=status.HTTP_201_CREATED, content="Ok")

@app.put("/mongo/unicast/{src}", response_description="Update prefix", response_model=PathDataClass)
async def updatePx(src: str, px: PathDataClass = Body(...)):
    px = jsonable_encoder(px)
    
    if (existed_px := await app.db.unicast.find_one({"src": src})) is not None:        
        update_res = await app.db.unicast.update_one({"_id": existed_px["_id"] }, {"$set": px})
        if update_res.modified_count == 1:
            result = await app.db.unicast.find_one({"src": src})
        else: 
            result = existed_px
        result.pop("_id")
    else: 
        raise HTTPException(status_code=404, detail=f"Prefix {px['src']} not found")
 
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

@app.put("/mongo/flowspec/{src:path}", response_description="Update flowspec policy", response_model=FlowSpecDataClass)
async def updateFlowspec(src: str, px: FlowSpecDataClass = Body(...)):
    px = jsonable_encoder(px)    

    if (existed_px := await app.db.flowspec.find_one({"src": src})) is not None:        
        update_res = await app.db.flowspec.update_one({"_id": existed_px["_id"] }, {"$set": px})
        if update_res.modified_count == 1:
            result = await app.db.flowspec.find_one({"src": src})
        else: 
            result = existed_px
        result.pop("_id")
    else: 
        raise HTTPException(status_code=404, detail=f"Policy with src:{px['src']} not found")
    
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)


@app.delete("/mongo/unicast/{src}", response_description="Delete Prefix")
async def deletePx(src: str):
    delete_res = await app.db.unicast.delete_one({"src": src})
    if delete_res.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Prefix {src} not found")

@app.delete("/mongo/flowspec/{src:path}", response_description="Delete flowspec policy")
async def deleteFlowspec(src: str):
    delete_res = await app.db.flowspec.delete_one({"src": src})
    if delete_res.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Flowspec policy with src:{src} not found")


### GoBGP API Section ###
@app.get("/gobgp/unicast/list") # returns all the prefixes from within gobgp
async def gobgp_listall():    
    result = ListPathUnicast()
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

@app.get("/gobgp/flowspec/list") # returns all the prefixes from within gobgp
async def gobgp_listall_flowspec():    
    result = ListPathFlowSpec()
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(result))


@app.post("/gobgp/unicast/add") # adds prefix into gobgp
async def gobgp_addpath(px: PathDataClass = Body(...)):
    AddPathUnicast(px)

@app.post("/gobgp/flowspec/add") # adds prefix into gobgp
async def gobgp_addpath_flowspec(px: FlowSpecDataClass = Body(...)):
    AddPathFlowSpec(px)


@app.post("/gobgp/unicast/del") # deletes prefix from gobgp
async def gobgp_delpath(px: PathDataClass = Body(...)):
    DelPathUnicast(px)

@app.post("/gobgp/flowspec/del") # deletes prefix from gobgp
async def gobgp_delpath_flowspec(px: FlowSpecDataClass = Body(...)):
    DelPathFlowSpec(px)


@app.get("/gobgp/unicast/delallrib") # Deletes all the unicast prefixes from GoBGP
async def gobgp_unicast_delallrib():
    paths = ListPathUnicast()
    if paths:
        for px in paths:                                    
            DelPathUnicast(PathDataClass(**px))

@app.get("/gobgp/flowspec/delallrib") # Deletes all the flowspec prefixes from GoBGP
async def gobgp_flowspec_delallrib():
    paths = ListPathFlowSpec()
    if paths:
        for px in paths:                                    
            DelPathFlowSpec(px)
            

### GoBGP to/from Mongo API section ###
@app.get("/gobgp/unicast/rib2db") # Loads all the unicast prefixes from GoBGP to Mongo
async def gobgp_unicast_rib2db():    
    paths = ListPathUnicast()
    if paths:
        await app.db.unicast.drop({})
        for path in paths:                        
            new_px = await app.db.unicast.insert_one(path)             
    return JSONResponse(status_code=status.HTTP_200_OK, content="OK")       

@app.get("/gobgp/flowspec/rib2db") # Loads all the flowspec prefixes from GoBGP to Mongo
async def gobgp_flowspec_rib2db():    
    paths = ListPathFlowSpec()
    if paths:
        await app.db.flowspec.drop({})
        for path in paths:                        
            new_px = await app.db.flowspec.insert_one(jsonable_encoder(path))
    return JSONResponse(status_code=status.HTTP_200_OK, content="OK")       


@app.get("/gobgp/unicast/db2rib") # Puts all the unicast prefixes from Mongo to GoBGP
async def gobgp_unicast_db2rib():
    async for px in app.db.unicast.find({}): 
        px.pop("_id")       
        AddPathUnicast(PathDataClass(**px))

@app.get("/gobgp/flowspec/db2rib") # Puts all the flowspec prefixes from Mongo to GoBGP
async def gobgp_flowspec_db2rib():
    async for px in app.db.flowspec.find({}): 
        px.pop("_id")       
        AddPathFlowSpec(FlowSpecDataClass(**px))


@app.get("/gobgp/unicast/cleardb") # Drop the unicast Mongo table (collection)
async def gobgp_unicast_cleardb():    
    await app.db.unicast.drop({})    
    return JSONResponse(status_code=status.HTTP_200_OK, content="OK")    

@app.get("/gobgp/flowspec/cleardb") # Drop the flowspec Mongo table (collection)
async def gobgp_flowspec_cleardb():    
    await app.db.flowspec.drop({})    
    return JSONResponse(status_code=status.HTTP_200_OK, content="OK")       
