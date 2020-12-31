import jieba
import string
import word2vec
from scipy.spatial.distance import cdist
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, HashingVectorizer, TfidfTransformer, TfidfVectorizer
import pandas as pd

jieba.add_word('没有良心')

def read_file(file_path, language):  # 读取文件的统一函数，利用language区分中英文，返回一个列表
    with open(file_path, mode='r') as f:
        data = f.read()
        if language == 'en':
            data = str(data).lower()
            for i in string.punctuation:
                data.replace(i, '')
            data = data.split()
        elif language == 'ch':
            data = list(jieba.cut(data))
    return data


def count_freq(data, stop_list=[]):  # data为字符列表，stop_list为停用词表，词频统计函数
    list_dict = {}
    data = data
    for word in data:
        if word not in stop_list and word[0].isalpha():
            list_dict[word] = list_dict.get(word, 0) + 1
    return list_dict


def add_stoplist(word_ls):  # word_ls为停用词，手动输入一个停用词列表进行添加，写入文件
    with open('stoplist.txt', mode='a+') as f:
        data = list(f.read().split())
        for word in word_ls:
            if word not in data:
                f.write(word + ' ')


def find_high_freq(list_dict, time=20):  # list_dict为词频字典，time为输入高频词个数，返回降序排序的前time个高频词
    list = sorted(list_dict.items(), key=lambda x: x[1], reverse=True)
    return list[:time]


def process_data(file_path, language, stop_list):  # 对数据进行一些处理，从文本中移除停用词，为进行向量化准备
    with open(file_path, mode='r', errors="ignore") as f:
        data = f.readlines()
        if language == 'en':
            with open('processed_en.txt', mode='w') as f1:
                f1.write('')  # 清空储存的之前保存的文件
        elif language == 'ch':
            with open('processed_ch.txt', mode='w') as f1:
                f1.write('')  # 同上

        for line in data:
            if language == 'en':
                line = line.lower()
                for i in string.punctuation:
                    line.replace(i, '')
                line = line.split()
            elif language == 'ch':
                line = list(jieba.cut(line))

            for word in line:
                if word in stop_list:
                    while word in line:
                        line.remove(word)

            if language == 'en':
                with open('processed_en.txt', mode='a') as f1:
                    for i in line:
                        f1.write(i + ' ')
                    f1.write('\n')
            elif language == 'ch':
                with open('processed_ch.txt', mode='a') as f1:
                    for i in line:
                        if i != '\n':
                            f1.write(i + ' ')
                    f1.write('\n')
    return


def create_word2vec():  # 进行word2vec向量化
    word2vec.word2vec('processed_en.txt', 'enWord2Vec.bin', size=10)

def create_tfidf(file_path):  # 创建tf_idf词向量，返回词向量矩阵
    data = []
    with open(file_path, mode='r') as f:
        while True:
            line = f.readline()
            if not line:
                break
            line.strip("\n")
            data.append(line)
    tf = TfidfVectorizer(use_idf=True, smooth_idf=True, norm=None)
    discuss_tf = tf.fit_transform(data)
    discuss_tf = discuss_tf.toarray()
    return discuss_tf  # 返回tf-idf矩阵

def cal_dist(tf_model, time):  # 以tf-idf为权重，计算矩阵距离与重心
    tf_data = []  # 前time个句子之间的距离
    count = 0
    avg = np.mean(tf_model)
    avg_count = find_nearest_sentence(tf_model, [avg], 1) # 查找距离中心最近的句子
    for x in tf_model[:time]: # 计算最短距离邻接矩阵
        line_data = []
        for y in tf_model[:time]:
            line_data.append(sum(abs(x - y)))
        tf_data.append(line_data)
    return avg_count, tf_data # 返回重心句子所在位置，与一个距离的邻接矩阵
    # return sum_array

def find_sentence(file_path,place): #返回某行句子
    with open(file_path,mode='r') as f:
        for i in range(place):
            f.readline()
        return str(f.readline())

def find_nearest_sentence(input_matrix,need_find, size):
    '''
    采用绝对值距离进行寻找
    :param input_matrix: 输入的词向量，借此寻找
    :param need_find: 需要被寻找的词向量
    :return: 返回一个列表，是最接近数据的位置
    '''
    count_ls = [0 for i in range(size)] # 为储存寻找到位置的列表
    dist_ls = [99999999 for i in range(size)] # 为储存最短距离的列表
    count = 0 # 为目前查找到数据的位置
    for i in input_matrix:
        for j in range(size):
            if sum(abs(need_find[j]-i)) < dist_ls[j]:
                dist_ls[j] = sum(abs(need_find[j]-i))
                count_ls[j] = count
        count += 1
    return count_ls

def make_wordcloud(file_path):  # 创建词云
    from wordcloud import WordCloud
    import matplotlib as plt
    from PIL import Image
    with open(file_path,mode='r') as f:
        data = f.read()
        data = data.split()
        data = ' '.join(data)
    word_cloud = WordCloud(font_path='/System/Library/Fonts/PingFang.ttc',
                           background_color='white',
                           width=2000,
                           height=2000,
                           max_font_size=200,
                           min_font_size=10,
                           mode='RGBA')
    word_cloud.generate(data)
    word_cloud.to_file('WordCloud.png')
    return

def cluster(data,n_clusters): # 聚类分析函数
    from sklearn.cluster import KMeans
    kmeans = KMeans(n_clusters=n_clusters) # 创建聚类模型
    kmeans.fit(data)
    return (kmeans.cluster_centers_) # 返回聚类中心

def process_file(file_path,language,processed_file_path,stop_list_path):
    '''
    :param file_path: 源文件路径
    :param language: 文件语言
    :param processed_file_path: 处理后文件的储存路径
    :param stop_list_path: 停用词表路径
    '''
    data = read_file(file_path, language) # 先读取文件
    stop_list = read_file(stop_list_path, language) # 然后读取停用词表
    words_dict = count_freq(data, stop_list) # 进行词频统计
    high_freq = find_high_freq(words_dict, 20) # 寻找高频词
    print(high_freq) # 输出高频词
    process_data(file_path, language, stop_list) # 处理文件格式，删去停用词
    tf_model = create_tfidf(processed_file_path) # 创建tf-idf矩阵
    place, vect = cal_dist(tf_model, 10) # 利用tf-idf矩阵寻找句子重心
    print(place[0], find_sentence(file_path, place[0])) # 输出找到的重心句子
    print(vect)
    cluster_centers = cluster(tf_model,10) # 最后进行聚类分析
    weighted_place = find_nearest_sentence(tf_model,cluster_centers,len(cluster_centers))
    for i in range(len(weighted_place)):
        print('Cluster'+str(i)+':'+str(find_sentence(file_path,weighted_place[i])))
    return

def main():
    process_file('tweets_apple_stock.txt','en','processed_en.txt','stopwords_list.txt')
    process_file('online_reviews_texts.txt','ch','processed_ch.txt','stopwords_list.txt')
    make_wordcloud('processed_en.txt')
    make_wordcloud('processed_ch.txt')

main()

# add_stoplist(['here','take','would','please','me','their','big','may','than','there','do','very'])
