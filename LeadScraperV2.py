import aiohttp as aio
import asyncio
from random import choice,randint
from selectolax.parser import HTMLParser
import re,aiofiles
import time
from json import dumps
from aiocsv import AsyncWriter

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.64 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edge/91.0.864.64",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:88.0) Gecko/20100101 Firefox/88.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:88.0) Gecko/20100101 Firefox/88.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:87.0) Gecko/20100101 Firefox/87.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
]
def UA():
   k=0
   while True:
    yield choice(user_agents[k])
    k=(k+1)%7

headers={
    "Accept": "text/html;q=0.9",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    'Accept-Encoding':'gzip, deflate, br, zstd',
    'Cache-Control':'no-cache'
}

class LeadScraper():
    def __init__(self,proxy=None):
        self.data=[]
        self.data_=[]
        self.files={}
        self.proxy=proxy
        self.min=10
        self.count=0
        self.requests=0
        self.pg=1
        self.query_tasks=[]
        self.agent=UA()
        
    async def handler(self):        
            while True:
            
             if self.query_tasks: 
              query=self.query_tasks.pop()
              self.q= f"site:{query[4]}  '@gmail.com' '{query[2]}' '{query[3]}' 'Followers' '@yahoo.com' '@icloud.com'  '@outlook.com'"         
              ctime=time.time()
              self.pg=query[1]
              self.min=query[0]
              print('[Started]:',ctime)
              await asyncio.gather(*[self.fetch_search_results() for i in range(0,int(self.min/10)+1)])
              print(self.count,self.requests,self.min)
              ctime=time.time()-ctime  
              await self.write_results_to_csv(f'./files/{query[5]}.csv',query[2],query[3],query[4])   
              self.files[query[5]]=1
              #await self.send_json_to_webhook(query[5],query[2],query[3],query[4],ctime,self.pg,query[1],self.min)
              print('done :',ctime)   
             else:await asyncio.sleep(1) 
             self.data=[]
    
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
    
    async def write_results_to_csv(self,filename,*args):
     async with aiofiles.open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = AsyncWriter(file)
        await writer.writerow(['Niche','Location','Site','Link','Title','Followers', 'Following', 'Email']) 
        for item in self.data[:self.min]:
           await writer.writerow((*args,*item))
        self.count=0

    async def fetch_search_results(self):
        async with aio.ClientSession() as session:
            counter = 0
            while self.count < self.min:
                h = headers
                count = 0
                h['User-Agent'] = next(self.agent)
                self.pg += 1
                if counter == 25:
                    session.cookie_jar.clear()
                    counter = 0
                url = f'https://www.bing.com/search?first={int(self.pg * 50)}&count=50&q={self.q}&rdr=1'
                async with session.get(url, headers=h, proxy=self.proxy) as response:
                    html = await response.text()
                    soup = HTMLParser(html, 'html.parser')
                link = ''
                for item in soup.css('.b_algo'):
                    data_text = item.text()
                    email = re.search(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[+A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+', data_text)
                    try:
                        link = item.css_first('h2 a').attributes['href']
                    except:
                        link = ''
                    following = re.search(r'\b\d+[A-Z]*\s+Followers\b', data_text)
                    following = (following.group())[:-9] if following else ""
                    followers = re.search(r'\b\d+[A-Z]*\s+Following\b', data_text)
                    followers = (followers.group())[:-9] if followers else ""
                    if email:
                        count += 1
                        email = following = email.group()
                        self.data.append((link.split('/')[-2], link, email, following, followers))
                    else:
                        self.data_.append((link.split('/')[-2], link, '', following, followers))
                self.requests += 1
                self.count += count
                count = 0
                counter += 1
        
    def add(self,data):
            pos=len(self.query_tasks) 
            self.files[data[5]]=0
            self.query_tasks.append(data)  
            return pos                

if(__name__=='__main__'):
   ls=LeadScraper()
   ls.add([100,1,'fitness','haldwani','instagram.com','test_token'])
   asyncio.run(ls.handler())
    