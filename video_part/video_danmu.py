# -*- coding: utf-8 -*-
"""
视频弹幕爬取脚本
参数为某视频的BV号
"""
__author__ = 'OtakuNio'

import pandas as pd
from lxml import etree
from sqlalchemy import create_engine
from get_response_with_proxy_ip import get_response


def video_danmu_main(bid):
    print("video_danmu")
    my_url1 = 'https://comment.bilibili.com/{}.xml'
    my_url2 = 'https://api.bilibili.com/x/web-interface/view?bvid={}'.format(bid)
    save_to_database_video_danmu(pd.DataFrame(
        data=get_data_video_danmu(get_response(my_url1.format(get_cid_video_danmu(get_response(my_url2)))))),
                                 'video_danmu')
    print("video_danmu-finish")


def get_cid_video_danmu(response):
    return response.json()['data']['cid']


def get_data_video_danmu(response):
    tree = etree.HTML(response.content)
    raw_danmu_list = tree.xpath("//d/text()")
    danmu_data = {
        'danmu': raw_danmu_list
    }
    return danmu_data


def save_to_database_video_danmu(df, table_name):
    # conn = create_engine("mysql+pymysql://{}:{}@{}:{}/{}?charset={}".format('用户名', '密码', '数据库IP地址', '端口号', '数据库名',
    # '字符编码'))
    conn = create_engine(
        "mysql+pymysql://{}:{}@{}:{}/{}?charset={}".format('root', '123456', 'localhost', '3306', 'test', 'utf8mb4'))
    df.to_sql(table_name, conn, if_exists='replace', index=False)
