from threading import Thread, currentThread, Lock
import time
import os
from bs4 import BeautifulSoup
from urllib.request import urlopen, urlretrieve
import queue
import pymongo

# url = 'https://www.51voa.com/VOA_Standard_1.html'  # 1-35

front = 'https://www.51voa.com'
download_count = 0

class DownloadVOA(Thread):
    lock = Lock()
    global my_col

    def __init__(self, url_queue):
        super().__init__()
        self.url_queue = url_queue

    def run(self):
        """
        下载网页数据，包括文章id，文章标题，文本内容，mp3下载路径，作者，日期，相关文章（存为字典列表）
        :return:
        """
        global download_count
        while not self.url_queue.empty():
            i = self.url_queue.get()
            if my_col.count_documents({'ID': i.attrs['href'].split('-')[-1].split('.')[0]}) > 0: # 假如已存在文章信息
                self.lock.acquire()
                print('ID', i.attrs['href'].split('-')[-1].split('.')[0], 'Exists!')
                self.lock.release()
                continue # 跳过下载部分
            new_url = front + i.attrs['href']
            new_html = BeautifulSoup(urlopen(new_url).read())
            # 获取各种属性（并不下载mp3）
            file_dict = {'ID': i.attrs['href'].split('-')[-1].split('.')[0],
                         'title': i.text,
                         'text': new_html.find('div', class_='Content').text,
                         'mp3_path': new_html.find_all('a', id='mp3')[0].attrs['href']}
            try:
                file_dict['author'] = new_html.find('span', class_="byline").text[3:]  # 作者
            except AttributeError as e:
                file_dict['author'] = 'None'
            try:
                file_dict['date'] = new_html.find('span', class_="datetime").text  # 时间
            except AttributeError as e:
                file_dict['date'] = 'None'
            _related_articles = []
            for i in new_html.find('ol'): # 将相关文章储存为字典列表，包含id，标题与文章路径
                articles = {'id': i.find('a').attrs['href'].split('-')[-1].split('.')[0],
                            'title': i.find('a').text,
                            'path': front + '/VOA_Standard_English/' + i.find('a').attrs['href']}
                _related_articles.append(articles)
            file_dict['related_articles'] = _related_articles
            x = my_col.insert_one(file_dict) # 存入数据库
            print('Download ID:', file_dict['ID'], 'Success!')
            download_count += 1


class MainProcess:
    """
    主线程，来源于Homework11
    """
    def __init__(self, pages_num, thread_num):
        self.pages_num = pages_num
        self.thread_num = thread_num
        self.url_queue = queue.Queue()

    def make_url_queue(self):
        for i in range(1, self.pages_num + 1):
            url = 'https://www.51voa.com/VOA_Standard_' + str(i) + '.html'
            html = BeautifulSoup(urlopen(url).read())
            for j in html.find_all('a', target='_blank'):
                self.url_queue.put(j)

    def start(self):
        thread_list = []
        for i in range(self.thread_num):
            td = DownloadVOA(url_queue=self.url_queue)
            thread_list.append(td)

        for i in thread_list:
            i.start()
            print(i.name, ' Start!')

        for i in thread_list:
            i.join()

        print('Download: ', download_count, 'Process End!')


def load_data(keywords, attr, blur=True, max_num=5):
    """
    查找函数，从数据库中进行查找
    :param keywords: 查找的关键词
    :param attr: 查找的属性
    :param blur: 是否模糊匹配，默认为模糊匹配
    :param max_num: 查找最大项目数
    :return:
    """
    if blur:
        keywords = {'$regex': keywords} # 模糊匹配
    search_words = {attr: keywords}
    ans = my_col.find(search_words).limit(5)
    for i in ans:
        print(i['text']) # 输出找到属性对应的文本
        print('--------------------\n')
    print('FIND', my_col.count_documents(search_words), 'ANS! SHOW TOP', max_num) # 输出找到的结果总数


if __name__ == '__main__':
    my_client = pymongo.MongoClient("mongodb://localhost:27017/")
    my_db = my_client["VOA_info"]
    my_col = my_db["sites"]
    #my_col.delete_many({}) #删库跑路
    #mp = MainProcess(pages_num=10, thread_num=8)
    #mp.make_url_queue()
    #mp.start()
    load_data('Trump', 'text', blur=True)
