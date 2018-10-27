from bs4 import BeautifulSoup
import threading
import asyncio
import json
from urllib.request import urlopen
import pandas
import time

_FILENAME = 'downloaded_clean_list.csv'
ERROR = 0

def getInfo(url):
    if url is None:
        return
    html = urlopen(url)
    soup = BeautifulSoup(html, 'html.parser')
    category = soup.find("a", itemprop="genre")
    price = soup.find("meta", itemprop="price")
    return category.string, price['content']


class download_thread (threading.Thread):
   def __init__(self, namespace):
      threading.Thread.__init__(self)
      self.namespace = namespace
      self.url = 'https://play.google.com/store/apps/details?id=' + namespace
   def run(self):
        try:
            print('Get : ', self.url)
            category, price = getInfo(self.url)
            data = {
                'name': [self.namespace],
                'category': [category],
                'price': [price]
            }
            df_saved = pandas.DataFrame(data)
            df_saved.to_csv(_FILENAME, sep='\t', mode='a', encoding='utf-8', index=False)
        except Exception as e:
            print('-- Error --')
            print(e)
            print(self.url)

packages = pandas.read_csv("package_name.csv", sep= ',' , compression=None)
downloaded_list = pandas.read_csv("already_downloaded_list.csv", sep="\t", encoding="utf-8", names=['package', 'category', 'price'])
downloaded_list_ = downloaded_list['package'].to_json(orient='records')
#
downloaded_list_to_json = {}
for download_item in json.loads(downloaded_list_):
    downloaded_list_to_json[download_item] = 1

#
packs = json.loads(packages.to_json(orient='records'))
if len(packs) > 0:
    for package in packs:
        if package['package_name'] not in downloaded_list_to_json:    
            thread2 = download_thread(package['package_name'])
            thread2.start()