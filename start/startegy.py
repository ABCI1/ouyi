import time
from common.interface import OkexRequest
from data.data_value import data_value, currency_strategy, time_date, set_data, get_data, del_data, update_data


class OkexStrategy:

    def __init__(self, rate, buy_money, base_money, lis_order):
        self.data_values = data_value()  # 获取API的配置
        self.login_request = OkexRequest(
            host=self.data_values.get('url'),
            flag=self.data_values.get('flag'),
            symbol=self.data_values.get('symbol'),  # 币种
            access_key=self.data_values.get('api_keys'),
            secret_key=self.data_values.get('secret_keys'),
            passphrase=self.data_values.get('passphrase')

        )
        self.rate = float(rate)
        self.buy_money = buy_money
        self.base_money = base_money
        self.lis_create_order = []  # 用于存储挡位信息
        self.lis_order = lis_order  # 存储未完成的订单列表（放订单ID）
        self.add_order_dic = {}
        self.xx = []

    def create_order(self):  # 创建订单（挂单）       currency_strategy 返回单价 0  币的个数 1  卖出总币 2  索引 3
        self.lis_create_order = currency_strategy(self.rate, self.buy_money, self.base_money)
        for index in range(len(self.lis_create_order[0])):  # 循环根据挡位创建订单
            if self.base_money == self.lis_create_order[0][index]:
                response = self.login_request.buy(price=self.base_money * 1.05,
                                                  quantity=self.lis_create_order[2] * 1.0011,
                                                  order_type="LIMIT")  # buy 返回 order id

                print(f"建仓, 索引{index},单号为{response[0]}, 价格 {self.base_money}"
                      f" 数量 {self.lis_create_order[2]}")
                self.lis_order.setdefault(self.lis_create_order[3][index], 'null')
                set_data(index, 'null')

            elif self.lis_create_order[0][index] < self.base_money:  # 挡位的价格小于等于BASE价格
                response = self.login_request.buy(price=self.lis_create_order[0][index],
                                                  quantity=self.lis_create_order[1][index],
                                                  order_type="LIMIT")
                self.lis_order.setdefault(self.lis_create_order[3][index], response[0])
                # 将生成的订单号存放在列表中，转化成字典（索引：单号）
                print(f" 买入,索引{index}, 单号为{response[0]}, 价格 {self.lis_create_order[0][index]}"
                      f" 数量 {self.lis_create_order[1][index]}")
                set_data(index, response[0])

            elif self.lis_create_order[0][index] > self.base_money:  # 挡位大于BASE
                response = self.login_request.sell(price=self.lis_create_order[0][index],
                                                   quantity=self.lis_create_order[1][index - 1],
                                                   order_type="LIMIT")
                self.lis_order.setdefault(self.lis_create_order[3][index], response[0])
                print(f" 卖出, 索引{index},单号为{response[0]}, 价格 {self.lis_create_order[0][index]}"
                      f" 数量 {self.lis_create_order[1][index - 1]}")
                set_data(index, response[0])

        print(f" 单号 {self.lis_order}")

    def infinite_order_trade(self, key):  # 无限网格
        print('无限网格')
        temp = get_data()
        if key > max(self.lis_order) - 30:  # 更改挡位信息
            y = int(temp[6]) + 1
            update_data('symbol', 'abc_id', str(y))
            self.lis_create_order = currency_strategy(self.rate, self.buy_money, self.base_money, 1)
            print(self.lis_order)
            print(self.lis_create_order)

            keys = self.lis_create_order[3]
            values1 = self.lis_create_order[0]
            values2 = self.lis_create_order[1]

            price_dic = dict(zip(keys, values1))
            quantity_dic = dict(zip(keys, values2))
            print(price_dic)
            print(quantity_dic)

            x_max = max(self.lis_order)  # 60   61
            x_min = min(self.lis_order)  # 0   1
            order = self.lis_order.get(x_min)
            self.login_request.revoke_order(order)  # 系统取消最上一个订单
            while True:
                money = self.login_request.get_trade()
                if money[0]['data'][0]['side'] == 'buy':
                    break
            print(money)
            response_buy = self.login_request.buy(price=money[0]['data'][0]['px'],
                                                  quantity=quantity_dic[x_max],
                                                  order_type="LIMIT")  # 购买币
            print(f" 挡位{key}买入,价格 {price_dic[key]}"
                  f" 数量 {quantity_dic[x_max]}")
            print(f"response_buy: {response_buy}")

            order_response = self.login_request.get_order_status(response_buy[0])
            response = self.login_request.sell(price=price_dic[x_max + 1],
                                               quantity=quantity_dic[x_max] + float(order_response[0]['data'][0]['fee']),
                                               order_type="LIMIT")  # 卖出（最后增加一个订单）
            print(f" 挡位{x_max + 1}挂卖出, 单号为{response[0]}, 价格 {price_dic[x_max + 1]}"
                  f" 数量 {quantity_dic[x_max]}")
            print(response)

            self.lis_order.pop(x_min)
            self.lis_order.setdefault(x_max + 1, response[0])  # 字典中增加订单
            print(self.lis_order)

            del_data(str(x_min))  # ini中删除最上一个      1
            set_data(x_max + 1, response[0])  # ini中增加订单   62

            update_top = int(temp[4]) - 1
            update_end = int(temp[5]) + 1
            update_data('symbol', 'top', str(update_top))  # ini中更改top和end
            update_data('symbol', 'end', str(update_end))

    def order_trade(self):  # 订单交易：查询订单状态，如果为完全成交，生成新的订单
        self.lis_create_order = currency_strategy(self.rate, self.buy_money, self.base_money)
        keys = self.lis_create_order[3]
        values1 = self.lis_create_order[0]
        values2 = self.lis_create_order[1]
        price_dic = dict(zip(keys, values1))
        quantity_dic = dict(zip(keys, values2))
        print(price_dic)
        print(quantity_dic)
        # price = price_dic[key]
        # quantity = quantity_dic[key]

        temp = [key for key in self.lis_order]
        print(temp)
        for key in temp:
            try:
                values = self.lis_order[key]
                print(values)
                if values != 'null':
                    order_response = self.login_request.get_order_status(values)
                    print(
                        f"挡位：{key} -----{order_response[0]['data'][0]['state']}--"
                        f"{order_response[0]['data'][0]['side']}---{self.lis_order[key]} ")
                    time.sleep(1)

                    if order_response[0]['data'][0]['state'] == 'filled':
                        # 防止跌得太快，跳级买，造成卖的下一个（还是买）不为空（卖的下一个应该为none）
                        # next_value = self.lis_order[key + 1]
                        # pre_value = self.lis_order[key - 1]
                        # 防止涨得太快，跳级卖,造成买的上一个（还是卖）不为空 （买的上一个应该为none）
                        if order_response[0]['data'][0]['side'] == 'buy' and self.lis_order[key + 1] == 'null':  # 创建订单

                            response = self.login_request.sell(
                                price=price_dic[key + 1],  # 有问题，将价格数量放入字典取值
                                quantity=quantity_dic[key] + float(order_response[0]['data'][0]['fee']),
                                order_type="LIMIT"
                            )

                            self.lis_order.update({key: 'null'})
                            self.lis_order.update({key + 1: response[0]})

                            with open(file=r"./log/Transaction_information.log", mode='a', encoding='utf8') as file:
                                str_log = (
                                    f"挡位：{key} buy成功  索引：{key + 1} 挂卖出, 单号为{response[0]},"
                                    f"价格 {price_dic[key + 1]}"
                                    f" 数量 {quantity_dic[key]}"
                                    f" fee {order_response[0]['data'][0]['fee']}\n\n")
                                file.write(str_log)
                            print(str_log)

                            set_data(key, 'null')
                            set_data(key + 1, response[0])

                        elif order_response[0]['data'][0]['side'] == 'sell' and self.lis_order[key - 1] == 'null':

                            response = self.login_request.buy(
                                price=price_dic[key - 1],
                                quantity=quantity_dic[key - 1],
                                order_type="LIMIT"
                            )

                            self.lis_order.update({key: 'null'})
                            self.lis_order.update({key - 1: response[0]})

                            with open(file=r"./log/Transaction_information.log", mode='a', encoding='utf8') as file:
                                str_log = (
                                    f"挡位：{key} sell成功  索引：{key - 1} 挂买入, 单号为{response[0]},"
                                    f"价格 {price_dic[key - 1]}"
                                    f" 数量 {quantity_dic[key - 1]}\n\n")
                                file.write(str_log)
                            print(str_log)

                            set_data(key, 'null')
                            set_data(key - 1, response[0])

                            self.infinite_order_trade(key)

            except BaseException as Argument:
                with open(file=r"./log/error.log", mode='a', encoding='utf8') as file:
                    str_log = f"{time_date()}\n出现异常：{Argument}\n\n"
                    file.write(str_log)
                print(f"出现异常！！{Argument}\n尝试跳过该异常")
                continue

    def get_earnings(self):
        """
        :return earnings: 收益
        :return transfer_earnings: 划转到资金账户的金额
        """
        if self.data_values.get('flag') == '1':
            print("API为模拟交易模式，无法使用资金划转功能！")
            return None, None
        transfer_earnings = None
        asset_response = self.login_request.get_asset("USDT")  # 获取账户资产信息
        try:
            print(f"账户资金为：{asset_response[0]['data'][0]['details'][0]['cashBal']}")
            earnings = float(asset_response[0]['data'][0]['details'][0]['cashBal'])
        except IndexError:
            earnings = 0

        if earnings > 0:
            max_response = self.login_request.get_max_money("USDT")  # 获取最大可转出金额

            # 从交易账户划转到资金账户
            transfer_response = self.login_request.transfer(
                max_response[0]['data'][0]['ccy'], max_response[0]['data'][0]['maxWd'], "18", "6")

            # 获取资金划转状态
            status_response = self.login_request.get_transfer_status(
                transfer_response[0]['data'][0]['transId'])
            transfer_earnings = status_response[0]['data'][0]['state']

            print(f"资金划转订单号：{transfer_response[0]['data'][0]['transId']}，"
                  f"划转状态：{status_response[0]['data'][0]['state']}")
        return earnings, transfer_earnings
