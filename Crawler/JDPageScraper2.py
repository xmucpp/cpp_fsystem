# __author__ = 'xjlin'
# -*- coding: utf-8 -*-

import os
import codecs
import csv
import time
import random
import re
import math
import requests
import json

from bs4 import BeautifulSoup

from config import join_paras
from config import PRESENT_DAY, PATH
from settings import crawler_logger as logger
#from pymongo import MongoClient
from ProxiesPool.headers import USER_AGENTS, PROXIES


PRESENT_TIME = str(time.strftime('%H-%M-%S', time.localtime(time.time())))


# Unit Function


def get_url(category_name, paras, page_num):
    """
    structure the top half of the request url
    Parameters
    ----------
    category_name
    paras
    page_num

    Returns
    -------

    """

    page = str(page_num * 2 - 1)
    s = str((page_num - 1) * 60 + 1)

    url_pre = u'http://search.jd.com/search?enc=utf-8'
    query = ''.join([u'&page=', page, u'&s=', s, u'&keyword=', category_name])
    if paras:
        url = ''.join([url_pre, query, paras])
    else:
        url = ''.join([url_pre, query])
    return url


def get_html(url):
    """
    get html content
    Parameters
    ----------
    url

    Returns
    -------

    """
    user_agent = random.choice(USER_AGENTS)
    proxy = re.sub('\n', '', random.choice(PROXIES))
    headers = {
        'Accept': 'text/html',
        'Accept-Encoding': 'gzip,deflate,sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'search.jd.com',
        'Referer': 'http://www.jd.com/',
        'user-agent': user_agent,
        'http': proxy,
    }

    try:
        r = requests.get(url, headers)
        if r.status_code == 302:
            logger.error('this server be banned by JD')
            time.sleep(30)
            return None
        else:
            return r.content
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
        logger.error('{} {}'.format(url.encode('utf-8'), 'Connect Error'))
        return None


def parse_html(html, **kwargs):

    if not html:
        logger.error('not get html')
        return None
    data_list = []
    try:
        soup = BeautifulSoup(html, 'html.parser')
        soup = soup.find('div', 'g-main2')
        IDs = []
        IDprice = ''
        IDcomment = []
        div_gls = soup.find_all('div', attrs={'class': 'p-name'})
        for i in range(0, div_gls.__len__()):
            div = div_gls[i]
            data = {}
            try:
                data['goodsName'] = div.em.text.encode('utf-8')
            except Exception, e:
                logger.warning('{} {} {}'.format(kwargs['url'], e, 'goods name is None'))
                data['goodsName'] = None

            try:
                data['ID'] = re.search(r'\d+', div.a['href']).group()
                IDs.append(data['ID'])
            except Exception, e:
                logger.warning('{} {} {}'.format(kwargs['url'], e, 'id is None'))
                data['ID'] = None
            data_list.append(data)
        for ID in IDs:
            IDprice = '{}J_{}%2C'.format(IDprice, str(int(ID.replace(':[]', ''))))
            IDcomment.append(int(ID.replace(':[]', '')))
        prices = json.loads(get_html('{}{}'.format('http://p.3.cn/prices/mgets?skuIds=',IDprice)))
        jscomments = get_html('{}{}'.format('http://club.jd.com/comment/productCommentSummaries.action?referenceIds=',str(IDcomment)[1:-1].replace(' ', '')))
        comments = json.loads(jscomments.decode('gbk').encode('utf8'))['CommentsCount']
        for i in range(0, div_gls.__len__()):
            try:
                if prices[i]['id'][2:] == data_list[i]['ID']:
                    data_list[i]['price'] = prices[i]['p']
                else:
                    raise KeyError
            except Exception, e:
                logger.warning('{} {} {}'.format('price is None'))
                data_list[i]['price'] = None

            try:
                if comments[i]['SkuId'] == int(data_list[i]['ID']):
                    data_list[i]['commentsNum'] = comments[i]['CommentCount']
                    data_list[i]['goodRate'] = comments[i]['GoodRate']
                    data_list[i]['generalRate'] = comments[i]['GeneralRate']
                    data_list[i]['poorRate'] = comments[i]['PoorRate']
                    data_list[i]['averageScore'] = comments[i]['AverageScore']
                else:
                    raise KeyError
            except Exception, e:
                logger.warning('{} {} {}'.format(kwargs['url'], e, 'comments num is None'))
                data_list[i]['commentsNum'] = data_list[i]['goodRate'] = data_list[i]['generalRate'] = data_list[i]['poorRate'] = data_list[i]['averangeScore'] = None
    except AttributeError, e:
        logger.error('{} {} {}'.format(kwargs['url'].encode('utf-8'), 'parse error', e))
        return None
    return data_list


def write_csv(data_list, **kwargs):
    """
    Write the data list into a .csv file

     Parameters
     ----------
      data_list: list
         elements with type "dict"

     Returns
     -------
      indicator: bool
          success with "True" and failure with "None"
    """

    if not data_list:
        logger.error('{} {}'.format(kwargs['url'].encode('utf-8'), 'data list is None'))
        return None

    # check or create a daily dictionary
    try:
        file_dict = os.path.join(PATH, 'Data', '{}{}'.format('JDData_', PRESENT_DAY))
    except TypeError:
        file_dict = ''.join(['../JDData_', PRESENT_DAY])
    try:
        os.makedirs(file_dict)
    except OSError, e:
        if e.errno != 17:
            raise e

    # create a file and its name for a certain page
    if kwargs['paras']:
        file_name = ''.join(
            [file_dict, '/', 'jdPrice2', '_', PRESENT_DAY, '_', PRESENT_TIME, '_',
             kwargs['category_name'].encode('utf-8'), '_', kwargs['paras'], '_', str(kwargs['page_num'])])
    else:
        file_name = ''.join(
            [file_dict, '/', 'jdPrice2', '_', PRESENT_DAY, '_', PRESENT_TIME, '_',
             kwargs['category_name'].encode('utf-8'), '_', str(kwargs['page_num'])])

    with codecs.open(file_name, 'wb') as f:
        fieldnames = ['goodsName', 'ID', 'price', 'commentsNum', 'averageScore', 'goodRate', 'generalRate', 'poorRate']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for data in data_list:
            data = {key: value for key, value in data.items() if key in fieldnames}
            writer.writerow(data)

    return 1


def split_url(url):
    regx_page = re.compile('page=\d+')

    #page_num = regx_page.search(url).group().split('=')[1]
    #page_num = (int(page_num)+1) / 2

    #regx_cate = re.compile('keyword=.*&?')
    #category_name = regx_cate.search(url).group().split('=')[1]
    paras = re.search(r'cat=\d.*', url).group()
    #regx_sort = re.compile('psort')
    #sort = regx_sort.search(url)
    #if sort:
        # 通常
        #psort = 1
    #else:
        # 新排序
        #psort = 0
    # for item in array[5:]:
    #     paras = ''.join([paras, '&', item])

    return paras


# Integration Function

def structure(category_name, page_num=2, **url_parameter):
    paras = join_paras(**url_parameter)
    #url_top = get_url_top(category_name, paras, 1)
    #html = get_html(url_top)
    #page_num = get_total_page(url_top, html)
    for i in xrange(1, page_num + 1):
        yield get_url(category_name, paras, i)


def parse(url):
    '''paras= split_url(url)
    dicty = {
        'url': url.decode('utf-8'),
        'page_num': page_num,
        'category_name': category_name.decode('utf-8'),
        'paras': paras
    }'''

    html = get_html(url)
    data_list = parse_html(html)
    return write_csv(data_list)


if __name__ == '__main__':
    categoryName = u'酱油'
    urlParameter = {}
    #for n in structure(categoryName, **urlParameter):
        #print n
        #print parse(n)
    url = 'http://list.jd.com/list.html?cat=737,794,878&page=1'
    parse(url)

