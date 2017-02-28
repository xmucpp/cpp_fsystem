# __author__ = 'xjlin'
# -*- coding: utf-8 -*-

import os
import codecs
import csv
import time
import random
import re
import requests
import json

from bs4 import BeautifulSoup

import config as cf
from Work.globalvar import USER_AGENTS
from Work.log import Logger
logger = Logger('JD', 'DEBUG')

PRESENT_DAY = cf.PRESENT_DAY
PATH = cf.PATH

# Unit Function


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
    headers = {
        'Accept': 'text/html',
        'Accept-Encoding': 'gzip,deflate,sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'search.jd.com',
        'Referer': 'http://www.jd.com/',
        'user-agent': user_agent,
    }

    try:
        r = requests.get(url, headers)
        if r.status_code == 302:
            logger.error('this server be banned by JD')
            time.sleep(30)
            raise
        else:
            return r.content
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout, requests.exceptions.MissingSchema) as e:
        logger.error('{} {}'.format(url.encode('utf-8'), 'Connect Error'))
        raise e


def parse_html(html, url, page_num, cate, sort):
    PRESENT_TIME = str(time.strftime('%H-%M-%S', time.localtime(time.time())))
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
        div_gls = []
        for i in soup.find_all('div', 'tab-content-item tab-cnt-i-selected j-sku-item'):
            div_gls.append(i.find('div', 'p-name'))
        for i in soup.find_all('div', 'gl-i-wrap j-sku-item'):
            div_gls.append(i.find('div', 'p-name'))
        for i in range(0, div_gls.__len__()):
            div = div_gls[i]
            data = {}
            try:
                data['goodsName'] = div.em.text.encode('utf-8')
            except Exception, e:
                logger.warning('{} {} {}'.format(url, e, 'goods name is None'))
                data['goodsName'] = None

            try:
                data['ID'] = re.search(r'\d+', div.a['href']).group()
                IDs.append(data['ID'])
            except Exception, e:
                logger.warning('{} {} {}'.format(url, e, 'id is None'))
                data['ID'] = None
            data_list.append(data)
        for ID in IDs:
            IDprice = '{}J_{}%2C'.format(IDprice, str(int(ID.replace(':[]', ''))))
            IDcomment.append(int(ID.replace(':[]', '')))
        try:
            prices = json.loads(get_html('{}{}'.format('http://p.3.cn/prices/mgets?skuIds=', IDprice)))
            jscomments = get_html('{}{}'.format('http://club.jd.com/comment/productCommentSummaries.'
                                                'action?referenceIds=',
                                                str(IDcomment)[1:-1].replace(' ', '').replace('L', '')))
            comments = json.loads(jscomments.decode('gbk').encode('utf8'))['CommentsCount']
        except Exception, e:
            logger.error('{} {}'.format(url, 'js error'))
        for i in range(0, div_gls.__len__()):
            try:
                if prices[i]['id'][2:] == data_list[i]['ID']:
                    data_list[i]['price'] = prices[i]['p']
                else:
                    raise KeyError
            except Exception, e:
                logger.warning('{} {} {}'.format(url, 'price is None', e))
                data_list[i]['price'] = None

            try:
                if comments[i]['SkuId'] == int(data_list[i]['ID']):
                    data_list[i]['commentsNum'] = comments[i]['CommentCount']
                    data_list[i]['goodRate'] = comments[i]['GoodRate']
                    data_list[i]['generalRate'] = comments[i]['GeneralRate']
                    data_list[i]['poorRate'] = comments[i]['PoorRate']
                    data_list[i]['averageScore'] = comments[i]['AverageScore']
                    data_list[i]['date'] = PRESENT_DAY
                    data_list[i]['time'] = PRESENT_TIME
                    data_list[i]['page'] = page_num
                    data_list[i]['cate'] = cate
                    data_list[i]['sort'] = sort
                else:
                    raise KeyError
            except Exception, e:
                logger.warning('{} {} {}'.format(url, e, 'comments num is None'))
                data_list[i]['commentsNum'] = data_list[i]['goodRate'] = data_list[i]['generalRate'] = data_list[i]['poorRate'] = data_list[i]['averangeScore'] = None
    except AttributeError, e:
        logger.error('{} {} {}'.format(url, 'parse error', e))
        return None
    return data_list


def write_csv(data_list, url, paras):
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

    PRESENT_TIME = str(time.strftime('%H-%M-%S', time.localtime(time.time())))
    if not data_list:
        logger.error('{} {}'.format(url, 'data list is None'))
        return None

    # check or create a daily dictionary
    try:
        file_dict = os.path.join(PATH, 'Data', 'JDData', '{}{}'.format('JDData_', PRESENT_DAY))
    except TypeError:
        file_dict = ''.join(['../JDData_', PRESENT_DAY])
    try:
        os.makedirs(file_dict)
    except OSError, e:
        if e.errno != 17:
            raise e

    try:
        page_num = data_list[0]['page']
        sort = data_list[0]['sort']
    except Exception:
        raise

    # create a file and its name for a certain page
    file_name = ''.join(
        [file_dict, '/', 'jdPrice2', '_', PRESENT_DAY, '_', PRESENT_TIME, '_',
         paras, '_', str(sort), '_', str(page_num)])

    with codecs.open(file_name, 'wb') as f:
        fieldnames = ['goodsName', 'ID', 'price', 'commentsNum', 'averageScore', 'goodRate', 'generalRate', 'poorRate',
                      'date', 'time', 'page', 'cate', 'sort']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for data in data_list:
            data = {key: value for key, value in data.items() if key in fieldnames}
            writer.writerow(data)

    return [itemid['ID'] for itemid in data_list]


def split_url(url):

    regx_page = re.compile('page=\d+')

    page_num = regx_page.search(url).group().split('=')[1]
    page_num = int(page_num)

    regx_cat = re.compile('cat=\d+,\d+,\d+')
    cat = regx_cat.search(url).group().split('=')[1]

    regx_catnum = re.compile('\d+')
    catall = re.findall(regx_catnum, cat)
    cat1 = catall[0]
    cat2 = catall[1]
    cat3 = catall[2]

    regx_sort = re.compile('&sort')
    sort = regx_sort.search(url)
    # 1为销量排序, 0为综合排序, 为文件名的倒数第二个参数, 在csv文件中为sort的值
    if sort:
        sort = 1
    else:
        sort = 0

    return page_num, cat1, cat2, cat3, sort


# Integration Function

def structure(category_name, page_num=2):
    for i in xrange(1, page_num + 1):
        yield 'http://{}&page={}'.format(category_name, i)
        yield 'http://{}&page={}&sort=sort_totalsales15_desc'.format(category_name, i)


def parse(url):
    global PRESENT_DAY, PATH
    PRESENT_DAY = cf.PRESENT_DAY
    PATH = cf.PATH
    try:
        page_num, cat1, cat2, cat3, sort = split_url(url)
        paras = '{},{},{}'.format(cat1, cat2, cat3)
        html = get_html(url)
        data_list = parse_html(html, url, page_num, cat3, sort)
        write_csv(data_list, url, paras)
        return 0
    except Exception:
        logger.error(logger.traceback())
        return 1


if __name__ == '__main__':
    url = 'http://list.jd.com/list.html?cat=9987,653,655&page=2&sort=sort_totalsales15_desc'
    parse(url)

