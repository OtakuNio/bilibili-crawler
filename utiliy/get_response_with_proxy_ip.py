# -*- coding: utf-8 -*-
"""
连接请求及代理IP爬取脚本
参数为:
1.请求连接:url(必选)
2.是否开启代理IP:is_proxy(可选)
3.代理IP列表：proxy_ip_list(可选)
可选参数若不提供可选参数，则使用默认值。
"""
__author__ = 'OtakuNio'

import random
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


def get_response(url, is_proxy=False, proxy_ip_list=None):
    if is_proxy is True:
        if proxy_ip_list is None:
            proxy_ip_list = get_proxy_ip(2)
        try:
            count = 0
            while True:
                error_ip_list = []
                num = random.randint(0, len(proxy_ip_list) - 1)
                while num in error_ip_list:
                    num = random.randint(0, len(proxy_ip_list) - 1)
                proxy_ip = proxy_ip_list[num]
                requests.adapters.DEFAULT_RETRIES = 3
                try:
                    response = requests.get(url=url, headers={'user-agent': UserAgent().random}, timeout=5,
                                            proxies={"http": proxy_ip})
                    if response.status_code == 200:
                        break
                    else:
                        error_ip_list.append(num)
                except Exception:
                    error_ip_list.append(num)
                finally:
                    if len(error_ip_list) == len(proxy_ip_list):
                        count += 1
                        if count == 4:
                            raise Exception()
                        proxy_ip_list = get_proxy_ip(2)
                        error_ip_list.clear()
        except Exception:
            try:
                for proxy_ip_round in proxy_ip_list:
                    requests.adapters.DEFAULT_RETRIES = 3
                    response = requests.get(url=url, headers={'user-agent': UserAgent().random}, timeout=5,
                                            proxies={"http": proxy_ip_round})
                    if response.status_code == 200:
                        break
                if response.status_code != 200:
                    response = requests.get(url=url, headers={'user-agent': UserAgent().random})
            except Exception:
                response = requests.get(url=url, headers={'user-agent': UserAgent().random})
    else:
        response = requests.get(url=url, headers={'user-agent': UserAgent().random})
    if response.status_code == 200:
        response.encoding = 'utf-8'
        return response
    else:
        return None


def get_proxy_ip(page_size=1):
    proxy_ip_list = []
    for page in range(1, page_size + 1):
        url = "https://ip.jiangxianli.com/?page={}".format(page)
        response = requests.get(url)
        bs = BeautifulSoup(response.text, "lxml")
        tr_list = bs.find("tbody").find_all("tr")
        for tr in tr_list:
            if tr.contents[0].string is not None:
                proxy_ip = check_proxy_ip(tr.contents[0].string, tr.contents[1].string)
                if proxy_ip is not None:
                    proxy_ip_list.append(proxy_ip)
    return proxy_ip_list


def check_proxy_ip(ip, port):
    try:
        proxy_ip = "http://{}:{}".format(ip, port)
        requests.adapters.DEFAULT_RETRIES = 3
        response = requests.get(url="http://httpbin.org/ip", timeout=5, proxies={"http": proxy_ip})
        if response.json()['origin'] == ip:
            return proxy_ip
        else:
            return None
    except Exception:
        return None
