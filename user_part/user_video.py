# -*- coding: utf-8 -*-
"""
用户视频爬取脚本
参数为某用户的uid
"""

import time
import pandas as pd
from sqlalchemy import create_engine
from get_response_with_proxy_ip import get_response, get_proxy_ip


def user_video_main(uid):
    print("user_video")
    my_url1 = 'http://api.bilibili.com/x/space/arc/search?mid={}&pn={}'
    my_url2 = 'https://api.bilibili.com/x/web-interface/view?bvid={}'
    subarea_data, user_video_data = get_data_user_video(uid, my_url1, my_url2)
    save_to_database_user_video(pd.DataFrame(subarea_data), 'user_video_subarea')
    save_to_database_user_video(pd.DataFrame(user_video_data), 'user_video')
    print("user_video-over")


def get_data_user_video(uid, url, video_url):
    proxy_ip_list = get_proxy_ip(2)
    page = 1
    video_bid_list = []
    video_aid_list = []
    video_title_list = []
    video_pubdate_list = []
    video_duration_time_list = []
    video_view_list = []
    video_history_rank_list = []
    subarea_list = []
    subarea_count_list = []
    while True:
        video_page_url = url.format(uid, page)
        response = get_response(video_page_url)
        if response is None:
            break
        video_json_vlist = response.json()['data']['list']['vlist']
        subarea_json_tlist = response.json()['data']['list']['tlist']
        if len(video_json_vlist) == 0 or subarea_json_tlist is None:
            break
        for subarea in subarea_json_tlist:
            subarea_list.append(subarea_json_tlist[subarea]['name'])
            subarea_count_list.append(subarea_json_tlist[subarea]['count'])
        for video in video_json_vlist:
            video_bid_list.append(video['bvid'])
            video_aid_list.append(video['aid'])
            video_title_list.append(video['title'])
        page += 1
        time.sleep(1)
    for video in video_bid_list:
        response = get_response(video_url.format(video), True, proxy_ip_list)
        if response is None:
            video_pubdate_list.append()
            video_duration_time_list.append()
            video_view_list.append()
            video_history_rank_list.append()
        else:
            video_pubdate_list.append(
                time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(response.json()['data']['pubdate'])))
            video_duration_time_list.append(response.json()['data']['duration'])
            video_view_list.append(response.json()['data']['stat']['view'])
            video_history_rank_list.append(response.json()['data']['stat']['his_rank'])
        time.sleep(1)
    subarea_data = {
        'subarea': subarea_list,
        'count': subarea_count_list
    }
    user_video_data = {
        'BV_bvid': video_bid_list,
        'aid': video_aid_list,
        'title': video_title_list,
        'pubdate': video_pubdate_list,
        'duration': video_duration_time_list,
        'view': video_view_list,
        'history_rank': video_history_rank_list
    }
    return subarea_data, user_video_data


def save_to_database_user_video(df, table_name):
    # conn = create_engine("mysql+pymysql://{}:{}@{}:{}/{}?charset={}".format('用户名', '密码', '数据库IP地址', '端口号', '数据库名',
    # '字符编码'))
    conn = create_engine(
        "mysql+pymysql://{}:{}@{}:{}/{}?charset={}".format('root', '123456', 'localhost', '3306', 'test', 'utf8mb4'))
    df.to_sql(table_name, conn, if_exists='replace', index=False)
