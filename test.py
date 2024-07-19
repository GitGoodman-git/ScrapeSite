import requests
import fake_useragent as fu

agent=fu.UserAgent()
    
def send_request_21():
    url = 'http://localhost:8000/add_queries'
    params = {
        'niche': 'fashion',
        'location': 'haldwani',
        'token': 'aabf3e2e-488f-4d63-8eae-df0b6f729f3d',
        'hook': 'https://webhook.site/384b992c-d54e-4cec-99ea-59f0c487aa03',
        'min': 10,
        'start': 1
    }
    
    response = requests.get(url, params=params)
    print(response.url)
    print(response.status_code)
    print(response.text)  # If the response is JSON

def send_request_2():
    url = 'http://localhost:8000/get_file'
    params = {
        'token': 'aabf3e2e-488f-4d63-8eae-df0b6f729f3d',
    }
    
    response = requests.get(url, params=params)
    print(response.url)
    print(response.status_code)
    print(response.text)  

headers={
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    'Accept-Encoding':'gzip, deflate, br, zstd',
    'Cache-Control':'no-cache',
    'Accept-Charset': 'utf-8',
    
    }
    
from bs4 import BeautifulSoup
def send_request_3():
    url='https://www.instagram.com/krishnamisra__/,fashion,dehradun'
    headers['User-Agent']=agent.random
    response = requests.get(url,headers=headers)
    soup= BeautifulSoup(response.content)
    print(response.url)
    print(response.status_code)
    print(soup.text)  
    
# Example usage:
import time
if __name__ == "__main__":
    send_request_3()
   # while True:
    # input()
     #send_request_2()
#http://scrape-site.vercel.app/add_queries?niche=fashion&location=haldwani&token=aabf3e2e-488f-4d63-8eae-df0b6f729f3d&hook=https%3A%2F%2Fwebhook.site%2F384b992c-d54e-4cec-99ea-59f0c487aa03&min=10&start=1  
#http://scrape-site.vercel.app/get_file?token=aabf3e2e-488f-4d63-8eae-df0b6f729f3d
