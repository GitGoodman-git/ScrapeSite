import asyncio
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
        "--force-device-scale-factor=0.7",
        
        '--disable-dev-shm-usage',
        '--disable-background-timer-throttling',
        '--disable-backgrounding-occluded-windows',
        '--disable-breakpad',
        '--disable-client-side-phishing-detection',
        '--disable-component-extensions-with-background-pages',
        '--disable-default-apps',
        '--disable-extensions',
        '--disable-features=site-per-process',
        '--disable-hang-monitor',
        '--disable-ipc-flooding-protection',
        '--disable-popup-blocking',
        '--disable-prompt-on-repost',
        '--disable-renderer-backgrounding',
        '--disable-sync',
        '--no-sandbox',
        '--disable-web-security',
        '--disable-accelerated-2d-canvas',
        '--disable-gpu',
        '--disable-software-rasterizer',
        '--disable-webgl',
        '--disable-notifications',
        '--disable-infobars',
        '--disable-background-networking',
        '--metrics-recording-only',
        '--no-first-run'

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

import urllib.parse as up

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
        self.up=3

        self.d=[]
        
    async def handler(self):
            
        async with async_playwright() as playwright:  
            browser = await playwright.chromium.launch(args=args,proxy=self.proxy,headless=False) 
            await asyncio.gather(*[self.fetch_search_results(await browser.new_context(user_agent=agent.random,viewport={'width':1000,'height':10000})) for i in range(0,self.up+2)])
            
    # async def send_json_to_webhook(self,url,niche,location,site,t,p,s,n):
    #  data=dumps({'niche':niche,
    #              'location':location,
    #              'site':site,
    #              'time':t,
    #              '_pos':p,
    #              '_start':s,
    #              '_n':n,
    #              'data':self.data[:n]                 
    #              })
     
    #  async with aio.ClientSession() as session:
    #     async with session.post(url, json=data) as response:
    #       print(response.status)
    
    async def write_results_to_csv(self,filename,data):
     print(f"[CREATE]:Generating file....{filename}")
     async with aiofiles.open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = AsyncWriter(file)
        await writer.writerow(['username','email','following','followers','link','niche','location']) 
        await writer.writerows(data)
        print('[WRITE]:',filename)
    async def scrape_insta(self,page,link):
         await page.goto(link)
         #s2='section main section ul'
       
    async def fetch_search_results(self,context):
       try: 
        page=await context.new_page()
        await stealth_async(page)
        print('[LOADED]:Context')
        while True:
            if not self.query_tasks.empty():      
              query=self.query_tasks.queue[0]
              counter = 0
              tries=3
              self.q=(f'"@gmail.com"+ followers or following and {query[2]}+ {query[3]}+   site:instagram.com')
              
                  #f"site:{query[4]}  '@gmail.com' '{query[2]}' '{query[3]}' 'Followers' Following '@yahoo.com' '@icloud.com'  '@outlook.com'"))                  
             
              if(query[7]):await utils.geolocate(page,query[7])
              uid=query[6]
              self.count=0
              self.ctime=0
              
              while self.count<self.min and uid in self.files and tries and self.tlim>self.ctime:
               self.pg+=10
               url =f'https://www.bing.com/search?count=50&first={self.pg}&go={self.q}&q={self.q}&rdr=1&FORM=PORE'
               count = 0
               if counter == 20:
                   await context.clear_cookies()
                   counter = 0   
               try:
                await page.goto(url)
                await asyncio.sleep(4)
                
                if not await page.query_selector('.b_algo'):
                   try:await page.click('#sb_form_go') 
                   except Exception as e: 
                      context.clear_cookies()
                      print('Exception at 161:',print(page.url))
                   await asyncio.sleep(2)

                await page.wait_for_load_state('load')  
                while True:
                 try:
                    await page.wait_for_load_state('load') 
                    items = HTMLParser(await page.content(), 'html.parser').css('.b_algo')
                    self.pg+=len(items)
                    break
                 except:await asyncio.sleep(2)
                count=self.parse(items,uid,query[2],query[3])
                self.count+=count
                print(count,self.count,self.pg) 
                if(count):tries=3
                else:tries-=1 
                counter += 1 
               except KeyError:pass 
               except Exception as e:print('Error:',traceback.format_exc())
               self.ctime=time.time()-self.ttime
              
              self.flg+=1

              while(self.flg<self.up):await asyncio.sleep(2)
              if(uid in self.files and self.flg>=self.up):
                 data=list(self.files.pop(uid)[2].values())[:self.min]
                 self.query_tasks.get()  
                 print(self.ctime,self.count)
                 data=self.files.pop(uid)[2].values()
                 self.files[uid][3]=self.pg
                 self.query_tasks.get()  
                 self.count=0
                 self.flg=0
                 fname=f'./files/{query[5]}_{query[6]}'
                 await asyncio.gather(self.write_results_to_csv(f'{fname}.csv',data),self.write_results_to_csv(f'{fname}_raw.csv',self.d))
               
            else:await asyncio.sleep(1)
       except:pass
    def parse(self,items,uid,*args):
                count=0
                for item in items:
                    data_text = item.css_first('.b_caption').text()
                    email = re.search(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[+A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+', data_text)
                    email=email.group() if email else None
                    link =item.css_first('div.b_attribution cite')
                    link=link.text() if link else '' 
                    pattern = r'https:\/\/www\.instagram\.com\/([a-zA-Z0-9._-]+)(:\/(reel|p|reels|followers|follower|following).*)?\/?'
                    username=re.search(pattern,link)
                    following = re.search(r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?[KM]?) Following', data_text)
                    following = (following.group(1)).replace('K','000').replace('M','000000').replace(',','') if following else ''
                    followers = re.search(r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?[KM]?) Followers', data_text)
                    followers = (followers.group(1)).replace('K','000').replace('M','000000').replace(',','') if followers else ''
                    username=username.group(1) if username else None
                    if username in ('reel','p','reels','followers','follower','following'):username=None  
                    if email and username and followers:                   
                     if  email not in self.files[uid][2]:
                        if followers:
                         data=(username,email,following,followers,link,*args)
                         if uid in self.files:
                            count += 1
                            self.files[uid][2][username]=data
                         else:break
                    self.d.append((username,email,following,followers,link,*args))
                    
                self.files[uid][0]+=count   
                return count        
           
    def add(self,data): 
            self.pg=data[1]-10
            self.min=data[0]
            self.tlim=data[8]
            self.files[data[6]]=[0,data[0],{},0,0]
            self.ttime=time.time()
            self.query_tasks.put(data)                  

if(__name__=='__main__'):
   
   ls=LeadScraper( )
   uid=str(uuid.uuid4())
   (ls.add([10,1,'fitness','madrid','instagram.com','test_token',uid,'ES',160]))
   asyncio.run(ls.handler())
    