import configparser
import os
import time

conf = configparser.ConfigParser()  # 类的实例化
cul_path = os.path.dirname(os.path.realpath(__file__))
path = os.path.join(cul_path, 'data.ini')
conf.read(path, encoding="utf-8")
if not os.path.exists(path):
    # 如果配置文件不存在，则创建一个新的配置文件
    with open(path, 'w', encoding="utf-8") as config_file:
        config_file.write('')

conf.read(path, encoding="utf-8")  # 读取配置文件

if 'symbol-orderid' not in conf:
    # 如果节不存在，则添加节
    conf.add_section('symbol-orderid')

with open(path, 'w', encoding="utf-8") as config_file:
    conf.write(config_file)  # 保存数据


def data_value():
    data_values = {
        'flag': '1',
        'symbol': conf['login']['symbol'],
        'url': "https://www.ouyicn.blue/",
        'api_keys': conf['login']['api_keys'],
        'secret_keys': conf['login']['secret_keys'],
        'passphrase': conf['login']['passphrase'],
    }
    return data_values


def time_date():
    now = int(time.time())  # 获得当前时间时间戳
    time_array = time.localtime(now)  # 转换为其他日期格式,如:"%Y-%m-%d %H:%M:%S"
    other_style_time = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
    return other_style_time


def currency_strategy(rate, buy_money, base_money, abc=0):
    """
    :param abc:
    :param rate:
    :param buy_money: 购买金额
    :param base_money: 0挡位的价格
    :param current_money: 当前价格
    :return: 返回列表 [购买价格、购买个数、0挡位之后的价格总计]
    """
    top = int(conf['symbol']['top'])
    end = int(conf['symbol']['end'])
    abc_id = int(conf['symbol']['abc_id'])

    lis_A, lis_C, lis_E = [], [], []
    coin_sum = 0
    E = 0

    for i in range(abc_id, top + end + abc_id):
        lis_A.append(i)
    for level in range(-top + abc, end + abc):
        A = level
        B = (rate ** A) * 100
        C = (rate ** A) * base_money
        D = buy_money
        E = D / C
        F = E * C if A <= 0 else E * base_money
        if A >= 0:
            coin_sum = E + coin_sum  # 计算当挡位大于0时，后面挡位的币的数量总和

        lis_C.append(C)
        lis_E.append(E)

    coin_sum = coin_sum - E
    lis = [lis_C, lis_E, coin_sum, lis_A]  # 购买价格、购买个数、0挡位之后币的数量总和
    return lis


def get_data():
    rate = conf['symbol']['rate']
    buy_money = conf['symbol']['buy_money']
    base = conf['symbol']['base']
    top = int(conf['symbol']['top'])
    end = int(conf['symbol']['end'])
    abc_id = int(conf['symbol']['abc_id'])
    lis_order = {}

    try:
        for i in range(0, top + end):
            x = i + abc_id
            lis_order.setdefault(i, conf['symbol-orderid'][f'{x}'])
    except Exception as e:
        pass
    return float(rate), float(buy_money), float(base), lis_order, top, end, abc_id


def set_data(key, order):
    conf['symbol-orderid'][str(key)] = str(order)

    # 往配置文件写入数据
    with open(path, 'w', encoding="utf-8") as file:
        conf.write(file)  # 保存数据


def del_data(key):
    conf.remove_option("symbol-orderid", key)
    # 往配置文件写入数据
    with open(path, 'w', encoding="utf-8") as file:
        conf.write(file)  # 保存数据


def update_data(session, key, values):
    conf.set(session, key, values)
    # 往配置文件写入数据
    with open(path, 'w', encoding="utf-8") as file:
        conf.write(file)  # 保存数据
