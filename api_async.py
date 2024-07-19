
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse,JSONResponse
import os
from LeadScraperV3 import LeadScraper 
from json import loads
import asyncio
import uvicorn
import uuid
tokens=""

with open('tokens.json','r')as f:tokens=loads(f.read())
task=None
app=FastAPI(docs_url="/docs")
scraper_ins=LeadScraper()
app.mount("/static", StaticFiles(directory="./static/"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def start():
     loop=asyncio.get_running_loop()
     task=loop.create_task(scraper_ins.handler())

"""@asynccontextmanager
async def lifespan(app: FastAPI):
     loop=asyncio.get_running_loop()
     task=loop.create_task(scraper_ins.handler())
     yield
"""
@app.get('/')
async def get():
    return JSONResponse({'status':'working..'},status_code=200)
    
@app.get("/add_queries")
async def get(niche:str,location:str,token:str,country_code:str=None,min:int=10,start:int=0,tlim:int=120):
        if(token in tokens):
             tries=tokens[token]['n']
             if(min>tries):min=tries
             elif(min<=0):return JSONResponse(status_code=400,content={'status':'param min should be greater than 0'})
             if(tries>0): 
                   uid=str(uuid.uuid4())
                   print(f'http://localhost:8000/get_file?token=aabf3e2e-488f-4d63-8eae-df0b6f729f3d&uid={uid}')
                   scraper_ins.add((min,start,niche,location,'instagram.com',token,uid,country_code,tlim))         
                   tokens[token]['n']-=min
                   return JSONResponse(status_code=200,content={'status':f'Added your query to the queue ','uuid':uid,'attempts_left':tokens[token]['n'],'target':min})                     
        else:return JSONResponse(status_code=401,content={'status':'Invalid Token Credentials'}) 
        return JSONResponse(status_code=400,content={'status':'Invalid Query'})

@app.get("/get_file")
async def get(token:str,uid:str):
     if(token in tokens):
              uid=uid.replace('//','')
              if uid in scraper_ins.files:
                    return JSONResponse(status_code=200,content={'status':'File is being generated',
                                                                 'count':scraper_ins.files[uid][0],
                                                                 'requested':scraper_ins.files[uid][1],
                                                                 'total':scraper_ins.files[uid][3],'time_taken':scraper_ins.files[uid][3]}) 
              file_path=f'./files/{token}_{uid}.csv'
              if(os.path.exists(file_path)):return FileResponse(file_path,status_code=200) 
              else:return JSONResponse(status_code=404,content={'status':'File doesnt exist'})
              
     else:return JSONResponse(status_code=401,content={'status':'Invalid Token Credentials'})
       
    


if __name__ == "__main__":

 uvicorn.run(app, host="0.0.0.0", port=8000)
    
