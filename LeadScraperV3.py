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
import traceback
from fake_useragent import UserAgent
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

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
        "--high-dpi-support=0.20",
        "--force-device-scale-factor=0.5",
        
        # '--disable-dev-shm-usage',
        # '--disable-background-timer-throttling',
        # '--disable-backgrounding-occluded-windows',
        # '--disable-breakpad',
        # '--disable-client-side-phishing-detection',
        # '--disable-component-extensions-with-background-pages',
        # '--disable-default-apps',
        # '--disable-extensions',
        # '--disable-features=site-per-process',
        # '--disable-hang-monitor',
        # '--disable-ipc-flooding-protection',
        # '--disable-popup-blocking',
        # '--disable-prompt-on-repost',
        # '--disable-renderer-backgrounding',
        # '--disable-sync',
        # '--no-sandbox',
        # '--disable-web-security',
        # '--disable-accelerated-2d-canvas',
        # '--disable-gpu',
        # '--disable-software-rasterizer',
        # '--disable-webgl',
        # '--disable-notifications',
        # '--disable-infobars',
        # '--disable-background-networking',
        # '--metrics-recording-only',
        # '--no-first-run'

        ]
import utils
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
            await asyncio.gather(*[self.fetch_search_results(await browser.new_context(user_agent=agent.random,viewport={'width':3000,'height':10000})) for i in range(0,10)])
            
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
    async def scrape_insta(self,page,link):
         await page.goto(link)
         #s2='section main section ul'
       
    async def fetch_search_results(self,context):
        page=await context.new_page()
        await stealth_async(page)
        print('[LOADED]:Context')
        while True:
            if not self.query_tasks.empty():      
              query=self.query_tasks.queue[0]
              counter = 0
              tries=6

              self.q=f"site:{query[4]}   {query[2]} based on {query[3]}  @gmail.com @yahoo.com @icloud.com  @outlook.com"
                  #f"site:{query[4]}  '@gmail.com' '{query[2]}' '{query[3]}' 'Followers' Following '@yahoo.com' '@icloud.com'  '@outlook.com'"))                  
              if(query[7]):await utils.geolocate(page,query[7])
              print('country',query[7])
              self.pg=query[1]
              self.min=query[0]
              uid=query[6]
              self.count=0

              while self.count<self.min and uid in self.files:
               if not tries:
                  print("TRIES:",'Exhausted')
                  break
               count = 0
               self.pg += 50
               if counter == 20:
                   await context.clear_cookies()
                   counter = 0

               url =f'https://www.bing.com/search?first={self.pg}&count=50&cc={query[7]}&q={self.q}&rdr=1' 
               
               try:
                await page.goto(url)
                await asyncio.sleep(5)
                if not await page.query_selector('.b_algo'):
                   try:
                    await page.click('#sb_form_go') 
                   except Exception as e:
                      print('Exception at 161:',print(page.url))
                      break
                await asyncio.sleep(5)
                await page.wait_for_load_state('load')  
                while True:
                 try:
                    soup = HTMLParser(await page.content(), 'html.parser').css('.b_algo')
                    break
                 except: await asyncio.sleep(2)
                self.count+= self.parse(soup,query[2],query[3])
               # print(self.count)
               except Exception as e:
                   print('Error:',traceback.format_exc())
               if(count):tries=6
               else:tries-=1 
               count = 0
               counter += 1
              if(uid in self.files):
               data=self.files.pop(uid)[2].values()
               self.query_tasks.get()  
               print(time.time()-self.ttime,self.count)
               self.count=0
               await self.write_results_to_csv(f'./files/{query[5]}_{query[6]}.csv',data)
            else:await asyncio.sleep(1)
    
    def parse(self,items,*args):
                count=0
                for item in items:
                    data_text = item.css_first('.b_caption').text()
                    email = re.search(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[+A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+', data_text)
                    email=email.group() if email else None
                    link =item.css_first('div.b_attribution cite')
                    link=link.text() if link else '' 
                    pattern = r'https:\/\/www\.instagram\.com\/([a-zA-Z0-9._-]+)(:\/(reel|p|reels|followers|follower|following).*)?\/?'
                    username=re.search(pattern,link)
                    
                    if username:
                          username=username.group(1)
                          if username in ('reel','p','reels','followers','follower','following'):username=''
                     
                    if (email and username) or username in self.files[uid][2] :
                        
                        following = re.search(r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?[KM]?) Following', data_text)
                        following = (following.group(1)).replace('K','000').replace('M','000000').replace(',','') if following else ''
                        followers = re.search(r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?[KM]?) Followers', data_text)
                        followers = (followers.group(1)).replace('K','000').replace('M','000000').replace(',','') if followers else ''
                        data=(username,email,following,followers,link,*args)
                        if username in self.files[uid][2]:
                            self.files[uid][2][username]=tuple(val1 if val1 else val2 for val1, val2 in zip(self.files[uid][2][username],data))
                              
                        elif uid in self.files:
                            count += 1
                            self.files[uid][0]+=1
                            self.files[uid][2][username]=data
                        else:break
                    
                return count        
           
    def add(self,data): 
            self.files[data[6]]=[0,data[0],{}]
            self.ttime=time.time()
            self.query_tasks.put(data)                  

if(__name__=='__main__'):
   
   ls=LeadScraper( )
   uid=str(uuid.uuid4())
   (ls.add([1000,1,'fitness','madrid','instagram.com','test_token',uid,'ES']))
   asyncio.run(ls.handler())
    