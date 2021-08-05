# -*- coding: utf-8 -*-
"""
词频分析脚本
参数为:
1.待进行词频分析的文本文件:analysis_file(必选)
2.词云生成背景图:background_pic(必选)
3.词频分析统计输出词汇个数:lexical_num(可选)
4.文件保存路径:save_path(可选)
5.词频分析保存文件名:save_file_name(可选)
6.词云保存文件名:save_pic_name(可选)
可选参数若不提供可选参数，则使用默认值。
"""
__author__ = 'OtakuNio'

import re
import collections
import numpy as np
import jieba
import wordcloud
from PIL import Image
import matplotlib.pyplot as plt


def lexical_frequency_analysis_main(analysis_file, background_pic, lexical_num, background_color='black',save_path='',
                                    save_file_name='save_file',
                                    save_pic_name='save_pic'):
    file = open(analysis_file, 'rt', encoding='utf-8')
    raw_string_data = file.read()
    file.close()
    segment_word_list = jieba.cut(raw_string_data, cut_all=False)
    filter_word_list = []
    for word in segment_word_list:
        s = re.sub('[^\u4e00-\u9fa5a-zA-Z0-9]+', '', word)
        if len(s) >= 2:
            filter_word_list.append(word)
    remove_words = [u'的', u'，', u'和', u'是', u'随着', u'对于', u'对', u'等', u'能', u'都', u'。', u' ', u'、', u'中', u'在', u'了',
                    u'通常', u'如果', u'我们', u'需要']
    output_word_list = []
    for word in filter_word_list:
        if word not in remove_words:
            output_word_list.append(word)
    word_counts_data = collections.Counter(output_word_list)
    word_counts_top = word_counts_data.most_common(lexical_num)
    file = open(save_path+'/'+save_file_name+'.txt', 'wt', encoding='utf-8')
    for word_count in word_counts_top:
        file.write(str(word_count)+'\n')
    file.close()
    mask = np.array(Image.open(background_pic))
    wc = wordcloud.WordCloud(font_path='C:/Windows/Fonts/simhei.ttf', mask=mask,
                             max_words=200, max_font_size=100,scale=32,background_color=background_color)
    wc.generate_from_frequencies(word_counts_data)
    image_colors = wordcloud.ImageColorGenerator(mask)
    wc.recolor(color_func=image_colors)
    plt.imshow(wc)
    plt.axis('off')
    plt.show()
    wc.to_file(save_path+'/'+save_pic_name+'.jpg')
