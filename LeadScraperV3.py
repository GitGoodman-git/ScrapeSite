import aiohttp as aio
import asyncio
from random import choice,randint
from selectolax.parser import HTMLParser
import re,aiofiles
import time
import os
from json import dumps
from aiocsv import AsyncWriter
import uuid
from fake_useragent import UserAgent
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
import urllib.parse as up
import queue
proxy = {
    "server": os.environ.get('PROXY_SERVER'),
    "username":os.environ.get('USER_NAME'),
    "password":os.environ.get('PASSWD'),
}
agent=UserAgent()
args=[
        '--deny-permission-prompts',
        '--no-default-browser-check',
        '--no-nth-run',
        '--disable-features=NetworkService',
        '--deny-permission-prompts',
        '--disable-popup-blocking',
        '--ignore-certificate-errors',
        '--no-service-autorun',
        '--password-store=basic',
        '--disable-audio-output',
        '--blink-settings=imagesEnabled=false'
        '--blink-settings=fonts=!',
        '--disable-javascript',
        "--high-dpi-support=0.50",
        "--force-device-scale-factor=0.50"
        ]
headers={
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    'Accept-Encoding':'gzip, deflate, br, zstd',
    'Cache-Control':'no-cache',
    'Accept-Charset': 'utf-8',
    'DNT': '1'
}



class LeadScraper():
    def __init__(self,proxy=None):
        self.data=[]
        self.data_=[]
        self.files={}
        self.proxy=proxy
        self.min=10
        self.pg=1
        self.flg=0
        self.query_tasks=queue.Queue()
        
        
    async def handler(self):
            
        async with async_playwright() as playwright:  
            browser = await playwright.chromium.launch(args=args,proxy=self.proxy,headless=True) 
            await asyncio.gather(*[self.fetch_search_results(await browser.new_context(user_agent=agent.random,viewport={'width':800,'height':1024})) for i in range(0,10)])
            
    async def send_json_to_webhook(self,url,niche,location,site,t,p,s,n):
     data=dumps({'niche':niche,
                 'location':location,
                 'site':site,
                 'time':t,
                 '_pos':p,
                 '_start':s,
                 '_n':n,
                 'data':self.data[:n]                 
                 })
     
     async with aio.ClientSession() as session:
        async with session.post(url, json=data) as response:
          print(response.status)
    
    async def write_results_to_csv(self,filename,data):
     async with aiofiles.open(filename, 'a', newline='', encoding='utf-8') as file:
        writer = AsyncWriter(file)
        await writer.writerow(['username','email','following','followers','link','niche','location']) 
        await writer.writerows(data)
        print('[WRITE]:',filename)
    
      
    async def fetch_search_results(self,context):
        page=await context.new_page()
        await stealth_async(page)
        
        while True:
            if not self.query_tasks.empty():      
              query=self.query_tasks.queue[0]
              counter = 0
              tries=20
              self.q= choice((
                  f"site:{query[4]}  @gmail.com {query[2]} {query[3]} Followers Following @yahoo.com @icloud.com  @outlook.com",
                  f"site:{query[4]}  '@gmail.com' '{query[2]}' '{query[3]}' 'Followers' Following '@yahoo.com' '@icloud.com'  '@outlook.com'"))                  
              self.pg=query[1]
              self.min=query[0]
              uid=query[6]
              self.count=0
              while self.count<self.min and tries and uid in self.files:
               count = 0
               self.pg += 50
               if counter == 20:
                   await context.clear_cookies()
                   counter = 0

               url =f'https://www.bing.com/search?first={self.pg}&count=50&q={self.q}&rdr=1' 
               try:
                await page.goto(url)
                await asyncio.sleep(3)
                if not await page.query_selector('.b_algo'):
                   await page.click('.b_searchbox') 
                   await page.keyboard.press('Enter') 
                   await asyncio.sleep(1)
                await page.wait_for_load_state('load')  
                await asyncio.sleep(2)
                
                soup = HTMLParser(await page.content(), 'html.parser').css('.b_algo')
                for item in soup:
                    data_text = item.text()
                    email = re.search(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[+A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+', data_text)
                    link=''
                    username=''
                    link =item.css_first('a').attributes['href'] 
                    try:username=link.split('/')[-2]
                    except:pass
                    
                    following = re.search(r'\b\d+[A-Z]*\s+Following\b', data_text)
                    following = (following.group())[:-9] if following else ""
                    followers = re.search(r'\b\d+[A-Z]*\s+Followers\b', data_text)
                    followers = (followers.group())[:-9] if followers else ""
                    if email:
                        count += 1
                        email = following = email.group()
                        if uid in self.files:
                            self.files[uid][0]+=1
                            self.files[uid][1].append((username,email,following,followers,link,query[2],query[3]))
                        else:break
                    #else:self.data_.append((link.split('/')[-2], link, '', following, followers))              
                self.count+= count
                if(count):tries=3
                else:tries-=1 
                count = 0
                counter += 1
               except Exception as e:pass
              if(uid in self.files):
               data=self.files.pop(uid)[2]
               self.query_tasks.get()  
               print(time.time()-self.ttime,self.count)
               self.count=0
               await self.write_results_to_csv(f'./files/{query[5]}_{query[6]}.csv',data)
            else:await asyncio.sleep(1)
    def add(self,data): 
            self.files[data[6]]=[0,data[0],[]]
            self.ttime=time.time()
            self.query_tasks.put(data)                  

if(__name__=='__main__'):
   
   ls=LeadScraper( )
   uid=str(uuid.uuid4())
   (ls.add([10,1,'fitness','haldwani','instagram.com','test_token',uid]))
   asyncio.run(ls.handler())
    