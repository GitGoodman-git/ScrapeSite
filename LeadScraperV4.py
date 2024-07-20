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
               '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-infobars',
            '--disable-dev-shm-usage',
            '--start-maximized',
            '--deny-permission-prompts',
            '--no-default-browser-check',
            '--no-nth-run',
            '--disable-features=NetworkService',
            '--disable-popup-blocking',
            '--ignore-certificate-errors',
            '--no-service-autorun',
            '--password-store=basic',
            '--disable-audio-output',
            '--blink-settings=imagesEnabled=false',
            '--blink-settings=fonts=!',
            '--disable-javascript',
            '--high-dpi-support=0.20',
            '--force-device-scale-factor=0.3',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-breakpad',
            '--disable-client-side-phishing-detection',
            '--disable-component-extensions-with-background-pages',
            '--disable-default-apps',
            '--blink-settings=imagesEnabled=false',
            '--disable-extensions',
            '--disable-features=site-per-process',
            '--disable-hang-monitor',
            '--disable-ipc-flooding-protection',
            '--disable-popup-blocking',
            '--disable-prompt-on-repost',
            '--disable-renderer-backgrounding',
            '--disable-sync',
            '--disable-web-security',
            '--disable-accelerated-2d-canvas',
            '--disable-gpu',
            '--disable-software-rasterizer',
            '--disable-webgl',
            '--disable-notifications',
            '--disable-background-networking',
            '--metrics-recording-only',
            '--no-first-run',
            '--incognito'
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
import aiohttp as aio

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
        self.up=10
        self.d=[]
        
    async def handler(self):
            
        async with async_playwright() as playwright:  
            browser = await playwright.chromium.launch(args=args,proxy=self.proxy,headless=True) 
            suffixes=["@gmail.com"]
            self.up=len(suffixes)
            ctx=[self.fetch_search_results(await browser.new_context(user_agent=agent.random,viewport={'width':7000,'height':15000}),suffix) for suffix in suffixes]
            await asyncio.gather(*ctx)    
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

    async def fetch_search_results(self,context,suffix):
       try: 
        page=await context.new_page()
        context.set_default_timeout(3000) 
        await stealth_async(page)
        print('[LOADED]:Context')
        while True:
            if not self.query_tasks.empty():      
              query=self.query_tasks.queue[0]
              counter = 0
              tries=6
              self.q=(f'"{suffix}" {query[3]}  followers  following  {query[2]}  site:www.instagram.com')              
              if(query[7]):await utils.geolocate(page,query[7])
              uid=query[6]
              self.count=0
              self.ctime=0
              url =f'https://www.bing.com/search?count=50&cc={query[7]}&q={self.q}&rdr=1' 

              await page.goto(url)
              await page.evaluate('document.body.style.zoom = "150%"')

              while self.count<self.min and uid in self.files and tries and self.tlim>self.ctime :
                
                    try:  
                        next=page.locator('a[title="Next page"]')
                        flag=True
                        for i in range(0,3): 
                         try:
                            await next.wait_for(state='attached',timeout=12000)
                            await asyncio.sleep(4)
                            items = HTMLParser(await page.content(), 'html.parser').css('.b_algo')
                            self.pg+=len(items)
                            self.parse(items,uid,query[2],query[3])  
                            flag=False
                         except Exception as e:
                            print("[ERROR]:timed out loading next button...")
                            await page.reload()    
                        
                        if flag:next=re.sub(r"first=\d+",f'first={self.pg}',page.url)               

                        
                        print(self.count,self.pg,self.ctime)  
                        
                        next= await next.get_attribute('href')
                        await page.goto(r'https://www.bing.com'+next)
                        counter += 1 
                        self.ctime=time.time()-self.ttime
                        
                    except Exception as e:pass
                        #print('Error:',traceback.format_exc())
               
              self.flg+=1
              await context.clear_cookies()
              while(self.flg<self.up):await asyncio.sleep(2)
              if(uid in self.files and self.flg>=self.up):
                 data=list(self.files.pop(uid)[2].values())[:self.min]
                 self.query_tasks.get()  
                 print(self.ctime,self.count)
                 data_=self.data
                 self.count=0
                 self.flg=0
                 self.data=[]
                 fname=f'./files/{query[5]}_{query[6]}'
                 await asyncio.gather(self.write_results_to_csv(f'{fname}.csv',data),self.write_results_to_csv(f'{fname}.csv',data))
                 await asyncio.gather(self.write_results_to_csv(f'{fname}.csv',data),self.write_results_to_csv(f'{fname}_raw.csv',data_))
               
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
                    if self.count>self.min:return 0
                    if username in ('reel','p','reels','followers','follower','following'):username=None  
                    data=(username,email,following,followers,link,*args)
                    if email and username and followers:                   
                     if  username not in self.files[uid][2]:
                         self.files[uid][2][username]=data
                         count += 1
                         self.count+=1

                    else:self.data.append(data)  
                self.files[uid][0]+=count   
                return count        
           
    def add(self,data): 
            self.pg=data[1]-10
            self.min=data[0]
            self.tlim=data[8]
            print(self.tlim)
            self.files[data[6]]=[0,data[0],{},0,0]
            self.ttime=time.time()
            self.query_tasks.put(data)                  

if(__name__=='__main__'):
   
   ls=LeadScraper( )
   uid=str(uuid.uuid4())
   (ls.add([100,1,'fitness','madrid','instagram.com','test_token',uid,'ES',10]))
   asyncio.run(ls.handler())
    