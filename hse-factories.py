import requests
from bs4 import BeautifulSoup
import re
import csv
from shapely.geometry import shape
import json


def smart_http_request(s: requests.Session, url='', method='get', params=None, headers=None, data = None, json = None, tries=10, verify=False):
    i = 1
    status_code = 0
    result = None
    if url:
        while (not result) and i <= tries and status_code != 200:
            i += 1            
            try:
                if method == 'get':
                    result = s.get(url, params=params, headers=headers, verify=verify)
                if method == 'post':
                    result = s.post(url, data=data, json=json, headers=headers, verify=verify)
                status_code = result.status_code
            except:
                pass
    return (status_code, result)


def download_factories(pages=1200):
    headers = {
        "Referer": "https://xn--80aegj1b5e.xn--p1ai/",
        "Dnt": "1",
        "Cookie": "beget=begetok; _ga=GA1.1.1569883291.1751358490; _ym_uid=175135849071815330; _ym_d=1751358490; _ym_isad=1; _ym_visorc=w; _ga_KVY5H4MWGY=GS2.1.s1751362888$o2$g1$t1751362903$j45$l0$h0"
    }
    factory_attrs = [
        'name', 'urn', 'lineage', 'people', 'text', 'categories', 'descr', 'type', 
        'business_size', 'employees', 'finance', 'legal_entity', 'ogrn', 'inn', 
        'kpp', 'address', 'phone', 'email', 'site', 'geojson', 'xcoord', 'ycoord'
        ]
    with open('result/factories_rf.csv', 'w', newline='', encoding='utf-8') as of:
        writer = csv.DictWriter(of, fieldnames=factory_attrs, delimiter='|')
        writer.writeheader()
        with requests.Session() as s:        
            for page in range(pages):
                params = {
                    "page": str(page)
                }
                url = f"https://xn--80aegj1b5e.xn--p1ai/factories"
                
                status_code, result = smart_http_request(s, url=url, params=params, headers=headers)
                
                if status_code == 200:
                    teasers_soup = BeautifulSoup(result.text, 'html.parser')
                    
                    for factory_teaser in teasers_soup.find_all(attrs={"class": re.compile('factory\steaser\steaser\-\d*')}):
                        factory_dict = {k: None for k in factory_attrs}
                        factory_title_tag = factory_teaser.find(attrs={"class": "factory__head"}).find(attrs={"class": "factory__title"})
                        if factory_title_tag:
                            factory_dict['name'] = factory_title_tag.text.strip()
                            factory_dict['urn'] = factory_title_tag['href']
                        factory_txt_tag = factory_teaser.find(attrs={"class": "factory__txt"})
                        if factory_txt_tag:
                            lineage_tag = factory_txt_tag.find(attrs={"class": "lineage-item lineage-item-level-0"})
                            if lineage_tag:
                                factory_dict['lineage'] = lineage_tag.text
                            people_tag = factory_txt_tag.find(attrs={"class": "factory__people content-list__title"})
                            if people_tag:
                                factory_dict['people'] = people_tag.text
                            factory_dict['text'] = factory_txt_tag.find('p').text
                        factory_categories_tags = factory_teaser.find(attrs={"class": "factory__category"}).find_all('li')
                        if factory_categories_tags:
                            factory_dict['categories'] = ', '.join([x.find('a').text for x in factory_categories_tags if x.find('a')])
                        
                        if factory_dict.get('urn'):
                            url = f"https://xn--80aegj1b5e.xn--p1ai{factory_dict['urn']}"
                            status_code, result = smart_http_request(s, url=url, headers=headers)
                            if status_code == 200:
                                about_soup = BeautifulSoup(result.text, 'html.parser')
                                factory_dict['descr'] = ' '.join([x.text for x in about_soup.find(attrs={"id": "company-descr"}).find_all('p')])
                                for content_list_item_tag in about_soup.find(attrs={"class": "content-list"}).find_all('li'):
                                    if content_list_item_tag.find(attrs={"class": "content-list__title"}).text == 'Тип предприятия':
                                        factory_dict['type'] = content_list_item_tag.find(attrs={"class": "content-list__descr"}).text.strip()
                                    if content_list_item_tag.find(attrs={"class": "content-list__title"}).text == 'Размер бизнеса':
                                        factory_dict['business_size'] = content_list_item_tag.find(attrs={"class": "content-list__descr"}).text.strip()
                                    if content_list_item_tag.find(attrs={"class": "content-list__title"}).text == 'Сотрудники':
                                        factory_dict['employees'] = content_list_item_tag.find(attrs={"class": "content-list__descr"}).text.strip()
                                    if content_list_item_tag.find(attrs={"class": "content-list__title"}).text == 'Фин показатели':
                                        factory_dict['finance'] = content_list_item_tag.find(attrs={"class": "content-list__descr"}).text.strip()
                                pass
                        
                            url = f"https://xn--80aegj1b5e.xn--p1ai{factory_dict['urn']}/details"
                            status_code, result = smart_http_request(s, url=url, headers=headers)
                            if status_code == 200:
                                details_soup = BeautifulSoup(result.text, 'html.parser')
                                for content_list_item_tag in details_soup.find(attrs={"class": "content-list"}).find_all('li'):
                                    if content_list_item_tag.find(attrs={"class": "content-list__title"}).text == 'Название юр лица':
                                        factory_dict['legal_entity'] = content_list_item_tag.find(attrs={"class": "content-list__descr"}).text.strip()
                                    if content_list_item_tag.find(attrs={"class": "content-list__title"}).text == 'ОГРН':
                                        factory_dict['ogrn'] = content_list_item_tag.find(attrs={"class": "content-list__descr"}).text.strip()
                                    if content_list_item_tag.find(attrs={"class": "content-list__title"}).text == 'ИНН':
                                        factory_dict['inn'] = content_list_item_tag.find(attrs={"class": "content-list__descr"}).text.strip()
                                    if content_list_item_tag.find(attrs={"class": "content-list__title"}).text == 'КПП':
                                        factory_dict['kpp'] = content_list_item_tag.find(attrs={"class": "content-list__descr"}).text.strip()
                        
                            url = f"https://xn--80aegj1b5e.xn--p1ai{factory_dict['urn']}/contacts"
                            status_code, result = smart_http_request(s, url=url, headers=headers)
                            if status_code == 200:
                                contacts_soup = BeautifulSoup(result.text, 'html.parser')
                                for content_list_item_tag in contacts_soup.find(attrs={"class": "content-list"}).find_all('li'):
                                    if content_list_item_tag.find(attrs={"class": "content-list__title"}).text == 'Адрес':
                                        factory_dict['address'] = content_list_item_tag.find(attrs={"class": "content-list__descr"}).text.strip()
                                    if content_list_item_tag.find(attrs={"class": "content-list__title"}).text == 'Телефон':
                                        factory_dict['phone'] = content_list_item_tag.find(attrs={"class": "content-list__descr"}).text.strip()
                                    if content_list_item_tag.find(attrs={"class": "content-list__title"}).text == 'Эл. почта':
                                        factory_dict['email'] = content_list_item_tag.find(attrs={"class": "content-list__descr"}).text.strip()
                                    if content_list_item_tag.find(attrs={"class": "content-list__title"}).text == 'Сайт':
                                        factory_dict['site'] = content_list_item_tag.find(attrs={"class": "content-list__descr"}).text.strip()
                                if contacts_soup.find(attrs={"class": "category-map"}):
                                    factory_dict['geojson'] = contacts_soup.find(attrs={"class": "category-map"}).find(attrs={"class": "geofield-ymap"}).get('data-map-objects')
                        
                        if factory_dict.get('geojson'):
                            feature = json.loads(factory_dict.get('geojson'))["features"][0]
                            geo = shape(feature["geometry"])
                            coords = geo.coords[0]
                            factory_dict['xcoord'] = coords[0]
                            factory_dict['ycoord'] = coords[1]
                            pass
                        # factory_dict = {k: v.replace('\r\n', ' ').replace('\n', ' ') for k, v in factory_dict.items()}
                        for k, v in factory_dict.items():
                            if isinstance(v, str):
                                v = v.replace('\r\n', ' ')
                                v = v.replace('\n', ' ')
                                v = v.replace('\r', ' ')
                                factory_dict[k] = v
                            if k == 'urn':
                                factory_dict[k] = f"https://xn--80aegj1b5e.xn--p1ai{v}"
                        writer.writerow(factory_dict)

if __name__ == '__main__':
    download_factories(pages=1200)