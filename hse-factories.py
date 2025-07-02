import requests
from bs4 import BeautifulSoup
import re


def download_factories(pages=1200):
    headers = {
        "Referer": "https://xn--80aegj1b5e.xn--p1ai/",
        "Dnt": "1",
        "Cookie": "beget=begetok; _ga=GA1.1.1569883291.1751358490; _ym_uid=175135849071815330; _ym_d=1751358490; _ym_isad=1; _ym_visorc=w; _ga_KVY5H4MWGY=GS2.1.s1751362888$o2$g1$t1751362903$j45$l0$h0"
    }
    with requests.Session() as s:
        for page in range(pages):
            params = {
                "page": str(page)
            }
            url = f"https://xn--80aegj1b5e.xn--p1ai/factories"
            i = 1
            status_code = 0
            result = None
            while (not result) and i <= 10 and status_code != 200:
                i += 1            
                try:
                    result = s.get(url, headers=headers, params=params, verify=False)                
                    status_code = result.status_code
                except:
                    pass
            if status_code == 200:
                soup = BeautifulSoup(result.text, 'html.parser')
                for factory_teaser in soup.find_all(attrs={"class": re.compile('factory\steaser\steaser\-\d*')}):
                    pass


if __name__ == '__main__':
    download_factories(pages=1)