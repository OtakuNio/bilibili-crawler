# -*- coding: utf-8 -*-
"""
用户粉丝爬取脚本
参数为某用户的uid
"""
__author__ = 'OtakuNio'

import time
import pandas as pd
from sqlalchemy import create_engine
from get_response_with_proxy_ip import get_proxy_ip, get_response


def user_follower_main(uid):
    print("user_follower")
    my_url1 = 'https://api.bilibili.com/x/relation/followers?vmid={}&pn={}'
    my_url2 = 'http://api.bilibili.com/x/web-interface/card?mid={}'
    save_to_database_user_follower(pd.DataFrame(get_data_user_follower(uid, my_url1, my_url2)), 'user_follower')
    print("user_follower-finish")


def get_data_user_follower(uid, url_1, url_2):
    proxy_ip_list = get_proxy_ip(2)
    page = 1
    follower_id_list = []
    follower_name_list = []
    follower_sex_list = []
    follower_level_list = []
    follower_vip_list = []
    follower_time_list = []
    while page <= 5:
        follower_page_url = url_1.format(uid, page)
        response = get_response(follower_page_url)
        if response is None:
            break
        follower_list_json = response.json()['data']['list']
        if len(follower_list_json) == 0:
            break
        try:
            for follower in follower_list_json:
                follower_id_list.append(follower['mid'])
                follower_name_list.append(follower['uname'])
                if follower['vip']['vipStatus'] == 1:
                    follower_vip_list.append(follower['vip']['vipType'])
                else:
                    follower_vip_list.append(follower['vip']['vipStatus'])
                follower_time_list.append(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(follower['mtime'])))
            page += 1
            time.sleep(1)
        except Exception:
            break;
    for follower in follower_id_list:
        response = get_response(url_2.format(follower), True, proxy_ip_list)
        if response is None:
            follower_sex_list.append('')
            follower_level_list.append('')
        else:
            follower_sex_list.append(response.json()['data']['card']['sex'])
            follower_level_list.append(response.json()['data']['card']['level_info']['current_level'])
        time.sleep(1)
    follower_data = {
        'follower_id': follower_id_list,
        'follower_name': follower_name_list,
        'follower_sex': follower_sex_list,
        'follower_level': follower_level_list,
        'follower_vip': follower_vip_list,
        'follower_time': follower_time_list
    }
    return follower_data


def save_to_database_user_follower(df, table_name):
    # conn = create_engine("mysql+pymysql://{}:{}@{}:{}/{}?charset={}".format('用户名', '密码', '数据库IP地址', '端口号', '数据库名',
    # '字符编码'))
    conn = create_engine(
        "mysql+pymysql://{}:{}@{}:{}/{}?charset={}".format('root', '123456', 'localhost', '3306', 'test', 'utf8mb4'))
    df.to_sql(table_name, conn, if_exists='replace', index=False)
