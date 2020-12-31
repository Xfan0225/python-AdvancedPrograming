from threading import Thread, currentThread, Lock
import time
import os
from bs4 import BeautifulSoup
from urllib.request import urlopen, urlretrieve
import queue

# url = 'https://www.51voa.com/VOA_Standard_1.html'  # 1-35

front = 'https://www.51voa.com'
download_count = 0


class DownloadVOA(Thread):
    def __init__(self, url_queue):
        super().__init__()
        self.url_queue = url_queue

    def run(self):
        global download_count
        while not self.url_queue.empty():
            place, i = self.url_queue.get()
            # 将文件命名为日期+文件名+.mp3
            file_name = 'downloads/' + str(place) + '/' + i.text[i.text.rfind('(') + 1:i.text.rfind(')')] + i.text[:i.text.rfind('(') - 1] + '.mp3'
            text_name = 'downloads/' + str(place) + '/' + i.text[i.text.rfind('(') + 1:i.text.rfind(')')] + i.text[:i.text.rfind('(') - 1] + '.txt'
            new_html = BeautifulSoup(urlopen(front + i.a.attrs['href']).read())  # 进入下载页面

            if os.path.exists(text_name):
                print('Text File Exist! ', text_name)
            else:
                text = new_html.find('div', class_='Content').text #获取文本并存为txt
                with open(text_name, 'w') as f:
                    f.write(text)
                print('Download File: '+text_name)

            if os.path.exists(file_name):
                print('MP3 File Exist! ', file_name)
            else:
                urlretrieve(new_html.find_all('a', id='mp3')[0].attrs['href'], file_name)  # 下载文件
                print('Download File: ' + i.text[i.text.rfind('(') + 1:i.text.rfind(')')] + i.text[:i.text.rfind(
                    '(') - 1] + '.mp3')
                download_count += 1


class MainProcess:
    def __init__(self, pages_num, thread_num):
        self.pages_num = pages_num
        self.thread_num = thread_num
        self.url_queue = queue.Queue()

    def make_url_queue(self):
        for i in range(1, self.pages_num+1):
            if not os.path.exists('downloads/' + str(i)):
                os.mkdir('downloads/' + str(i))
            url = 'https://www.51voa.com/VOA_Standard_' + str(i) + '.html'
            html = BeautifulSoup(urlopen(url).read())
            for j in html.find_all('li'):
                if j.a.attrs.get('target') == '_blank':
                    self.url_queue.put((i, j))

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


if __name__ == '__main__':
    mp = MainProcess(pages_num=1, thread_num=8)
    mp.make_url_queue()
    mp.start()
