import time
import string
from multiprocessing import Process, Queue
import jieba
import threading
import os
import matplotlib.pyplot as plt

lock = threading.Lock()


class Map(Process):
    def __init__(self, file_queue, dict_queue):
        """
        :param file_queue: 等待处理的文件，以队列形式储存
        :param dict_queue: 字典队列，等待加入总字典
        """
        super().__init__()
        self.file_queue = file_queue
        self.dict_queue = dict_queue

    def run(self):
        """
        去除非文本字符，并且删去停用词之后进行词频统计
        :return:
        """
        count = 0
        stop_list = []
        with open('stopwords_list.txt', 'r') as f:
            while True:
                line = f.readline()
                if not line:
                    break
                line = line.strip()  # 去除\n
                stop_list.append(line)

        stop = string.punctuation + '0123456789，。！…*（）-+=【】；：[]丶、~《》～？”' + ' ' + '\xa0' + '\n' + '\ue627' + '\u3000'

        while not self.file_queue.empty() or count < 100:
            name = '/Users/xie/PycharmProjects/现代程设/Homework_10 多进程/data/' + self.file_queue.get() + '.txt'
            with open(name, 'r') as f:
                file = f.read()
                # print('Read File: ',file)
            for i in stop:
                file = file.replace(i, '')
            word_list = list(jieba.cut(file))
            word_dict = {}
            for word in word_list:
                if word in stop_list:
                    while word in word_list:
                        word_list.remove(word)

            for word in word_list:
                word_dict[word] = word_dict.get(word, 0) + 1
            self.dict_queue.put(word_dict)
            count += 1
            # print(word_dict)
            # print()
            word_dict = {}

        print(self.name, "CLOSED!")


class Reduce(Process):
    def __init__(self, dict_queue, file_len):
        """
        :param dict_queue: 字典队列
        :param file_len: 文件长度，根据文件长度来停止进程
        """
        super().__init__()
        self.total_dict = {}
        self.dict_queue = dict_queue
        self.file_len = file_len

    def run(self):
        """
        当统计数小于字典长度时维持进程运行
        :return:
        """
        count = 0
        while count < self.file_len:
            lock.acquire()
            word_dict = self.dict_queue.get()
            # print('Process File: ', word_dict)
            for i in word_dict.items():
                self.total_dict[i[0]] = self.total_dict.get(i[0], 0) + i[1]
            count += 1
            if count % 1000 == 0:
                print('Successfully process', count, 'messages.')
            lock.release()
        ls = sorted(self.total_dict.items(), key=lambda x: x[1], reverse=True)
        print(ls[:20])
        print('Dict Queue Empty! Process End!')


class MainProcess:
    def __init__(self, file_num):
        """
        初始化函数，传入一个列表，为文件的初始数字与终止数字
        :param file_num:
        """
        self.file_num = file_num
        self.file_len = file_num[1] - file_num[0] + 1
        self.file_queue = Queue(maxsize=0)  # 队列有最大值 maxsize = 32767
        self.dict_queue = Queue()

    def multi_process(self, process_num):
        """
        主进程，负责创建多线程与读入数据
        :param process_num:
        :return:
        """


        reduce_process = Reduce(dict_queue=self.dict_queue, file_len=self.file_len)
        p_list = []
        for i in range(process_num):
            p_list.append(Map(file_queue=self.file_queue, dict_queue=self.dict_queue))
        p_list.append(reduce_process)

        for i in p_list:
            i.start()
            print('Thread Start! ', i.name)

        """
        在进程开始之后再读入数据，以避免出现一次性读入全部数据导致超过队列最大长度
        """
        for i in range(self.file_num[0], self.file_num[1] + 1):
            self.file_queue.put(str(i))

        for i in p_list:
            i.join()

        print('All Thread Finished!')


# 文件数：131604-220315 队列最大处理文件数32767
# @profile

def time_test():
    time_dict = {}
    for i in range(1, 16):
        start = time.time()
        mp = MainProcess(file_num=[131604, 140000])
        mp.multi_process(process_num=i)
        end = time.time()
        print("Thread:", i, "Run time:", end - start)
        time_dict[i] = end - start
    plt.figure(figsize=(16, 9))
    plt.title('Run Time VS Processes on All data')
    plt.xlabel('Processes')
    plt.ylabel('Run Time')
    plt.plot(time_dict.keys(), time_dict.values())
    plt.savefig('time.jpg')

def order_test():
    mp = MainProcess(file_num=[140000, 140100])
    mp.multi_process(process_num=10)


def main():
    start = time.time()
    mp = MainProcess(file_num=[131604, 220315])
    mp.multi_process(process_num=16)
    end = time.time()
    print("Thread:", 16, "Run time:", end - start)

    """
    mp.file_num = [161605, 191605]
    mp.multi_process(process_num=20)
    mp.file_num = [191606, 220315]
    mp.multi_process(process_num=20)
    """

    print('End!')


if __name__ == '__main__':
    main()

# kernprof -l -v Homework_10.py
