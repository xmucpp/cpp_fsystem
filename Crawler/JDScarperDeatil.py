# -*- coding: utf-8 -*-
import json
import requests
import time
import csv
import codecs
import random
import re
import os
from config import PRESENT_DAY, PATH
from settings import crawler_logger as logger
from ProxiesPool.headers import USER_AGENTS, PROXIES

limit = 3
test = [None, None, None]


def get_json(url):
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
            try:
                json_data = json.loads(r.content.decode('gbk')[1:-2])
            except ValueError:
                json_data = json.loads(r.content.decode('gbk'))
    except requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout:
        logger.error('{} {}'.format(url.encode('utf-8'), 'Connect Error'))
    return json_data


# 有货状态 , 运费 , 提示 ,
def get_stock(itemid, times=1):
    try:
        json_data = get_json('https://c0.3.cn/stock?skuId={}{}'.format(
            itemid,
            '&cat=670,12800,12801&area=1_72_4137_0&extraParam='
            '{%22originid%22:%221%22}'))

        stock_state = json_data['stock']['StockState']
        try:
            if json_data['stock']['dcashDesc']:
                shipment = json_data['stock']['dcashDesc'][:json_data['stock']['dcashDesc'].find('<a')]
            else:
                shipment = json_data['stock']['eir'][0]['iconSrc']
        except TypeError:
            logger.warning('TypeError in [4]Shipment. ID:{}'.format(itemid))
            shipment = None
        tip = json_data['stock']['Ext']
        return stock_state, shipment, tip
    except KeyError:
        if times <= limit:
            return get_stock(itemid, times + 1)
        else:
            logger.error('{}:{}'.format(itemid, logger.traceback()))
            return -1, -1, -1


# 自营与否 , 商店ID ,
def get_vender(itemid, times=1):
    try:
        json_data = get_json('https://c0.3.cn/stocks?type=batchstocks&skuIds={}'
                             '&area=1_72_4137_0'.format(itemid))
        if 'self_D' in json_data[str(itemid)].keys():
            return 1, json_data[str(itemid)]['self_D']['id']
        elif 'D' in json_data[str(itemid)].keys():
            return 0, json_data[str(itemid)]['D']['id']
        else:
            return 1, 0
    except KeyError:
        if times <= limit:
            return get_vender(itemid, times + 1)
        else:
            logger.error('{}:{}'.format(itemid, logger.traceback()))
            return -1, -1


# 赠品 , 促销券, 其它促销手段,
def get_cuxiao(itemid, times=1):
    try:
        json_data = get_json('https://cd.jd.com/promotion/v2?skuId={}'
                             '&area=1_72_4137_0&shopId=57617&venderId=61908'
                             '&cat=652%2C654%2C832&_=1480602489906'.format(itemid))
        if not json_data['prom']['tags'] or 'gifts' not in json_data['prom']['tags'][0]:
            premiums = None
        else:
            premiums = ''
            for i in json_data['prom']['tags'][0]['gifts']:
                premiums = ''.join([premiums, i['nm']])
        tickets = ''
        for i in json_data['skuCoupon']:
            tickets = '{}满{}减{},'.format(tickets, i['quota'], i['discount'])
        if not json_data['prom']['pickOneTag']:
            POT = None
        else:
            POT = ''
            for i in json_data['prom']['pickOneTag']:
                '{},{}'.format(POT, i['content'])
        return premiums, tickets, POT
    except KeyError:
        if times <= limit:
            return get_cuxiao(itemid, times + 1)
        else:
            logger.error('{}:{}'.format(itemid, logger.traceback()))
            return -1, -1, -1


# 平均分，评论数，好评率，中评率，差评率，
def get_comment(itemid, times=1):
    try:
        json_data = get_json('https://club.jd.com/comment/productCommentSummaries.'
                             'action?referenceIds={}'.format(itemid))
        json_data = json_data['CommentsCount'][0]
        average_score = json_data['AverageScore']
        comment_count = json_data['CommentCount']
        good_rate = json_data['GoodRate']
        general_rate = json_data['GeneralRate']
        poor_rate = json_data['PoorRate']
        return average_score, comment_count, good_rate, general_rate, poor_rate
    except KeyError:
        if times <= limit:
            return get_comment(itemid, times + 1)
        else:
            logger.error('{}:{}'.format(itemid, logger.traceback()))
            return -1, -1, -1, -1, -1


# 价格
def get_price(itemid, times=1):
    try:
        json_data = get_json('https://p.3.cn/prices/get?skuid=J_{}'
                             .format(itemid))
        price = json_data['p']
        return price
    except KeyError:
        if times <= limit:
            return get_price(itemid, times + 1)
        else:
            logger.error('{}:{}'.format(itemid, logger.traceback()))
            return -1


def work(ID):
    if not ID:
        return -1
    data = dict()
    data['ID'] = ID
    print ID
    try:
        itemid = ID.split('_')[1]
    except Exception:
        logger.error('SPLIT ERROR {}'.format(ID))
        itemid = ''
    try:
        data['price'] = get_price(itemid)
        data['average_score'], data['comment_count'], data['good_rate'], data['general_rate'], data['poor_rate'] \
            = get_comment(itemid)
        data['premiums'], data['tickets'], data['POT'] = get_cuxiao(itemid)
        data['vender'], data['shop_id'] = get_vender(itemid)
        data['stock_state'], data['shipment'], data['tip'] = get_stock(itemid)
        file_name = ''.join([os.path.join(PATH, 'Data'), '/', 'jdDeatil', '_', PRESENT_DAY])
        if os.path.isfile(file_name):
            with codecs.open(file_name, 'ab') as f:
                fieldnames = ['ID', 'price', 'average_score', 'comment_count', 'good_rate', 'general_rate', 'poor_rate',
                              'vender', 'shop_id', 'stock_state', 'shipment', 'tip', 'premiums', 'tickets', 'POT']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                data = {key: value for key, value in data.items() if key in fieldnames}
                writer.writerow(data)
        else:
            with codecs.open(file_name, 'ab') as f:
                fieldnames = ['ID', 'price', 'average_score', 'comment_count', 'good_rate', 'general_rate', 'poor_rate',
                              'vender', 'shop_id', 'stock_state', 'shipment', 'tip', 'premiums', 'tickets', 'POT']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                data = {key: value for key, value in data.items() if key in fieldnames}
                writer.writerow(data)
    except Exception:
        logger.error('{}{}'.format(itemid, logger.traceback()))
        return 0
    else:
        return 1


if __name__ == '__main__':
    for i in test:
        work(i)
