from bs4 import BeautifulSoup as soup
import requests
from user_agent import generate_user_agent
import sys
import re
from functools import reduce

def get_headers():
    return {'User-Agent': generate_user_agent(device_type="desktop", os=('mac', 'linux'))}

def get_pages_links(url):
    try:
        page = requests.get(url,timeout=5,headers = get_headers())
    except Exception as e:
        print(str(e))
    finally:
        if page.status_code == 200:
            s = soup(page.content,"html.parser")
            return list(s.find_all("a",class_="chapter-link cp-l"))
def get_hrefs(root,links):
    return list(map(lambda n:root+n.get("href"),links))

def get_page(url):
    try:
        page = requests.get(url,timeout=5,headers=get_headers())
    except Exception as e:
        print(str(e))
    finally:
        if page.status_code == 200:
            s = soup(page.content,"html.parser")
            return s.find_all("div",class_="b-chapter")[0]
        else:
            print("connection to {} returned {}".format(url,page.status_code))

def get_root_url(url):
    pattern = "http[s]?://\w+[.]\w+[/]+"
    m = re.search(pattern,url)
    if m:
        return m.group(0)
    else:
        return ""

def get_page_content(page):
    content = ""
    for el in page:
        if el.name == "div":
            subcontent = get_page_content(el)
            content += subcontent + "\n"
        elif el.name == "p":
            text = str(reduce(lambda a,b:a+b,el.contents))
            content += text + "\n"
    return content
        
if __name__ == "__main__":
    if len(sys.argv) != 3:
        exit(-1)

    _, url, save_path = sys.argv
    page_urls = get_hrefs(get_root_url(url),get_pages_links(url))

    pages = []
    for url in page_urls:
        pages.append(get_page(url))

    contents = []
    for page in pages:
        contents.append(get_page_content(page))

    with open(save_path,"w") as f:
        for p in contents:
            f.write(p)
    

    

