import pandas as pd
import pickle
from matplotlib import pyplot as plt
import numpy as np


class ReadData:
    """
    数据读取类，负责读取数据，并且返回所需的数据格式
    """
    emission_data = {}
    years = [i for i in range(1997, 2016)]
    sheet_name = []
    file_name = 'Province sectoral CO2 emissions '

    def __init__(self, file_path):
        """
        初始化函数
        :param file_path: 文件路径
        """
        self.emission_data = ReadData.emission_data
        self.years = ReadData.years
        self.sheet_name = pd.ExcelFile(file_path + '/Province sectoral CO2 emissions 1997.xlsx').sheet_names
        self.file_name = ReadData.file_name

    def read_data(self, file_path, reopen=False):
        """
        读取数据，储存为字典格式。键：（时间，省份）元组，值：Dataframe表
        :param file_path: 文件路径
        :param reopen: 是否为重新打开（由于读取速度慢，故打开第一次后用pickle保存）
        :return:
        """
        if not reopen:
            file_name = '/Province sectoral CO2 emissions '
            sheet_name = pd.ExcelFile(file_path + '/Province sectoral CO2 emissions 1997.xlsx').sheet_names
            years = [i for i in range(1997, 2016)]

            for year in years:
                for name in sheet_name:
                    self.emission_data[(year, name)] = pd.read_excel(file_path + file_name + str(year) + '.xlsx',
                                                                     sheet_name=name)
            print(len(self.emission_data))
            with open('emission_data.pkl', 'wb') as f:
                pickle.dump(self.emission_data, f)
        else:
            with open('emission_data.pkl', 'rb') as f:
                self.emission_data = pickle.load(f)

    def select_time_data(self, province, industry):
        """
        选择时间序列数据，选择某省份某污染类型在时间上的序列
        :param province: 省份
        :param industry: 污染类型
        :return:
        """
        time_data_ls = []
        index_ls = self.emission_data[(1997, province)].loc[industry].index
        for year in self.years:
            time_data_ls.append(self.emission_data[(year, province)].loc[industry])

        return time_data_ls, list(index_ls)

    def select_place_data(self, time, poll_type, province):
        """
        按照空间维度进行分析，返回需要的数据
        :param time: 分析的年份
        :param poll_type: 需要分析的变量，为列变量
        :param province: 是否为省份数据，为布尔型。如果为True则分析所有省。否则分析Sum
        :return: 返回一个所有省所求数据的列表，与所有省份的索引（如果是sum则只返回一个sum）
        """
        place_data_ls = []
        if province:
            index_ls = self.sheet_name[1:]
        else:
            index_ls = [self.sheet_name[0]]
        for name in index_ls:
            place_data_ls.append(self.emission_data[(time, name)][poll_type])

        return place_data_ls, index_ls

    def if_nan(self, year, province):
        """
        判断数据是否存在空置，并且删除存在空值的行并报错
        :param year: 年份
        :param province: 省份
        :return:
        """
        test_nan = self.emission_data[(year, province)]
        if test_nan.isnull().sum().sum() > 0:
            nan_place = np.where(np.array(test_nan.isnull()))
            nan_lines = test_nan.index[nan_place[0]]
            nan_columns = test_nan.columns[nan_place[1]]
            for i in range(len(nan_lines)):
                raise NotNumError(year=year, province=province, industry=nan_lines[i], poll_type=nan_columns[i])
            self.emission_data[(year, province)].dropna(axis=0, inplace=True)

    def if_divzero(self, year, province):
        """
        查找是否存在和为0的情况，进行报错
        :param year: 年份
        :param province: 省份
        :return:
        """
        test_zero = self.emission_data[(year, province)]
        for index, line in test_zero.iterrows():
            if type(list(line)[0]) == int and sum(line) == 0:
                raise ZeroDivError(year=year, province=province, industry=index)

    def test_data(self, year, province, error_type):
        """
        对数据进行测试（测试和为0与存在空值）
        :param year: 年份
        :param province: 省份
        :param error_type: 错误的类型（'nan','div'）
        :return:
        """
        if error_type == 'nan':
            try:
                self.if_nan(year, province)
            except NotNumError as nan_error:
                print(nan_error.message)
        elif error_type == 'div':
            try:
                self.if_divzero(year, province)
            except ZeroDivError as zero_error:
                print(zero_error.message)


class PlaceAnalysis:
    """
    分析空间序列数据
    """
    def __init__(self, data_ls, group_type):
        self.data_ls = data_ls
        self.group_type = group_type

    def data_analysis(self, index, time, file_name):
        """
        数据分析并且绘图
        :param file_name: 文件名
        :param index: 绘图索引
        :param time: 绘图时间刻度
        :return:
        """
        para_ls = []
        for data in self.data_ls:
            # print(dataa)
            # print(dataa[self.group_type])
            para_ls.append(data[self.group_type])

        plt.figure(figsize=(30, 9))
        plt.xticks(rotation=45)
        plt.bar(x=index, height=para_ls)
        plt.title(time + self.group_type)
        plt.savefig(file_name)


class TimeAnalysis:
    """
    分析时间序列数据
    """
    def __init__(self, data_ls, group_type):
        self.data_ls = data_ls
        self.group_type = group_type

    def data_analysis(self, index, province, file_name):
        """
        绘图并分析
        :param file_name: 文件名
        :param index: 绘图索引
        :param province: 绘图省份
        :return:
        """
        para_ls = []
        for data in self.data_ls:
            para_ls.append(data[self.group_type])

        plt.figure(figsize=(30, 9))
        # plt.xticks(rotation=45)
        plt.bar(x=index, height=para_ls)
        plt.title(province + ' ' + self.group_type)
        plt.savefig(file_name)


class NotNumError(ValueError):
    """
    year，province，industry，type
    存在空值的错误类
    """

    def __init__(self, year, province, industry, poll_type):
        self.year = year
        self.province = province
        self.industry = industry
        self.poll_type = poll_type
        self.message = 'NotNumError at Year:{}, Province:{}, Industry:{}, Type:{}'.format(self.year, self.province,
                                                                                          self.industry, self.poll_type)


class ZeroDivError(ValueError):
    """
    存在和为0的错误类
    """
    def __init__(self, year, province, industry):
        self.year = year
        self.province = province
        self.industry = industry
        self.message = 'ZeroDivisionError at Year:{}, Province:{}, Industry:{}'.format(self.year, self.province,
                                                                                       self.industry)


def main():
    data = ReadData('co2_demo')
    data.read_data('co2_demo', reopen=True)
    raw_coal_1997, index_ls = data.select_place_data(time=1997, poll_type='Raw Coal', province=True)

    data.test_data(1997, 'Beijing', 'nan')
    data.test_data(1997, 'Beijing', 'div')
    place_1997 = PlaceAnalysis(data_ls=raw_coal_1997, group_type='Total Consumption')
    place_1997.data_analysis(index=index_ls, time='1997 ', file_name='place_1997.jpg')

    beijing_total, index_ls = data.select_time_data(province='Beijing', industry='Total Consumption')
    beijing_time = TimeAnalysis(data_ls=beijing_total, group_type='Raw Coal')
    years = [str(i) for i in range(1997, 2016)]
    beijing_time.data_analysis(index=years, province='Beijing', file_name='beijing_time.jpg')


if __name__ == '__main__':
    main()
