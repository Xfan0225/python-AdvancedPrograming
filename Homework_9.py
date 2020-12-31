import os
import abc
import random
import imageio
import jieba
import matplotlib.pyplot as plt
from PIL import Image
from wordcloud import WordCloud
import pandas as pd
from sklearn.decomposition import PCA
from mpl_toolkits.mplot3d import Axes3D


class Plotter(abc.ABC):
    @abc.abstractmethod
    def plot(self, data, *args, **kwargs):
        pass


class PointPlotter(Plotter):
    def __init__(self, size):
        self.size = size

    def create_test_point(self):
        point_list = []
        for i in range(self.size):
            point_list.append(Point(i, random.randint(1, 100)))
        print('Successfully create ', self.size, 'test data!')
        return point_list

    def plot(self, data, *args, **kwargs):
        plt.figure()
        x = []
        y = []
        for point in data:
            x.append(point.x)
            y.append(point.y)

        plt.plot(x, y)
        # plt.show()
        plt.savefig('plot.jpg')


class ArrayPlotter(Plotter):
    def __init__(self, size, dim):
        self.size = size
        self.dim = dim

    def create_test_array(self):
        point_list = []
        for i in range(self.size):
            if self.dim == 2:
                point_list.append(Point(i, random.randint(1, 100)))
            else:
                point_list.append([random.randint(1, 100) for i in range(self.dim)])
        return point_list

    def plot(self, data, *args, **kwargs):
        if self.dim > 3:  # PCA降维
            pca = PCA(n_components=3)
            pca.fit(data)
            data = pca.fit_transform(data)
            print('WARNING:Dim 【', self.dim, '】 > 3. PCA Transformed To 3!')

        x = []
        y = []
        z = []
        for point in data:
            x.append(point[0])
            y.append(point[1])
            z.append(point[2])

        fig = plt.figure()
        ax = Axes3D(fig)
        ax.scatter(x, y, z)
        # plt.show()
        plt.savefig('array_plot_'+str(self.dim)+'.jpg')


class TextPlotter(Plotter):
    def __init__(self, file_path):
        self.file_path = file_path

    def create_test_text(self):
        data = pd.read_csv(self.file_path, sep='\t', header=None, names=['评论', '经度', '纬度', '时间'])
        data_ls = list(data['评论'])
        return data_ls

    def plot(self, data, *args, **kwargs):
        # 停用词表
        stop_list = []
        with open('stopwords_list.txt', 'r') as f:
            while True:
                line = f.readline()
                if not line:
                    break
                line = line.strip()  # 去除\n
                stop_list.append(line)

        all_word_list = []
        for text in data:
            word_list = list(jieba.cut(text))
            if 'http' in word_list:
                word_list = word_list[:word_list.index('http')]
            for word in word_list:
                if word not in stop_list:
                    all_word_list.append(word)

        plt.figure()
        word_cloud = WordCloud(font_path='/System/Library/Fonts/PingFang.ttc',
                               background_color='white',
                               width=1000,
                               height=1000,
                               max_font_size=100,
                               min_font_size=10,
                               mode='RGBA')

        word_str = ' '.join(all_word_list)
        word_cloud.generate(word_str)
        word_cloud.to_file('word_cloud.png')


class ImagePlotter(Plotter):
    def __init__(self, file_path):
        self.file_path = file_path

    def create_test_image(self):
        img_list = []
        for file_name in os.listdir(self.file_path):
            if file_name.split('.')[-1] == 'jpeg':
                img_list.append(Image.open(self.file_path + '/' + file_name))

        return img_list

    def plot(self, data, *args, **kwargs):
        column = args[0]
        line = args[1]
        plt.figure("Processed Image")
        for i in range(column * line):
            plt.subplot(column, line, i + 1)
            plt.axis('off')
            plt.imshow(data[i])
        plt.savefig('image_show.jpg')


class GifPlotter(Plotter):
    def __init__(self, file_path):
        self.file_path = file_path

    def create_test_image(self):
        img_list = []
        for file_name in os.listdir(self.file_path):
            if file_name.split('.')[-1] == 'jpeg':
                img_list.append(imageio.imread(self.file_path + '/' + file_name))
                
        return img_list

    def plot(self, data, *args, **kwargs):
        imageio.mimsave('test_gif.gif', data, 'GIF', duration=0.35)


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def main():
    pp = PointPlotter(size=100)
    test_data = pp.create_test_point()
    pp.plot(test_data)

    ap = ArrayPlotter(size=100, dim=10)
    test_data = ap.create_test_array()
    ap.plot(test_data)

    tp = TextPlotter(file_path='weibo.txt')
    test_data = tp.create_test_text()
    tp.plot(test_data)

    ip = ImagePlotter(file_path='pictures')
    test_data = ip.create_test_image()
    ip.plot(test_data, 3, 3)

    gp = GifPlotter(file_path='pictures')
    test_data = gp.create_test_image()
    gp.plot(test_data, 3, 3)


if __name__ == '__main__':
    main()
