# -*- coding: utf-8 -*-
"""
排行榜爬取脚本
参数为某一榜单代称
因番剧bangumi、国产动画guochan、纪录片documentary、电影movie及电视剧tv排行榜页面参数相异等部分问题，故对其进行舍弃爬取处理。
可爬取排行榜页面名单如下所示(榜单,参数)：
（全站,all）、(国创相关,guochuang)、(动画,douga)、(音乐,music)、(舞蹈,dance)、(游戏,game)、
(知识,knowledge)、(科技,tech)、(运动,sports)、(汽车,car)、(生活,life)、(美食,food)、(动物,animal)、
(鬼畜,kichiku)、(时尚,fashion)、(娱乐,ent)、(影视,cinephile)、(原创,origin)、(新人,rookie)
"""
__author__ = 'OtakuNio'

import pandas as pd
from lxml import etree
from sqlalchemy import create_engine

from get_response_with_proxy_ip import get_response


def rank_main(rank_name):
    print("rank")
    my_url = 'https://www.bilibili.com/v/popular/rank/{}'.format(rank_name)
    response = get_response(my_url)
    if response is None:
        return
    save_to_database_rank(pd.DataFrame(data=get_data_rank(response)), 'rank')
    print("rank-finish")


def get_data_rank(response):
    rank_num_list = []
    bid_list = []
    title_list = []
    uploader_list = []
    view_list = []
    comment_list = []
    points_list = []
    tree = etree.HTML(response.text)
    raw_ranking_list = tree.xpath("//ul[@class='rank-list']/li")
    for li in raw_ranking_list:
        rank_num_list.append(int(li.xpath("./div[1]/text()")[0].strip()))
        title_list.append(li.xpath("./div[2]/div[2]/a/text()")[0].strip())
        li.xpath("./div[2]/div[2]/div[1]/span[1]/text()")[0].strip().replace(' ', '')
        view_list.append(li.xpath("./div[2]/div[2]/div[1]/span[1]/text()")[0].strip().replace(' ', ''))
        comment_list.append(li.xpath("./div[2]/div[2]/div[1]/span[2]/text()")[0].strip().replace(' ', ''))
        uploader_list.append(li.xpath("./div[2]/div[2]/div[1]/a/span/text()")[0].strip().replace(' ', ''))
        points_list.append(int(li.xpath("./div[2]/div[2]/div[2]/div[1]/text()")[0].strip()))
        bid_list.append(li.xpath("./div[2]/div[2]/a/@href")[0].strip('https://www.bilibili.com/video/'))
    rank_data = {
        'rank': rank_num_list,
        'BV_bid': bid_list,
        'title': title_list,
        'uploader': uploader_list,
        'view': view_list,
        'comment': comment_list,
        'points': points_list
    }
    return rank_data


def save_to_database_rank(df, table_name):
    # conn = create_engine("mysql+pymysql://{}:{}@{}:{}/{}?charset={}".format('用户名', '密码', '数据库IP地址', '端口号', '数据库名',
    # '字符编码'))
    conn = create_engine(
        "mysql+pymysql://{}:{}@{}:{}/{}?charset={}".format('root', '123456', 'localhost', '3306', 'test', 'utf8mb4'))
    df.to_sql(table_name, conn, if_exists='replace', index=False)
