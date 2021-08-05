# -*- coding: utf-8 -*-
"""
视频评论爬取脚本
参数为某视频的BV号
"""
__author__ = 'OtakuNio'

import time
import pandas as pd
from sqlalchemy import create_engine
from get_response_with_proxy_ip import get_response, get_proxy_ip


def video_reply_main(bid):
    print("video_reply")
    my_url1 = 'http://api.bilibili.com/x/v2/reply?type=1&sort={}&oid={}&pn={}'
    my_url2 = 'https://api.bilibili.com/x/web-interface/view?bvid={}'
    save_to_database_video_reply(pd.DataFrame(data=get_all_video_reply(get_aid_video_reply(bid, my_url2), my_url1)),
                                 'video_all_reply')
    save_to_database_video_reply(pd.DataFrame(data=get_hot_video_reply(get_aid_video_reply(bid, my_url2), my_url1)),
                                 'video_hot_reply')
    print("video_reply-over")


def get_aid_video_reply(bid, url):
    url = url.format(bid)
    aid = get_response(url).json()['data']['aid']
    return aid


def get_all_video_reply(oid, url):
    proxy_ip_list = get_proxy_ip(2)
    page = 1
    rpid_list = []
    user_id_list = []
    user_name_list = []
    user_sex_list = []
    user_level_list = []
    user_vip_list = []
    message_list = []
    message_length_list = []
    message_like_list = []
    message_time_list = []
    while True:
        reply_page_url = url.format(1, oid, page)
        response = get_response(reply_page_url, True, proxy_ip_list)
        if response is None:
            break
        reply_json_list = response.json()['data']['replies']
        if len(reply_json_list) == 0:
            break
        for reply in reply_json_list:
            rpid_list.append(reply['rpid'])
            user_id_list.append(int(reply['member']['mid']))
            user_name_list.append(reply['member']['uname'])
            user_sex_list.append(reply['member']['sex'])
            user_level_list.append(reply['member']['level_info']['current_level'])
            if reply['member']['vip']['vipStatus'] == 1:
                user_vip_list.append(reply['member']['vip']['vipType'])
            else:
                user_vip_list.append(reply['member']['vip']['vipStatus'])
            message_list.append(reply['content']['message'])
            message_length_list.append(len(reply['content']['message']))
            message_like_list.append(reply['like'])
            message_time_list.append(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(reply['ctime'])))
        page += 1
        time.sleep(1)
    all_reply_data = {
        'rpid': rpid_list,
        'user_id': user_id_list,
        'user_name': user_name_list,
        'user_sex': user_sex_list,
        'user_level': user_level_list,
        'vip': user_vip_list,
        'message': message_list,
        'message_length': message_length_list,
        'like': message_like_list,
        'time': message_time_list
    }
    return all_reply_data


def get_hot_video_reply(oid, url):
    rpid_list = []
    user_id_list = []
    user_name_list = []
    user_sex_list = []
    user_level_list = []
    user_vip_list = []
    message_list = []
    message_length_list = []
    message_like_list = []
    message_time_list = []
    reply_url = url.format(1, oid, 1)
    response = get_response(reply_url)
    hot_reply_json_list = response.json()['data']['hots']
    for reply in hot_reply_json_list:
        rpid_list.append(reply['rpid'])
        user_id_list.append(int(reply['member']['mid']))
        user_name_list.append(reply['member']['uname'])
        user_sex_list.append(reply['member']['sex'])
        user_level_list.append(reply['member']['level_info']['current_level'])
        if reply['member']['vip']['vipStatus'] == 1:
            user_vip_list.append(reply['member']['vip']['vipType'])
        else:
            user_vip_list.append(reply['member']['vip']['vipStatus'])
        message_list.append(reply['content']['message'])
        message_length_list.append(len(reply['content']['message']))
        message_like_list.append(reply['like'])
        message_time_list.append(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(reply['ctime'])))
    hot_reply_data = {
        'rpid': rpid_list,
        'user_id': user_id_list,
        'user_name': user_name_list,
        'user_sex': user_sex_list,
        'user_level': user_level_list,
        'vip': user_vip_list,
        'message': message_list,
        'message_length': message_length_list,
        'like': message_like_list,
        'time': message_time_list
    }
    return hot_reply_data


def save_to_database_video_reply(df, table_name):
    # conn = create_engine("mysql+pymysql://{}:{}@{}:{}/{}?charset={}".format('用户名', '密码', '数据库IP地址', '端口号', '数据库名',
    # '字符编码'))
    conn = create_engine(
        "mysql+pymysql://{}:{}@{}:{}/{}?charset={}".format('root', '123456', 'localhost', '3306', 'test', 'utf8mb4'))
    df.to_sql(table_name, conn, if_exists='replace', index=False)
