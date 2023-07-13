import configparser
import os
import time


def data_value():
    data_values = {
        'flag': '1',
        'symbol': 'OKB-USDT',
        'url': "https://www.ouyicn.blue/",
        'proxies': None,
        'api_keys': 'd231677e-8631-4f55-a213-dc64a62eeed5',
        'secret_keys': 'B97D9A2F6A2AC59B77A688D99BE28BDF',
        'passphrase': "19980620MJQmjq,./",
    }
    return data_values


def time_date():
    now = int(time.time())  # 获得当前时间时间戳
    time_array = time.localtime(now)  # 转换为其他日期格式,如:"%Y-%m-%d %H:%M:%S"
    other_style_time = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
    return other_style_time


def currency_strategy(rate, buy_money, base_money, current_money=None):
    """
    :param rate:
    :param buy_money: 购买总金额
    :param base_money: 0挡位的价格
    :param current_money: 当前价格
    :return: 返回列表 [购买价格、购买个数、0挡位之后的价格总计]
    """
    conf = configparser.ConfigParser()  # 类的实例化
    cul_path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(cul_path, 'data.ini')
    conf.read(path, encoding="utf-8")
    top = int(conf['okb-usdt']['top'])
    end = int(conf['okb-usdt']['end'])

    lis_A, lis_C, lis_E = [], [], []
    coin_sum = 0
    E = 0
    D = buy_money / top + end
    for i in range(0, top + end):
        lis_A.append(i)
    for level in range(-top, end):
        A = level
        B = (rate ** A) * 100
        C = (rate ** A) * base_money
        D = D
        E = D / C
        F = E * C if A <= 0 else E * base_money
        if A >= 0:
            coin_sum = E + coin_sum  # 计算当挡位大于0时，后面挡位的币的数量总和

        lis_C.append(C)
        lis_E.append(E)
        with open(file=r"./data/档位.csv", mode='a', encoding='utf8') as file:
            str_log = f"{A}, {B}, {C}, {D}, {E}, {F}\n"
            file.write(str_log)

    coin_sum = coin_sum - E
    lis = [lis_C, lis_E, coin_sum, lis_A]  # 购买价格、购买个数、0挡位之后币的数量总和
    return lis


def get_data():
    conf = configparser.ConfigParser()  # 类的实例化

    cul_path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(cul_path, 'data.ini')
    conf.read(path, encoding="utf-8")

    rate = conf['okb-usdt']['rate']
    buy_money = conf['okb-usdt']['buy_money']
    base = conf['okb-usdt']['base']
    top = int(conf['okb-usdt']['top'])
    end = int(conf['okb-usdt']['end'])
    lis_order = {}

    try:
        for i in range(0, top + end):
            lis_order.setdefault(i, conf['okb-usdt-orderid'][f'{i}'])
    except Exception as e:
        pass
    return float(rate), float(buy_money), float(base), lis_order


def set_data(key, order):
    conf = configparser.ConfigParser()
    cul_path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(cul_path, 'data.ini')

    if not os.path.exists(path):
        # 如果配置文件不存在，则创建一个新的配置文件
        with open(path, 'w') as config_file:
            config_file.write('')

    conf.read(path, encoding="utf-8")  # 读取配置文件

    if 'okb-usdt-orderid' not in conf:
        # 如果节不存在，则添加节
        conf['okb-usdt-orderid'] = {}

    conf['okb-usdt-orderid'][str(key)] = str(order)

    # 往配置文件写入数据
    with open(path, 'w') as config_file:
        conf.write(config_file)  # 保存数据
