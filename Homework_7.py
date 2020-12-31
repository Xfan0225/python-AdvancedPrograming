import os
from memory_profiler import profile as memory_profile
from functools import wraps
from tqdm import tqdm
import math
import playsound
import pickle


class Test:
    """
    测试类，进行运行时间测试，运行内存测试等
    """
    def __init__(self, num):
        self.num = num

    def mem_test(self):
        """
        内存测试，通过创建一个大列表实现
        :return:
        """
        ls = []
        for i in range(self.num):
            ls.append([j * j for j in range(i)])
        return ls

    def time_test(self):
        """
        运行时间测试，利用进行高维乘法实现，并且利用tqdm库输出进度条
        :return:
        """
        count = 1
        for i in tqdm(range(1, self.num * 1000)):
            count *= math.sqrt(i)
        return count

    def dump_test(self, file_path, file):
        """
        对之前创建的大列表进行dump
        :param file_path: 文件路径
        :param file: 需要dump的文件
        :return:
        """
        with open(file_path, 'wb') as f:
            pickle.dump(file, f)

    def load_test(self, file_path):
        """
        对之前创建的大列表进行load
        :param file_path: 文件路径
        :return:
        """
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
        return data


def check_path(file_path):
    """
    检测文件路径是否存在
    :param file_path:文件路径
    :return:
    """
    def decorator(func):
        @wraps(func)
        def check(*args, **kwargs):
            """
            检测输入的是文件夹，还是文件名。如果是文件夹则创建文件夹，否则创建文件
            :param args:
            :param kwargs:
            :return:
            """
            if not os.path.exists(file_path):
                print("Warning! File【"+file_path+"】Not Exist!\nInvalid File Has Been Created Automatically!")
                if '.' in file_path:
                    with open(file_path, 'wb') as f:
                        pass
                else:
                    os.mkdir(file_path)
            return func
        return check
    return decorator


def make_sound(func):
    """
    播放声音装饰器，注意声音文件路径不能有中文
    :param func:
    :return:
    """
    def sound(*args, **kwargs):
        playsound.playsound('/Users/xie/Desktop/test.m4a')
        print('Music Played!')
        return func(*args, **kwargs)
    return sound



@memory_profile
#@profile
def main():
    """
    进行各种测试
    :return:
    """
    file_path = 'test.pkl'
    test = Test(num=1000)
    file = test.mem_test()
    test.time_test()
    test.dump_test(file_path=file_path, file=file)
    test.load_test(file_path=file_path)


@make_sound
def dump_test(file_path):
    @check_path(file_path=file_path)
    def _test(path):
        data = Test(num=1000)
        file = data.mem_test()
        file.dump_test(file_path=path, file=file)
    _test(file_path)


#main()

"""
对发声功能与路径功能进行测试
"""
dump_test('nontest')

# kernprof -l -v Homework_7.py
