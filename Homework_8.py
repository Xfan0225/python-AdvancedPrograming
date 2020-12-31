import random


def random_walk(mu, x0, sigma, n):
    """
    生成随机序列的生成器 X_t = mu + X_{t-1} + w_t; w_t = N(0, sigma^2)
    :param mu: 随机参数
    :param x0: 初始值
    :param sigma: 随机正态分布参数
    :param n: 生成的数字数
    :return:
    """
    count = 0
    x = x0
    while count < n:
        w_t = random.normalvariate(0, sigma) #生成正态分布随机数
        yield x
        x = mu + x + w_t
        count += 1
    return 'done'


if __name__ == '__main__':
    ls = random_walk(1, 0, 1, 10)
    ls1 = random_walk(1, 0, 4, 10)
    ls2 = random_walk(1, 0, 9, 10)
    ziped = zip(ls, ls1, ls2)
    for i in ziped:
        print(i)

