# -*- coding: utf-8 -*-
"""
视频信息爬取脚本
参数为某视频的BV号
因标签无法与视频信息同时获得，故需另外爬取。
且MySQL数据库无法存储列表，故将标签列表放置与video_tag表中。
video_info表与video_tag通过BV_bid进行连接
get_tag_video_info为通过api获得视频标签
get_tag_video_info_1_list、get_tag_video_info_1_data为通过网页原码获得视频标签
"""
__author__ = 'OtakuNio'

import time
import pandas as pd
from lxml import etree
from sqlalchemy import create_engine
from get_response_with_proxy_ip import get_response


def video_info_main(bid):
    print("video_info")
    my_url1 = 'https://api.bilibili.com/x/web-interface/view?bvid={}'.format(bid)
    # my_url2 = 'https://api.bilibili.com/x/tag/archive/tags?bvid={}'.format(bid)
    my_url3 = 'https://www.bilibili.com/video/{}'.format(bid)
    save_to_database_video_info(pd.DataFrame(data=get_data_video_info(get_response(my_url1).json()['data']), index=[1]),
                                'video_info')
    save_to_database_video_info(
        pd.DataFrame(data=get_tag_data_video_info(get_tag_list_video_info(get_response(my_url3)), bid), index=[1]),
        'video_tag')
    print("video_info-finish")


def get_data_video_info(response_json):
    video_info_data = {
        'BV_bid': response_json['bvid'],
        'aid': response_json['aid'],
        'title': response_json['title'],
        'uploader': response_json['owner']['name'],
        'UP_mid': response_json['owner']['mid'],
        'description': response_json['desc'],
        'pubdate': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(response_json['pubdate'])),
        'duration_time': response_json['duration'],
        'view': response_json['stat']['view'],
        'danmu': response_json['stat']['danmaku'],
        'reply': response_json['stat']['reply'],
        'favorite': response_json['stat']['favorite'],
        'coin': response_json['stat']['coin'],
        'share': response_json['stat']['share'],
        'like': response_json['stat']['like'],
        'now_rank': response_json['stat']['now_rank'],
        'history_rank': response_json['stat']['his_rank']
    }
    return video_info_data


def get_tag_video_info(response_json, BV_bid):
    tag_list = []
    for tag in response_json:
        tag_list.append(tag['tag_name'])
    while len(tag_list) < 10:
        tag_list.append('')
    tag_data = {
        'BV_bid': BV_bid,
        'tag0': tag_list[0],
        'tag1': tag_list[1],
        'tag2': tag_list[2],
        'tag3': tag_list[3],
        'tag4': tag_list[4],
        'tag5': tag_list[5],
        'tag6': tag_list[6],
        'tag7': tag_list[7],
        'tag8': tag_list[8],
        'tag9': tag_list[9],
    }
    return tag_data


def get_tag_list_video_info(response):
    tag_list = []
    tree = etree.HTML(response.text)
    raw_tag_list = tree.xpath("//ul[@class='tag-area clearfix']/li")
    count = 0
    for li in raw_tag_list:
        if len(li.xpath("./div/a/span/text()")) != 0:
            tag_list.append((li.xpath("./div/a/span/text()")[0].strip().replace(' ', '')))
        elif len(li.xpath("./a/span/text()")) != 0:
            tag_list.append((li.xpath("./a/span/text()")[0].strip().replace(' ', '')))
        elif len(li.xpath("./div/a/text()")) != 0:
            tag_list.append((li.xpath("./div/a/text()")[0].strip().replace(' ', '')))
        count = count + 1
        if count == 10:
            break
    while count < 10:
        tag_list.append('')
        count += 1
    return tag_list


def get_tag_data_video_info(tag_list, BV_bid):
    tag_data = {
        'BV_bid': BV_bid,
        'tag0': tag_list[0],
        'tag1': tag_list[1],
        'tag2': tag_list[2],
        'tag3': tag_list[3],
        'tag4': tag_list[4],
        'tag5': tag_list[5],
        'tag6': tag_list[6],
        'tag7': tag_list[7],
        'tag8': tag_list[8],
        'tag9': tag_list[9],
    }
    return tag_data


def save_to_database_video_info(df, table_name):
    # conn = create_engine("mysql+pymysql://{}:{}@{}:{}/{}?charset={}".format('用户名', '密码', '数据库IP地址', '端口号', '数据库名',
    # '字符编码'))
    is_table_exist = True
    is_data_exist = True
    conn = create_engine(
        "mysql+pymysql://{}:{}@{}:{}/{}?charset={}".format('root', '123456', 'localhost', '3306', 'test', 'utf8mb4'))
    try:
        sql = "select * from {} where Bv_bid='{}';".format(table_name, df.loc[1, 'BV_bid'])
        if pd.read_sql_query(sql, conn).empty:
            is_data_exist = False
    except Exception:
        is_table_exist = False
    if (is_table_exist == False) or (is_data_exist == False):
        df.to_sql(table_name, conn, if_exists='append', index=False)
    else:
        try:
            sql = "delete from {} where Bv_bid='{}'".format(table_name, df.loc[1, 'BV_bid'])
            pd.read_sql_query(sql, conn)
        except Exception:
            df.to_sql(table_name, conn, if_exists='append', index=False)
