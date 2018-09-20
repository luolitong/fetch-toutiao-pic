# coding:utf-8
import re
from urllib.parse import urlencode
from requests.exceptions import RequestException
from hashlib import md5
from multiprocessing import Pool
import json
import os
import requests
from bs4 import BeautifulSoup


BASE_URL='http://www.toutiao.com'
def get_page_index(offset,keyword):
    data={
        'offset': offset,
        'format':'json',
        'keyword':keyword,
        'autoload':'true',
        'count':20,
        'cur_tab':1,
        'from':'search_tab'
    }
    headers={'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
    url='https://www.toutiao.com/search_content/?'+urlencode(data)
    try:
        response=requests.get(url,headers=headers)
        if response.status_code==200:
            return response.text
        return None
    except RequestException:
        print('请求索引页出错')
        return None


def parse_page_index(html):
    data=json.loads(html)
    if data and 'data' in data.keys():
        for item in data.get('data'):
            if item.get('open_url'):
                yield item.get('open_url')


def get_page_detail(url):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
    try:
        response=requests.get(url,headers=headers)
        if response.status_code==200:
            return response.text
        return None
    except RequestException:
        print('请求详情页出错',url)
        return None


def parse_page_detail(html,url):
    soup=BeautifulSoup(html,'lxml')
    title=soup.select('title')[0].get_text()
    print(title)
    images_pattern=re.compile('gallery: JSON.parse\\(\\"(.*?)\\"\\)',re.S)
    result=re.search(images_pattern,html)
    if result:
        result_json_obj=json.loads(result.group(1).replace('\\',''))
        #print(result_json_obj)
        pic_url_list=result_json_obj.get('sub_images')
        images=[item.get('url') for item in pic_url_list]
        return {
            'title':title,
            'url':url,
            'images':images
        }
    else:
        print('no string matched')


def download_image(url):
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            save_images(response.content)
        else:
            print('下载图片出错，请求相应码为：'+response.status_code)
    except RequestException:
        print('请求图片出错',url)
        return None


def save_images(content):
    file_path='{0}\\{1}.{2}'.format(os.getcwd()+'\\images\\',md5(content).hexdigest(),'jpg')
    if not os.path.exists(file_path):
        with open(file_path,'wb') as f:
            f.write(content)
            f.close()


def main(offset):
    html=get_page_index(offset,'街拍')
    for url in parse_page_index(html):
        url=BASE_URL+url
        #print(url)
        html=get_page_detail(url)
        result=parse_page_detail(html,url)
        try:
            for each in result.get('images'):
                download_image(each)
        except AttributeError:
            print("------------------出错，非图集页面------------------")
            pass


if __name__=='__main__':
    groups =[x*20 for x in range(0,5)]
    pool=Pool()
    pool.map(main,groups)
