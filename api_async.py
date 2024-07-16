
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from LeadScraperV2 import LeadScraper 
from json import loads
import multiprocessing
import asyncio
import uvicorn
import datetime
tokens=""
with open('tokens.json','r')as f:tokens=loads(f.read())
task=None
app=FastAPI()
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
    return {'status':'working..'}
    
@app.get("/add_queries")
async def get(niche:str,location:str,token:str,min:int,start:int):
        if(token in tokens):
             tries=tokens[token]['n']
             flag=False
             if(min>tries):min=tries
             elif(min<=0):return {'status':'param min should be greater than 0'}
             if(tries>0): 
                  try:
                   pos=scraper_ins.add((min,start,niche,location,'instagram.com',token))         
                   tries-=min
                   return {'status':f'Added your query to the queue at postion {pos}'}                    
                  except Exception as e:print(e)   
        else:return {'status':'Invalid Token Credentials'} 
        return {'status':'Invalid Query'}

@app.get("/get_file")
async def get(token:str):
     if(token in scraper_ins.files):
          if scraper_ins.files[token]:
              return FileResponse(f'./files/{token}.csv') 
          else: return {'status':'File is being edited'}      
     else:return {'status':'Invalid Token Credentials or File doesnt exist'}
       
    


if __name__ == "__main__":

 uvicorn.run(app, host="0.0.0.0", port=8000)
    
