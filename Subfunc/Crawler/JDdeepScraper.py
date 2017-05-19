# __author__ = 'xjlin'
# -*- coding: utf-8 -*-

# !/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import time
import random
import json
import csv
import re
import os
import threading
from Work.log import Logger
#import gevent
#from gevent import monkey;monkey.patch_all()
logger = Logger('JD', 'DEBUG')


class Jd_scraper(object):
    def __init__(self,keyword,sort):
        PATH = os.path.join(os.getcwd())
        PRESENT_TIME = str(time.strftime('%H-%M-%S', time.localtime(time.time())))
        PRESENT_DAY = str(time.strftime('%Y-%m-%d', time.localtime(time.time())))
        #1为销量排序，0为综合排序
        self.sort_dict ={0:'',1:'1'}
        self.sort = sort

        self.keyword = keyword
        self.search_list_url = 'https://so.m.jd.com/ware/searchList.action'

        self.page_num =self.get_page_num()

        #文件名为url里的参数和爬取时间
        self.date = PRESENT_DAY
        self.time = PRESENT_TIME
        file_dict = os.path.join(PATH, 'Data', 'JDDeep', '{}{}'.format('JDData_', PRESENT_DAY))
        try:
            os.makedirs(file_dict)
        except OSError, e:
            if e.errno != 17:
                raise e
        self.save_name = ''.join([
            file_dict, '/', 'jd_', self.date, '_', self.time, '_', self.keyword, '_', str(self.sort)])

    def get_comment_info(self,id):
        url ='http://club.jd.com/comment/productCommentSummaries.action?'
        headers = {'User-Agent':'Mozilla/5.0 (Linux; U; Android 2.3; en-us) AppleWebKit/999+ (KHTML, like Gecko) Safari/999.9',
                   'Host':'club.jd.com',
                   'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }
        payload = {'referenceIds':id}
        try:
            r = requests.get(url,headers =headers,params = payload)
            json_info = json.loads(r.text)['CommentsCount'][0]
            return json_info
        except:
            return None

    def get_html(self,page_num=1):
        #sort1表示按销量顺序
        data={'_format_':'json',
              'keyword': self.keyword,
              'sort': self.sort_dict[self.sort],
              'page':str(page_num)}
        headers = {'authority':'so.m.jd.com',
        'method':'POST',
        'path':'/ware/searchList.action',
        'scheme':'https',
        'accept':'application/json',
        'referer':'https://so.m.jd.com/ware/search.action?keyword={}'.format(self.keyword),
        'user-agent':'Mozilla/5.0 (Linux; U; Android 2.3; en-us) AppleWebKit/999+ (KHTML, like Gecko) Safari/999.9',
        'x-requested-with':'XMLHttpRequest'}
        #time.sleep(random.randint(1,3))
        r = requests.post(self.search_list_url,headers=headers,data=data)
        if r.status_code == 200:
            return r.text
        else:
            return None

    #获取总面数
    def get_page_num(self):
        html = self.get_html()
        try:
            pagenum = int(json.loads((json.loads(html)['value']))['wareList']['wareCount'])//10
            return pagenum

        except KeyError:
            return None

    def parse(self,pagenum):
        try:
            r = self.get_html(page_num=pagenum)
            ware_list = json.loads(json.loads(r)['value'])['wareList']['wareList']
            wholeinfo =[]
            for index,i in enumerate(ware_list):
                info=[]
                #表示在第几页第几个 如1-2表示第一页第二个

                info.append(i['wname'].encode('utf8'))
                info.append(i['wareId'].encode('utf8'))
                info.append(i['jdPrice'].encode('utf8'))
                info.append(i['totalCount'].encode('utf8'))
                comment_info = self.get_comment_info(i['wareId'].encode('utf8'))
                info.append(comment_info['AverageScore'])
                info.append(comment_info['GoodRate'])
                info.append(comment_info['GeneralRate'])
                info.append(comment_info['PoorRate'])
                info.append(self.date)
                info.append(self.time)
                info.append(str(pagenum) + '-' + str(index + 1))
                info.append(self.keyword)
                info.append(self.sort)
                #print(info)

                wholeinfo.append(info)
            self.save_csv(wholeinfo)
        except Exception:
            print self.keyword
            logger.error(logger.traceback())

    def create_csv(self):
        titles=['goodsName','ID','price','commentsNum','averageScore','goodrate','generalRate','poorRate','date','time','page','keyword','sort']
        with open(self.save_name, 'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(titles)

    def save_csv(self,infolist):
        with open(self.save_name, 'ab') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(infolist)

    def run(self):
        self.create_csv()
        jobs=[]
        for i in range(self.page_num):
            jobs.append(threading.Thread(target=self.parse, args=(i+1,)))
            jobs[i].start()
            #jobs.append(gevent.spawn(self.parse,i+1))
        for i in range(self.page_num):
            jobs[i].join()
        #gevent.joinall(jobs)


def main(keyword):
    #综合排序
    try:
        c =Jd_scraper(keyword,0)
        c.run()

    #销量排序
        m =Jd_scraper(keyword,1)
        m.run()
        return 0
    except Exception:
        logger.error(logger.traceback())
        return 1

if __name__ == "__main__":
    keyword = '酱油'
    main(keyword)


crawler = {
    'JDDeep': main
}