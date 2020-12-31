import copy
import os
from PIL import Image
from PIL import ImageFilter
import matplotlib.pyplot as plt
import numpy as np


class Filter:
    def __init__(self, image, para_list):
        self.image = image
        self.para_list = para_list

    def filter(self, method):
        """
        过滤器，对于传入的图像，采用method对其进行过滤
        :param method: 过滤的方法
        :return:
        """
        if method == 'findedges':
            self.image = FindEdges(self.image, self.para_list).find_edges()
        elif method == 'sharpen':
            self.image = Sharpen(self.image, self.para_list).sharp()
        elif method == 'blur':
            self.image = Blur(self.image, self.para_list).blur()
        elif method == 'reshape':
            self.image = Reshape(self.image, self.para_list).reshape()


class FindEdges(Filter):
    """
    过滤器类的子类，继承其中的图像与参数列表
    """

    def __init__(self, image, para_list):
        Filter.__init__(self, image, para_list)

    def find_edges(self):
        """
        查询图像边界
        :return:
        """
        edge = self.image.filter(ImageFilter.FIND_EDGES)
        return edge


class Sharpen(Filter):
    def __init__(self, image, para_list):
        Filter.__init__(self, image, para_list)

    def sharp(self):
        sharped_img = self.image.filter(ImageFilter.SHARPEN)
        return sharped_img


class Blur(Filter):
    def __init__(self, image, para_list):
        Filter.__init__(self, image, para_list)

    def blur(self):
        blured_img = self.image.filter(ImageFilter.BLUR)
        return blured_img


class Reshape(Filter):
    def __init__(self, image, para_list):
        Filter.__init__(self, image, para_list)

    def reshape(self):
        shape = self.para_list['reshape']
        return self.image.resize(shape, Image.ANTIALIAS)


class ImageShop:
    """
    图像处理类，利用两个类变量列表保存Filter实例，储存处理后的照片与原图
    """
    raw_list = []
    processed_list = []

    def __init__(self, file_type, file_path):
        self.file_type = file_type
        self.file_path = file_path
        self.raw_list = ImageShop.raw_list
        self.processed_list = ImageShop.processed_list

    def load_images(self):
        """
        加载图像
        :return:
        """
        for file_name in os.listdir(self.file_path):
            if file_name.split('.')[-1] == self.file_type:
                self.raw_list.append(Filter(Image.open(self.file_path + '/' + file_name), {}))
                print('Successfully Read:' + file_name)
        self.processed_list = copy.deepcopy(self.raw_list)

    def __batch_ps(self, method):
        """
        批处理内函数
        :param method:
        :return:
        """
        for image in self.processed_list:
            image.filter(method)

    def batch_ps(self, methods):
        """
        批处理外函数
        :param methods: 处理的方法列表，按照顺序进行批处理
        :return:
        """
        for method in methods:
            if method[0] == 'reshape':
                for image in self.processed_list:
                    image.para_list = {'reshape': method[1]}
            self.__batch_ps(method[0])

    def display(self, column, line):
        """
        展示图像
        :param column: 行数
        :param line: 列数
        :return:
        """
        plt.figure("Processed Image")
        for i in range(column * line):
            plt.subplot(column, line, i + 1)
            plt.axis('off')
            plt.imshow(self.processed_list[i].image)
        plt.savefig('Processed.jpg')

    def compare(self, column, line):
        """
        对比图像，生成对比图
        :param column: 行数
        :param line: 列数
        :return:
        """
        plt.figure(figsize=(32, 18))
        for i in range(column * line):
            plt.subplot(column, line * 2, i * 2 + 1)
            plt.axis('off')
            plt.imshow(self.raw_list[i].image)
            plt.subplot(column, line * 2, i * 2 + 2)
            plt.axis('off')
            plt.imshow(self.processed_list[i].image)
            fig1 = np.array(self.raw_list[i].image)
            fig2 = np.array(self.processed_list[i].image)
            distance = np.sqrt(np.sum((fig1 - fig2) ** 2))
            print("Figure" + str(i + 1) + ' Distance: ', distance)
        plt.savefig('compare.jpg')


class TestImageShop:
    def __init__(self, type, img_path, method_ls, display, compare):
        self.type = type
        self.img_path = img_path
        self.method_ls = method_ls
        self.display = display
        self.compare = compare

    def test(self):
        """
        测试函数，进行图像批处理，并展示对比等
        :return:
        """
        ps = ImageShop(self.type, self.img_path)
        ps.load_images()
        ps.batch_ps(self.method_ls)
        if self.display: ps.display(3, 3)
        if self.compare: ps.compare(3, 3)


def main():
    test = TestImageShop('jpeg', 'pictures', [('blur', 0), ('sharpen', 0), ('findedges', 0)], True, True)
    test.test()

if __name__ == '__main__':
    main()
