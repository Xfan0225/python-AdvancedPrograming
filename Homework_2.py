import pandas as pd
import jieba
import numpy as np
import datetime
import matplotlib.pyplot as plt
import folium
from folium.plugins import HeatMap


def read_data(file_path='weibo.txt', index=['评论', '经度', '纬度', '时间'], sep='\t'):
    """
    读入weibo数据文件，储存为dataframe
    :param file_path: 文件读取路径
    :param index: 行索引
    :param sep: 文件间隔符
    :return: 返回一个文件的dataframe
    """
    if index:
        data = pd.read_csv(file_path, sep=sep, header=None, names=index)
    else:
        data = pd.read_csv(file_path, sep=sep, header=0, index_col=0)
    return data


def read_words(file_path):
    '''
    读入词典文件，储存为列表
    :param file_path: 词典文件路径
    :return: 返回词典的列表
    '''
    word_list = []
    with open(file_path, mode='r') as f:
        while True:
            line = f.readline()
            if not line:
                break
            line = line.strip()  # 去除\n
            word_list.append(line)
    return word_list


def add_jieba_words(word_list):
    '''
    为jieba库增加词汇
    :param word_list: 词汇列表
    :return: 无返回
    '''
    for i in word_list:
        jieba.add_word(i)
    return


def trans_long_and_lat(long, lat):
    '''
    经纬度转换函数，输入long为经度，lat为纬度，返回所在省市的字符串，利用百度地图api
    :param long: 经度
    :param lat: 纬度
    :return: 省市字符串变量
    '''
    import json
    import urllib.request

    url = 'http://api.map.baidu.com/reverse_geocoding/v3/?ak=d3BbpYwib3lgsUVMHmlG6igaF2izxxEA&output=json&location=' + str(
        lat) + ',' + str(long)
    req = urllib.request.urlopen(url)  # json格式的返回数据
    res = req.read().decode("utf-8")
    print(res)
    res = json.loads(res)
    json_res = res.get('result')
    address = json_res.get('addressComponent')

    province = address.get('province')
    city = address.get('city')
    district = address.get('district')
    format_adress = json_res.get('formatted_address')

    # print([province,city,district,format_adress])
    return [province, city, district, format_adress]


def pd_process(data):
    '''
    处理dataframe中的数据，删除微博信息中的不必要信息，并且将时间字符串转化为时间数据
    :param data: 输入的dataframe
    :return: 返回一个处理后的dataframe
    '''
    import string
    comment_ls = []
    time_ls = []
    stop = '0123456789，。！@#…*（）-+=】【】；：[]丶、~《》～？”' + string.punctuation
    long_ls = []
    lat_ls = []
    loction_ls = []
    for i in data['评论']:
        i = jieba.lcut(i)
        for j in stop:
            while j in i:
                i.remove(j)
        if 'http' in i:
            comment_ls.append(i[:i.index('http')])

    for i in data['时间']:
        time_ls.append(pd.Timestamp(i))

    for i in data['经度']:
        long_ls.append(i)
    for i in data['纬度']:
        lat_ls.append(i)

    for i in range(len(long_ls)):
        loction_ls.append(trans_long_and_lat(long_ls[i], lat_ls[i]))

    comment_pd = pd.DataFrame(dict(comment=comment_ls))
    time_pd = pd.DataFrame(dict(time=time_ls))
    location_pd = pd.DataFrame(dict(location=loction_ls))

    process_pd = pd.concat([comment_pd, location_pd, time_pd], axis=1)
    process_pd.to_csv('processed_data.csv')
    return process_pd


def process_early_data():
    '''
    创建最早使用的csv文件，转化经纬度等，仅仅需要执行一次
    :return: 不返回
    '''
    data = read_data()
    emotion = ['anger', 'disgust', 'fear', 'joy', 'sadness']
    for e in emotion:
        add_jieba_words(read_words('emotion_lexicon/' + e + '.txt'))
    pd_process()


def process_emotion(data):
    '''
    传入一个dataframe文件，将处理后的心情作为新列附加并返回
    :param data: 传入的dataframe
    :return: 返回一个dataframe，心情作为两个新列返回，分别是所有心情，与最突出心情
    '''
    comment = data['comment']
    emotions = ['anger', 'disgust', 'fear', 'joy', 'sadness']
    emotion_count = []
    distinct_emotion_count = []
    anger_count = count_emotion(emotion='anger')
    disgust_count = count_emotion(emotion='disgust')
    fear_count = count_emotion(emotion='fear')
    joy_count = count_emotion(emotion='joy')
    sadness_count = count_emotion(emotion='sadness')
    for line in comment:
        temp_emo_count = [0, 0, 0, 0, 0]
        temp_emo_count[0] = anger_count(comment=line)
        temp_emo_count[1] = disgust_count(comment=line)
        temp_emo_count[2] = fear_count(comment=line)
        temp_emo_count[3] = joy_count(comment=line)
        temp_emo_count[4] = sadness_count(comment=line)
        sum_emo = sum(temp_emo_count)
        # temp_emo_count = [temp_emo_count[i]/sum_emo for i in range(5)]
        if max(temp_emo_count):
            temp_emo_count = [temp_emo_count[i] / sum_emo for i in range(5)]
            distinct_emotion_count.append(emotions[temp_emo_count.index(max(temp_emo_count))])
        else:
            distinct_emotion_count.append('NULL')
        emotion_count.append(temp_emo_count)
    emotions_df = pd.DataFrame(dict(emotions=emotion_count))
    distinct_emotion_df = pd.DataFrame(dict(dist_emotion=distinct_emotion_count))
    data = pd.concat([data, emotions_df, distinct_emotion_df], axis=1)
    # data.to_csv('processed_data_with_emotion.csv')
    return data


def count_emotion(emotion):
    '''
    闭包函数，输入一个emotion，返回一个处理函数（使用该函数的时候需要传入句子）
    :param emotion_list: 需要处理的心情列表
    :param comment: 一个评论句子
    :return:
    '''
    emotion_list = read_words('emotion_lexicon/' + emotion + '.txt')

    def count(comment):
        nonlocal emotion_list
        num = 0
        for i in list(comment):
            if i in emotion_list:
                num += 1
        return num

    return count


def create_time_emotion_figure(data):
    '''
    创建时间与心情关系的图，并且时间心情地点热力图
    :param data: dataframe格式的数据
    :return:无返回值，输出一个时间与心情相关的图片
    '''

    emotions = ['anger', 'disgust', 'fear', 'joy', 'sadness']
    time_series = pd.date_range('2014-07-08', '2014-07-09', freq='H')
    time_series_dict = {}
    for time in time_series:
        time_series_dict[time] = np.array([0, 0, 0, 0, 0])
    for index, line in data.iterrows():
        # print(line)
        quarter_time = lambda dt: datetime.datetime(dt.year, dt.month, dt.day, dt.hour)
        hour_time = quarter_time(pd.Timestamp(line.time))
        time_series_dict[hour_time] = time_series_dict.get(hour_time) + np.array(line.emotions)

    y_ls = [list(time_series_dict.values())[i]/sum(time_series_dict.values()) for i in range(5)]
    plt.figure(figsize=(16, 9))
    plt.plot(time_series, y_ls, linewidth=2)
    plt.legend(emotions)
    plt.savefig('demo.jpg')

    '''
    以下是创建热力图的部分
    '''
    raw_data = read_data()
    long_ls = list(raw_data['经度'])
    lat_ls = list(raw_data['纬度'])
    grat_ls = []
    count = 0
    for i in range(5):
        grat_emo_ls = []
        for index, line in data.iterrows():
            if line.emotions[i] != 0:
                grat_emo_ls.append([lat_ls[count], long_ls[count], line.emotions[i] * 100])
            count += 1
        grat_ls.append(grat_emo_ls)
        count = 0
    print(grat_ls[0])
    for i in range(5):
        map_osm = folium.Map(location=[39, 116], zoom_start=1)
        HeatMap(grat_ls[i]).add_to(map_osm)
        map_osm.save('Heatmap/' + emotions[i] + '.html')

    return


if __name__ == '__main__':
    data = read_data('processed_data.csv', index=0, sep=',')
    data = process_emotion(data)
    # data = pd.read_csv('processed_data_with_emotion.csv')
    create_time_emotion_figure(data)
