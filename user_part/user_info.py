# -*- coding: utf-8 -*-
"""
用户信息爬取脚本
参数为某用户的uid
"""
__author__ = 'OtakuNio'

import pandas as pd
from sqlalchemy import create_engine
from get_response_with_proxy_ip import get_response, get_proxy_ip


def user_info_main(uid):
    print("user_info")
    my_url1 = 'https://api.bilibili.com/x/space/acc/info?mid={}'.format(uid)
    my_url2 = 'https://api.bilibili.com/x/web-interface/card?mid={}'.format(uid)
    response_1 = get_response(my_url1)
    response_2 = get_response(my_url2)
    save_to_database_user_info(
        pd.DataFrame(get_data_user_info(response_1.json()['data'], response_2.json()['data']['card']), index=[1]),
        'user_info')
    print("user_info-finish")


def get_data_user_info(response_json_1, response_json_2):
    if response_json_1['vip']['status'] == 1:
        vip_info = response_json_1['vip']['type']
    else:
        vip_info = response_json_1['vip']['status']
    user_info_data = {
        'uid': response_json_1['mid'],
        'name': response_json_1['name'],
        'sign': response_json_1['sign'],
        'birthday': response_json_1['birthday'],
        'sex': response_json_1['sex'],
        'level': response_json_1['level'],
        'vip': vip_info,
        'friend': response_json_2['friend'],
        'attention': response_json_2['attention'],
        'fans': response_json_2['fans'],
        'official': response_json_1['official']['title'],
        'live_room_status': response_json_1['live_room']['roomStatus'],
        'live_status': response_json_1['live_room']['liveStatus'],
        'silence': response_json_1['silence'],
    }
    return user_info_data


def save_to_database_user_info(df, table_name):
    # conn = create_engine("mysql+pymysql://{}:{}@{}:{}/{}?charset={}".format('用户名', '密码', '数据库IP地址', '端口号', '数据库名',
    # '字符编码'))
    is_table_exist = True
    is_data_exist = True
    conn = create_engine(
        "mysql+pymysql://{}:{}@{}:{}/{}?charset={}".format('root', '123456', 'localhost', '3306', 'test', 'utf8mb4'))
    try:
        sql = "select * from {} where uid='{}';".format(table_name, df.loc[1, 'mid'])
        if pd.read_sql_query(sql, conn).empty:
            is_data_exist = False
    except Exception:
        is_table_exist = False
    if (is_table_exist == False) or (is_data_exist == False):
        df.to_sql(table_name, conn, if_exists='append', index=False)
    else:
        try:
            sql = "delete from {} where uid='{}'".format(table_name, df.loc[1, 'mid'])
            pd.read_sql_query(sql, conn)
        except Exception:
            df.to_sql(table_name, conn, if_exists='append', index=False)
