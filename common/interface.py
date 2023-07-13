# _*_ coding: UTF-8 _*_


import base64
import hmac
import json
from datetime import datetime

import requests

from urllib.parse import urljoin


class OkexRequest:
    """OKEX Spot REST API client."""

    def __init__(self, symbol, access_key, secret_key, passphrase, flag=None, host=None, proxies=None):
        """
        :param flag: 0 表示实时交易，1 表示模拟交易
        :param access_key: access_key的值\
        :param secret_key: secret_key的值
        :param passphrase: 密码
        :param proxies: 使用VPN时，传入代理地址
        """
        self.flag = flag
        self.symbol = symbol
        self._host = host or "https://www.ouyicn.blue/"
        self._access_key = access_key
        self._secret_key = secret_key
        self._passphrase = passphrase
        self.proxies = proxies

    def api_request(self, method, uri, params=None, body=None, headers=None, auth=False):
        """
        发起网络请求
        @param method:请求方法，GET / POST / DELETE / PUT
        @param uri:请求Uri参数:字典、请求查询参数
        @param body:字典，请求体
        @param headers:请求HTTP报头
        @param auth: boolean，是否添加权限验证(声明要不要登录）
        @param params:
       """
        if params:
            query = "&".join(
                ["{}={}".format(k, params[k]) for k in sorted(params.keys())]
            )
            uri += "?" + query
        url = urljoin(self._host, uri)

        if auth:

            timestamp = (str(datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S."))
                         + str(datetime.utcnow()).split('.')[1][:-3] + 'Z')  # 获取世界标准时间并转换
            if body:
                body = json.dumps(body)
            else:
                body = ""
            message = str(timestamp) + str.upper(method) + uri + str(body)
            mac = hmac.new(
                bytes(self._secret_key, encoding="utf8"),
                bytes(message, encoding="utf-8"),
                digestmod="sha256",
            )
            d = mac.digest()
            sign = base64.b64encode(d)

            if not headers:
                headers = {}
            headers["Content-Type"] = "application/json"
            headers["OK-ACCESS-KEY"] = self._access_key
            headers["OK-ACCESS-SIGN"] = sign
            headers["OK-ACCESS-TIMESTAMP"] = str(timestamp)
            headers["OK-ACCESS-PASSPHRASE"] = self._passphrase
            headers["x-simulated-trading"] = self.flag
        result = requests.request(
            method, url, data=body, headers=headers, proxies=self.proxies, timeout=50
        ).json()
        if result.get("code") and result.get("code") != "0":
            return None, result
        return result, None

    def get_exchange_info(self):
        """获取交易规则和交易信息。"""
        uri = "/api/v5/public/instruments"
        params = {"instType": "SPOT", "instId": self.symbol}
        success, error = self.api_request(method="GET", uri=uri, params=params)
        return success, error

    def get_order_book(self):
        """
       获取订单数据
       """
        uri = "/api/v5/market/books"
        params = {"instId": self.symbol, "sz": 5}
        success, error = self.api_request(method="GET", uri=uri, params=params)
        return success, error

    def get_trade(self):
        """
        获取贸易数据
       """
        uri = "/api/v5/market/trades"
        params = {"instId": self.symbol, "limit": 1}
        success, error = self.api_request(method="GET", uri=uri, params=params)
        return success, error

    def get_kline(self, interval):
        """
       获取 kline 数据
       :param interval: kline period.
       """
        if str(interval).endswith("h") or str(interval).endswith("d"):
            interval = str(interval).upper()
        uri = "/api/v5/market/candles"
        params = {"instId": self.symbol, "bar": interval, "limit": 200}
        success, error = self.api_request(method="GET", uri=uri, params=params)
        return success, error

    def get_asset(self, currency):
        """
       获取账号资产信息
       :param currency: "USDT"
       """
        params = {"ccy": currency}
        result, error = self.api_request(
            "GET", "/api/v5/account/balance", params=params, auth=True
        )
        return result, error

    def get_max_money(self, currency):
        """
        获取可以从交易账户划转到资金账户的最大数量
        :param currency: "USDT"
        """
        params = {"ccy": currency}
        result, error = self.api_request(
            "GET", "/api/v5/account/max-withdrawal", params=params, auth=True
        )
        return result, error

    def transfer(self, currency, amt, my_from, to):
        """
        :param currency: "USDT"
        :param amt: 划转数量
        :param my_from: 转出账户 e.g "6" 资金账户 "18" 交易账户
        :param to: 转入账户 e.g "6" 资金账户 "18" 交易账户
        """
        data = {'ccy': currency, 'amt': amt, 'from': my_from, 'to': to}
        result, error = self.api_request(
            "POST", "/api/v5/asset/transfer", body=data, auth=True
        )
        return result, error

    def get_transfer_status(self, transfer_order_id):
        """
        获取资金划转状态
        :param transfer_order_id: 资金划转订单ID
        """
        params = {'transId': transfer_order_id}
        result, error = self.api_request(
            "GET", "/api/v5/asset/transfer-state", params=params, auth=True
        )
        return result, error

    def get_order_status(self, order_no):
        """
        获取订单状态
       :param order_no: 订单ID
       """
        uri = "/api/v5/trade/order"
        params = {"instId": self.symbol, "ordId": order_no}
        success, error = self.api_request(method="GET", uri=uri, params=params, auth=True)
        return success, error

    def buy(self, price, quantity, order_type=None):
        """
       买入
       :param price:订单价格
       :param quantity:订单数量
       :param order_type:订单类型，“LIMIT”或“MARKET”限价 市价
       :return:订单id和None，否则返回None和错误信息
       """
        uri = "/api/v5/trade/order"
        data = {"instId": self.symbol, "tdMode": "cash", "side": "buy"}
        if order_type == "POST_ONLY":
            data["ordType"] = "post_only"
            data["px"] = price
            data["sz"] = quantity
        elif order_type == "MARKET":
            data["ordType"] = "market"
            data["sz"] = quantity
        else:
            data["ordType"] = "limit"
            data["px"] = price
            data["sz"] = quantity
        success, error = self.api_request(method="POST", uri=uri, body=data, auth=True)
        if error:
            return None, error
        return success["data"][0]["ordId"], error

    def sell(self, price, quantity, order_type=None):
        """
       卖出
       :param price:订单价格
       :param quantity:订单数量
       :param order_type:订单类型, "LIMIT" or "MARKET"
       :return:订单id和None，否则返回None和错误信息
       """
        uri = "/api/v5/trade/order"
        data = {"instId": self.symbol, "tdMode": "cash", "side": "sell", "sz": quantity}
        if order_type == "POST_ONLY":
            data["ordType"] = "post_only"
            data["px"] = price
            data["sz"] = quantity
        elif order_type == "MARKET":
            data["ordType"] = "market"
            data["sz"] = quantity
        else:
            data["ordType"] = "limit"
            data["px"] = price
            data["sz"] = quantity
        success, error = self.api_request(method="POST", uri=uri, body=data, auth=True)
        if error:
            return None, error
        return success["data"][0]["ordId"], error

    def revoke_order(self, order_no):
        """
        取消订单
       @param order_no: 订单ID
       """
        uri = "/api/v5/trade/cancel-order"
        data = {"instId": self.symbol, "ordId": order_no}
        _, error = self.api_request(method="POST", uri=uri, body=data, auth=True)
        if error:
            return order_no, error
        else:
            return order_no, None

    def revoke_orders(self, order_nos):
        """
       按照订单号取消订单
       @param order_nos :订单列表
       """
        success, error = [], []
        for order_id in order_nos:
            _, e = self.revoke_order(order_id)
            if e:
                error.append((order_id, e))
            else:
                success.append(order_id)
        return success, error

    def get_open_orders(self):
        """获取所有未完成订单
       * NOTE: 最多获取100条
       """
        uri = "/api/v5/trade/orders-pending"
        params = {"instType": "SPOT", "instId": self.symbol}
        success, error = self.api_request(method="GET", uri=uri, params=params, auth=True)
        if error:
            return None, error
        else:
            order_ids = []
            if success.get("data"):
                for order_info in success["data"]:
                    order_ids.append(order_info["ordId"])
            return order_ids, None
