# __author__ = 'xjlin'
# -*- coding: utf-8 -*-
import os
import codecs
import csv
import time
import random 
import re
import json

import requests
from bs4 import BeautifulSoup
#from pymongo import MongoClient

from config import join_paras
from config import PRESENT_DAY, PATH
from settings import crawler_logger as logger
from ProxiesPool.headers import USER_AGENTS, PROXIES


PRESENT_TIME = str(time.strftime('%H-%M-%S', time.localtime(time.time())))


def deal_sales(sales):
    sales = sales.encode('utf-8')
    pattern_ten_th = re.compile('万')
    pattern_num = re.compile('^\d+\.?\d*')
    match = re.search(pattern_ten_th, sales)
    if match:
        match_num = re.search(pattern_num, sales)
        num = int(float(match_num.group(0)) * 10000)
        return num
    else:
        match_num = re.search(pattern_num, sales)
        num = int(match_num.group(0))
        return num


def join_paras(**url_paras):

    if not url_paras:
        return None

    paras = ''
    url_paras = url_paras.items()
    for para in url_paras:
        new_para = ''.join([para[0], '=', str(para[1])])
        paras = '&'.join([paras, new_para])
    return paras


def join_url(category_name, paras, s):

    url = u'http://list.tmall.com/search_product.htm?'
    query = ''.join([u'&s=', str(s), u'&q=', category_name, u'&sort=d'])
    if paras:
        page_url = ''.join([url, query, paras])
    else:
        page_url = ''.join([url, query])
    return page_url


def get_json(url):
    user_agent = random.choice(USER_AGENTS)
    proxy = re.sub('\n', '', random.choice(PROXIES))
    headers = {
        ':host': 'list.tmall.com',
        ':method': 'GET',
        ':path': url,
        ':scheme': 'https',
        ':version': 'HTTP/1.1',
        'accept': 'text/html',
        'accept-encoding': 'gzip,deflate',
        'accept-language': 'zh-CN,zh;q=0.8',
        'cache-control': 'max-age=0',
        'referer': 'https://list.tmall.com',
        'user-agent': user_agent,
        'http': proxy,
    }

    # request for the HTML
    try:
        r = requests.get(url, headers)
        if r.status_code == 302:
            logger.error('this server be banned by Tmall')
            time.sleep(30)
            return None
        else:
            return r.content
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
        logger.error('{} {}'.format(url.encode('utf-8'), 'Connect Error'))
        return None


def split_url(url):
    array = url.split('&')
    regx_page = re.compile('\d+')

    page_num = regx_page.search(array[1]).group()
    page_num = (int(page_num) / 60) + 1

    category_name = array[2].split('=')[1]

    paras = ''
    for item in array[4:]:
        paras = ''.join([paras, '&', item])

    return page_num, category_name, paras


def get_url(category_name, **url_paras):
    paras = join_paras(**url_paras)

    url = join_url(category_name, paras, 0)
    array = url.split('&s=0')
    url_pre = array[0]
    url_suf = array[1]
    urls = []
    html = get_html(url)

    if not html:
        return None, None, None

    try:
        soup = BeautifulSoup(html, 'html.parser')
        div_page = soup.body.find('div', attrs={'class', 'page'})
        div_content = div_page.find('div', attrs={'id': 'content'})
        div_filter = div_content.find('div', attrs={'class': 'filter clearfix'})
        p_ui = div_filter.find('p', attrs={'class': 'ui-page-s'})
        total_page = p_ui.find('b', attrs={'class': 'ui-page-s-len'}).getText().split('/')[1]
        total_page = int(total_page)
        for i in range(total_page):
            url = join_url(category_name, paras, i * 60)
            urls.append(url)
        return url_pre, url_suf, total_page
    except (AttributeError, TypeError), e:
        return None, None, None


def parse_html(html, **kwargs):
    if not html:
        return None

    try:
        soup = BeautifulSoup(html, 'html.parser')
        products = soup.find_all('div', attrs={'class': 'product-iWrap'})

    except AttributeError, e:
        print(e)
        return None

    if not products:
        logger.warning('{} {} {}'.format(kwargs['url'].encode('utf-8'), 'parse warning', '"products" is None'))
        return None

    data_list = []
    for goods_order, product in enumerate(products):
        data = {}
        try:
            goods_id = product.find('p', attrs={'class': 'productStatus'}).find_all('span')[-1]['data-item'].encode(
                'utf-8')
        except (AttributeError, IndexError):
            goods_id = None
        data['goodsID'] = goods_id

        try:
            goods_url = product.find('div', attrs={'class': 'productImg-wrap'}).find('a')['href']
            goods_url = ''.join(['http:', goods_url]).encode('utf-8')
        except (AttributeError, IndexError):
            goods_url = None
        data['goodsURL'] = goods_url

        if not data['goodsID'] and data['goodsURL']:
            pattern = re.compile('id=\d+')
            match = re.search(pattern, data['goodsURL'])
            if match:
                data['goodsID'] = match.group().split('=')[1]
            else:
                data['goodsID'] = None

        try:
            goods_name = product.find('p', attrs={'class': 'productTitle'}).find('a')['title'].encode('utf-8')
        except (AttributeError, IndexError):
            try:
                a = product.find('div', attrs={'class': 'productTitle productTitle-spu'}).find_all('a')
                text = ''.join([i.getText() for i in a])
                text = re.sub(' ', '', text)
                text = re.sub('\n', '', text)
                text = re.sub('\r', '', text)
                goods_name = text.encode('utf-8')
            except (AttributeError, IndexError):
                goods_name = None
        except Exception:
            goods_name = None
        data['goodsName'] = goods_name

        try:
            shop_url = product.find('div', attrs={'class': 'productShop'}).find('a')['href']
            shop_url = ''.join(['http:', shop_url]).encode('utf-8')
        except (AttributeError, IndexError):
            shop_url = None
        data['shopURL'] = shop_url

        try:
            text = product.find('div', attrs={'class': 'productShop'}).find('a').getText()
            text = re.sub('\n', '', text)
            text = re.sub('\r', '', text)
            shop_name = text.encode('utf-8')
        except (AttributeError, IndexError):
            shop_name = None
        data['shopName'] = shop_name

        try:
            price = product.find('p', attrs={'class': 'productPrice'}).em['title'].encode('utf-8')
        except (AttributeError, IndexError):
            price = None
        data['price'] = price

        try:
            price_ave = product.find('span', attrs={'class': 'productPrice-ave'}).getText().encode('utf-8')
        except (AttributeError, IndexError):
            price_ave = None
        data['price_ave'] = price_ave

        try:
            monthly_sales = product.find('p', attrs={'class': 'productStatus'}).em.getText()
            monthly_sales = str(deal_sales(monthly_sales)).encode('utf-8')
        except (AttributeError, IndexError):
            monthly_sales = None
            continue
        data['monthly_sales'] = monthly_sales

        try:
            comments = product.find('p', attrs={'class': 'productStatus'}).a.getText()
            comments = str(deal_sales(comments)).encode('utf-8')
        except (AttributeError, IndexError):
            comments = None
        data['comments'] = comments

        if filter((lambda x: x), data.values()):
            data['category_name'] = str(kwargs['category_name']).encode('utf-8')
            data['paras'] = kwargs['paras']
            data['page_num'] = kwargs['page_num']
            data['order'] = goods_order + 1
            data['present_day'] = PRESENT_DAY
            data['present_time'] = PRESENT_TIME
            data_list.append(data)

    return data_list


def get_item(json_data):
    js = json.loads(json_data)['item']
    data_list = []
    for i in js:
        item = {}
        try:
            item['goodsID'] = i['item_id']
        except KeyError:
            item['goodsID'] = None

        try:
            item['goodsName'] = i['title']
        except KeyError:
            item['goodsName'] = None

        try:
            item['shopID'] = i['shop_id']
        except KeyError:
            item['shopID'] = None

        try:
            item['shopName'] = i['shop_name']
        except KeyError:
            item['shopName'] = None

        try:
            item['sales'] = i['sold']
        except KeyError:
            item['sales'] = None

        try:
            item['price'] = i['price']
        except KeyError:
            item['price'] = None

        try:
            item['comments'] = i['comment_num']
        except KeyError:
            item['comments'] = None
        data_list.append(item)
    return data_list


def write_csv(data_list, page, category_name):
    if data_list is None:
        return None

    # check or create a daily dictionary
    try:
        file_dict = os.path.join(PATH, 'Data', '{}{}'.format('TmallData_', PRESENT_DAY))
    except TypeError:
        file_dict = ''.join(['../TmallData_', PRESENT_DAY])
    try:
        os.makedirs(file_dict)
    except OSError, e:
        if e.errno != 17:
            raise e

    # create a file and its name for a certain page

    file_name = ''.join(
        [file_dict, '/', 'tmallPrice', '_', PRESENT_DAY, '_', PRESENT_TIME, '_', category_name,
         '_', str(page)])

    with codecs.open(file_name, 'wb') as f:
        fieldnames = ['goodsID', 'goodsName', 'shopName', 'shopID', 'sales', 'price',
                      'comments', ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for data in data_list:
            data = {key: value for key, value in data.items() if key in fieldnames}
            writer.writerow(data)

    # return indicator
    return [itemid['goodsID'] for itemid in data_list]


def structure(category_name, page_num=2):
    yield category_name


def parse(fake_url):
    url = fake_url.split('&*')[0]
    page = url.split('no=')[1]
    category_name = fake_url.split('*')[-1]
    json_data = get_json(url)
    data_list = get_item(json_data)
    return write_csv(data_list, page, category_name)
    

if __name__ == '__main__':
    for i in structure('tmall'):
        print i
    # parse('https://list.tmall.com/m/search_items.htm?q=%CD%E0%D7%D3&page_no=1&*name*袜子')
