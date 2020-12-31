from socket import *
from threading import Thread, currentThread, RLock
import time
from datetime import datetime

# HOST = '127.0.0.1'
HOST = '172.20.10.12'
PORT = 8888
RSIZE = 1024


class Manager(Thread):
    """
    管理者类，将用户名与用户的connection设为字典，存为类变量
    并且在类创建时就尝试链接server，利用try避免二次打开server
    """
    client_name_dict = {}
    try:
        server = socket(AF_INET, SOCK_STREAM)
        server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen(5)
    except OSError:
        pass

    def __init__(self):
        super().__init__()

    def run(self):
        """
        manager主线程，每一个manager线程服务一个client
        """

        print("SERVER ", self.name, " Start!")
        print("SERVER is listening on ", PORT)
        break_flag = 0
        while True:
            connection, address = self.server.accept()  # 接受连接

            while True:
                """
                先监听用户返回的用户名，持续到接收用户名为止
                """
                try:
                    raw_msg = connection.recv(RSIZE)
                    if raw_msg:
                        user_name = raw_msg.decode('utf_8')
                        self.client_name_dict[user_name] = connection  # 将用户名与connection存为字典
                        break
                except Exception as e:
                    print("CREATE USER ERROR: ", e)
                    break_flag = 1
                    break

            if break_flag == 1:
                break  # 如果创建用户失败则直接结束本线程

            print('用户【' + user_name + '】加入！地址：', address)
            connection.send(('用户:' + user_name + ' 您已连接服务器, 欢迎!\n').encode('utf-8'))
            connection.send(('目前服务器中的用户数：' + str(len(self.client_name_dict))).encode('utf-8'))
            connection.send('\n您可以发送\'USER\'命令来查看所有在线用户名,如果想退出，请发送\'QUIT\'命令。\n'.encode('utf-8'))
            connection.send('如果向私人送信，请在句子头添加@用户名，并与送信内容用空格间隔。否则默认向全体用户送信\n\n'.encode('utf-8'))

            for user_dict in self.client_name_dict.items():  # 新成员进入向所有成员发送通知
                user_dict[1].send(('---用户' + user_name + '加入聊天室---').encode('utf-8'))

            while True:
                try:
                    raw_msg = connection.recv(RSIZE).decode('utf-8')
                    send_msg = ' ' + user_name + ': ' + raw_msg
                    send_msg = datetime.now().strftime('%Y-%m-%d %H:%M:%S') + send_msg  # 将接收到的信息加上用户名与时间后分发
                    if len(send_msg) > 0:
                        print(send_msg)  # 如果收到的信息非空，则存入聊天记录并且在管理员窗口输出
                        with open('manager.txt', 'a+') as f:
                            f.write(send_msg + '\n')

                    if not raw_msg:  # 如果没有收到信息则继续接收
                        break

                    if raw_msg == 'QUIT':  # 如果收到退出命令则删除字典中的用户并向所有用户发送用户退出消息
                        self.client_name_dict.pop(user_name)
                        connection.send("再见!".encode('utf-8'))
                        for user_dict in self.client_name_dict.items():
                            user_dict[1].send(('---用户' + user_name + '离开了聊天室---').encode('utf-8'))

                    elif raw_msg == 'USER':  # 如果收到查询当前用户命令则以字符串形式发送用户字典的键
                        connection.send('所有用户名如下，以空格间隔：'.encode('utf-8'))
                        connection.send(' '.join(list(self.client_name_dict.keys())).encode('utf-8'))
                    elif raw_msg[0] == '@':  # 如果收到私发消息则在用户字典中寻找用户私发，否则报错
                        send_user = raw_msg.split()[0][1:]  # @用户名 切片后删除@查找用户名
                        if send_user in self.client_name_dict.keys():
                            self.client_name_dict[send_user].send(send_msg.encode('utf-8'))
                        else:
                            connection.send('@的用户不存在或输入格式错误！请检查输入！'.encode('utf-8'))
                    else:  # 如果收到的是普通消息则向其他所有人转发
                        for user_dict in self.client_name_dict.items():
                            if user_dict[0] != user_name:
                                user_dict[1].send(send_msg.encode('utf-8'))

                except Exception as e:  # 如果出现错误则在管理窗口报错
                    print("MESSAGE SEND ERROR: ", e)
                    break
            connection.close()
        print('Manager server ' + self.name + 'close!')  # 服务器以外退出时也将用户从字典中删除
        self.server.close()
        self.client_name_dict.pop(user_name)


class Chatter(Thread):
    """
    客户端类，为了实现收发信同时进行，采用Chatter作为基类，并且创建两个专门用于收信与发信的子类
    首先在客户端类中创建连接
    """
    client = socket(AF_INET, SOCK_STREAM)
    client.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    client.connect((HOST, PORT))

    def __init__(self, server_ip, server_port, user_name):
        super().__init__()
        self.server_ip = server_ip
        self.server_port = server_port
        self.user_name = user_name

    def run(self):
        pass


class ChatterSend(Chatter):
    """
    发信子类，继承自客户端类，并且在初始化时向服务器发送用户名信息，确保服务器第一条接收的信息就是用户名
    """

    def __init__(self, server_ip, server_port, user_name):
        super(ChatterSend, self).__init__(server_port=server_port, server_ip=server_ip, user_name=user_name)
        self.client.send(self.user_name.encode('utf-8'))

    def run(self):
        """
        发信器主线程
        """
        while True:
            try:
                time.sleep(0.1)  # 控制每秒最大发信量，防止连续发信爆破程序
                inp = input()
                self.client.send(inp.encode('utf-8'))
                with open(self.user_name + '.txt', 'a+') as f:
                    f.write(inp + '\n')  # 将发出的信息保存如个人的聊天记录
                if inp == 'QUIT':  # 如果输入为退出聊天，则休眠一秒等待与manager通行完成后退出进程
                    print('已断开发送线程')
                    time.sleep(1)
                    break
            except Exception as e:
                print('ERROR:', e)
        self.client.close()


class ChatterReceive(Chatter):
    """
    接收器子类，与发信器实现相同，区别在主要在run函数
    """

    def __init__(self, server_ip, server_port, user_name):
        super(ChatterReceive, self).__init__(server_port=server_port, server_ip=server_ip, user_name=user_name)

    def run(self):
        """
        接收器主线程
        """
        with open(self.user_name + '.txt', 'a+') as f:  # 在进入新接收器时创建新的聊天记录行
            f.write('\n\n-----新聊天记录 ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '-----\n')
        while True:
            try:
                msg = self.client.recv(RSIZE)
                if not msg:
                    time.sleep(0.1)  # 每0.1秒获取一条信息
                    break
                if msg.decode('utf-8') == '再见!':
                    print('已断开接收线程')
                    time.sleep(0.5)
                    break
                else:
                    with open(self.user_name + '.txt', 'a+') as f:
                        f.write(msg.decode('utf-8') + '\n')  # 将收到的信息存入txt文件
                    print(msg.decode('utf-8'))
                time.sleep(0.1)
            except Exception as e:
                print('ERROR:', e)

        self.client.close()


def main():
    start = input('输入启动类型:man/cli:')  # 根据输入的不同创建管理窗口或者聊天窗口
    if start == 'man':
        m_ls = []
        for i in range(5):
            m = Manager()
            m_ls.append(m)
        for m in m_ls:
            m.start()
        with open('manager.txt', 'a+') as f:  # 创建管理员聊天记录
            f.write('\n\n-----新聊天记录 ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '-----\n')
        for m in m_ls:
            m.join()
    elif start == 'cli':
        print('START CLIENT')
        name = input('请输入用户名:')  # 在最开始就获取用户名
        cl_receive = ChatterReceive(server_ip=HOST, server_port=PORT, user_name=name)
        cl_send = ChatterSend(server_ip=HOST, server_port=PORT, user_name=name)
        cl_send.start()
        time.sleep(0.5)
        cl_receive.start()
        cl_receive.join()
        cl_receive.join()


if __name__ == '__main__':
    main()

# python Homework_12.py
