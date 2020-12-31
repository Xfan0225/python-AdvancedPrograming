import os
import time
import random
from faker import Faker
from pypinyin import lazy_pinyin
import pandas as pd


fake = Faker('en_US')  # 创建英文虚拟联系人
#fake = Faker('zh_CN')  # 创建中文虚拟联系人


class Contacts:
    """
    init: id, name, phone, email, profile 其中id设置为类变量
    """
    id = 0
    add_time = 0
    renew_time = 0

    def __init__(self, name, phone, email, profile):
        """
        初始化类函数
        :param name: 姓名
        :param phone: 手机号
        :param email: 电子邮箱
        :param profile: 自拍照（profile类文件）
        """
        Contacts.id += 1
        self.id = Contacts.id
        self.name = name
        self.phone = phone
        self.email = email
        self.profile = profile
        self.renew_time = Contacts.renew_time
        self.add_time = time.ctime()

    def renew_name(self, new):
        """
        更新名称，下同，仅为属性不同
        :param new:新名称
        :return:
        """
        Contacts.renew_time = time.ctime()
        self.name = new

    def renew_phone(self, new):
        Contacts.renew_time = time.ctime()
        self.phone = new

    def renew_email(self, new):
        Contacts.renew_time = time.ctime()
        self.email = new

    def renew_profile(self, new):
        Contacts.renew_time = time.ctime()
        self.profile = new

    def get_id(self):
        """
        获取该类中的id，下同，仅属性不同
        :return:
        """
        print("ID: " + str(self.id))
        return self.id

    def get_name(self):
        print("Name: " + str(self.name))
        return self.name

    def get_phone(self):
        print("Phone: " + str(self.phone))
        return self.phone

    def get_email(self):
        print("Email: " + str(self.email))
        return self.email

    def get_profile(self):
        return self.profile

    def print_contact(self):
        """
        输出联系人信息，包括基本信息与时间信息
        :return:
        """
        print("ID:{},\tName:{},\tPhone:{},\tEmail:{}".format(self.id, self.name, self.phone,
                                                             self.email))
        print("Profile Path:{},\tProfile Size:{}x{}".format(self.profile.path, self.profile.length,
                                                            self.profile.width))
        print("Create Time:{}\tLast Update Time:{}\n".format(self.add_time, self.renew_time))


class Profile:
    def __init__(self, path, length, width):
        """
        profile类，包含图像地址，
        :param path: 图像地址
        :param length: 长度
        :param width: 宽度
        """
        self.path = path
        self.length = length
        self.width = width

    def renew_path(self, new):
        """
        更新图像地址，下同
        :param new: 新地址
        :return:
        """
        self.path = new

    def renew_length(self, new):
        self.length = new

    def renew_width(self, width):
        self.width = width

    def get_path(self):
        """
        获取图像地址，下同
        :return: 返回获得的地址
        """
        print("Path:" + str(self.path))
        return self.path

    def get_length(self):
        print("Length:" + str(self.length))
        return self.length

    def get_width(self):
        print("Width:" + str(self.width))
        return self.width


class AddressBook:
    def __init__(self, contacts_num, contacts_ls):
        """
        实例化类，需要传入联系人列表与联系人数量
        :param contacts_num: 联系人数量
        :param contacts_ls: 联系人列表
        """
        self.contacts_num = contacts_num
        self.contacts_ls = contacts_ls

    def is_all_chinese(self, name):
        """
        判断是否为中文的函数，用于姓名排序
        :param name: 姓名
        :return: 返回bool类型
        """
        for _char in name:
            if not '\u4e00' <= _char <= '\u9fa5':
                return False
        return True

    def search_id(self, Id):
        """
        查找某id是否存在于通讯录中，下同
        :param Id: id
        :return: 返回查找到的联系人类，如果找不到则返回0
        """
        for contact in self.contacts_ls:
            if contact.id == Id:
                return contact
        print("ID:" + str(Id) + " Not Found!")
        return 0

    def search_name(self, name):
        for contact in self.contacts_ls:
            if contact.name == name:
                print("Find Same Name:" + str(name) + " On ID:" + str(contact.id))
                return contact.name
        return 0

    def search_phone(self, phone):
        for contact in self.contacts_ls:
            if contact.phone == phone:
                print("Find Same Phone:" + str(phone) + " On ID:" + str(contact.id))
                return contact.phone
        return 0

    def search_email(self, email):
        for contact in self.contacts_ls:
            if contact.email == email:
                print("Find Same Email:" + str(email) + " On ID:" + str(contact.id))
                return contact.email
        return 0

    def add_contacts(self, name, phone, email, profile):
        """
        添加单个联系人
        :param address_book: 所在的通讯录类
        :param name: 姓名
        :param phone: 电话
        :param email: 邮箱
        :param profile: 自拍类
        :return: 返回新增的联系人类
        """
        if self.search_email(email) and self.search_phone(phone):
            print("Add New Contacts Error!")
            return 0
        else:
            new_contacts = Contacts(name=name, phone=phone, email=email, profile=profile)
            new_contacts.add_time = time.ctime()
            print("Add Contacts Success!")
            new_contacts.get_id()
            new_contacts.get_name()
            new_contacts.get_phone()
            new_contacts.get_email()
            new_contacts.get_profile()
            self.contacts_ls.append(new_contacts)
            return new_contacts

    def renew_name(self, Id, name):
        """
        更新通讯录中某id对应的联系人的名字，下同
        :param id: 被更新的id
        :param name: 更新的姓名
        :return:
        """
        contact = self.search_id(Id=Id)
        if contact:
            contact.renew_name(name)
            contact.renew_time = time.ctime()
            print("Renew Success! ID:" + str(Id) + " New Name:" + str(name))

    def renew_phone(self, Id, phone):
        contact = self.search_id(Id)
        if contact:
            contact.renew_phone(phone)
            contact.renew_time = time.ctime()
            print("Renew Success! ID:" + str(Id) + " New Phone:" + str(phone))

    def renew_email(self, Id, email):
        contact = self.search_id(Id)
        if contact:
            contact.renew_email(email)
            contact.renew_time = time.ctime()
            print("Renew Success! ID:" + str(Id) + " New email:" + str(email))

    def renew_profile(self, Id, profile):
        contact = self.search_id(Id)
        if contact:
            contact.renew_phone(profile)
            contact.renew_time = time.ctime()
            print("Renew Success! ID:" + str(Id) + " New Profile:" + str(profile))

    def sort_name(self, reverse=False):
        """
        以姓名排序，下同
        :param reverse: 默认升序排序，True为降序
        :return:
        """
        if self.is_all_chinese(self.contacts_ls[0].name):
            sorted_contacts = sorted(self.contacts_ls, key=lambda x: ''.join(lazy_pinyin(x.name)), reverse=reverse)
        else:
            sorted_contacts = sorted(self.contacts_ls, key=lambda x: x.name, reverse=reverse)
        for contact in sorted_contacts:
            contact.print_contact()

    def sort_phone(self, reverse=False):
        sorted_contacts = sorted(self.contacts_ls, key=lambda x: x.phone, reverse=reverse)
        for contact in sorted_contacts:
            contact.print_contact()

    def sort_email(self, reverse=False):
        sorted_contacts = sorted(self.contacts_ls, key=lambda x: x.email, reverse=reverse)
        for contact in sorted_contacts:
            contact.print_contact()

    def save_address(self):
        """
        保存通讯录，利用pandas存为txt文件，间隔符为\t
        :return:
        """
        pd_id = []
        pd_name = []
        pd_phone = []
        pd_email = []
        pd_profile_path = []
        pd_profile_size = []
        pd_create_time = []
        pd_update_time = []
        for contact in self.contacts_ls:
            pd_id.append(contact.id)
            pd_name.append(contact.name)
            pd_phone.append(contact.phone)
            pd_email.append(contact.email)
            pd_profile_path.append(contact.profile.path)
            pd_profile_size.append((contact.profile.length, contact.profile.width))
            pd_create_time.append(contact.add_time)
            pd_update_time.append(contact.renew_time)

        pd_id = pd.DataFrame(dict(id=pd_id))
        pd_name = pd.DataFrame(dict(Name=pd_name))
        pd_phone = pd.DataFrame(dict(phone=pd_phone))
        pd_email = pd.DataFrame(dict(email=pd_email))
        pd_profile_path = pd.DataFrame(dict(profile_path=pd_profile_path))
        pd_profile_size = pd.DataFrame(dict(profile_size=pd_profile_size))
        pd_create_time = pd.DataFrame(dict(create_time=pd_create_time))
        pd_update_time = pd.DataFrame(dict(update_time=pd_update_time))
        pd_address = pd.concat([pd_id, pd_name, pd_phone, pd_email, pd_profile_path, pd_profile_size,
                                pd_create_time, pd_update_time], axis=1)
        pd_address.to_csv('Address_ch.txt', sep='\t', index=0)

    def read_address(self, file_path):
        """
        读取保存的联系人，并加入通讯录中
        :param file_path: 保存联系人的路径
        :return:
        """
        pd_address = pd.read_csv(file_path, sep='\t')
        for index, items in pd_address.iterrows():
            size = items.profile_size[1:-1].split(',')
            profile = Profile(path=items.profile_path, length=size[0], width=size[1])
            contact = Contacts(name=items.Name, phone=items.phone, email=items.email, profile=profile)
            self.contacts_ls.append(contact)


class Test:
    def __init__(self, create_num, add_num):
        """
        测试类，传入测试新增随机联系人的数目，增加联系人的数目
        :param create_num: 新增联系人的数目
        :param add_num: 增加联系人的数目
        """
        self.create_num = create_num
        self.add_num = add_num

    def random_create(self):
        """
        随机创建联系人，创建为联系人列表，建立通讯录类
        :return: 返回建立的通讯录类
        """
        contact_ls = []
        for i in range(self.create_num):
            name = fake.name()
            phone = fake.phone_number()
            email = fake.email()
            profile = Profile(path=fake.file_path(), length=random.randint(100, 1000), width=random.randint(100, 1000))
            contact = Contacts(name=name, phone=phone, email=email, profile=profile)
            contact_ls.append(contact)
        address_book = AddressBook(contacts_num=self.create_num, contacts_ls=contact_ls)
        return address_book

    def random_add(self, address_book):
        """
        随机增加联系人，返回增加后的类
        :param address_book: 需要增加联系人的通讯录
        :return: 返回增加完联系人后的类
        """
        for i in range(self.add_num):
            name = fake.name()
            phone = fake.phone_number()
            email = fake.email()
            profile = Profile(path=fake.file_path(), length=random.randint(100, 1000), width=random.randint(100, 1000))
            address_book.add_contacts(name=name, phone=phone, email=email, profile=profile)
        return address_book


def main():
    test = Test(create_num=5, add_num=5)
    time1 = time.time()
    address_book = test.random_create()
    time2 = time.time()
    address_book.sort_name()
    address_book.sort_email()
    address_book.sort_phone()
    time3 = time.time()
    test.random_add(address_book=address_book)
    time4 = time.time()
    address_book.sort_name()
    # address_book.sort_email()
    # address_book.sort_phone()
    time5 = time.time()
    #address_book.save_address()
    address_book.read_address('Address_ch.txt')
    time6 = time.time()
    address_book.sort_name()
    time7 = time.time()
    print("Create Time: {:.2f}s,\tSort Time: {:.2f}s,\tAdd Time: {:.2f}s,\tSort All Time: {:.2f}s\tAdd Time: {:.2f}\t"
          "Sort New Time: {:.2f}\nTotal Time: {:.2f}s "
          .format(time2 - time1, time3 - time2, time4 - time3, time5 - time4, time6 - time5, time7 - time6,
                  time7 - time1))


    '''
    contact1 = Contacts(name='Huang',phone='13388881111', email='Huang@163.com', profile=Profile(path='123.jpg',length=123,width=123))
    contact2 = Contacts(name='He',phone='13788881111', email='He@126.com', profile=Profile(path='234.jpg',length=234,width=234))
    contact3 = Contacts(name='Han',phone='13888881111', email='Han@163.com', profile=Profile(path='345.jpg',length=345,width=345))
    contact_ls = [contact1,contact2,contact3]
    test_address = AddressBook(contacts_num=3, contacts_ls=contact_ls)
    #test_address.sort_name()
    #test_address.add_contacts(test_address, name='Huangson', phone='13388881111', email='Huang@163.com', profile=Profile(path='123.jpg',length=123,width=123))
    #time.sleep(3)
    #test_address.renew_name(Id=1, name='NewHuang')

    #test_address.sort_name()
    '''

if __name__ == '__main__':
    main()
