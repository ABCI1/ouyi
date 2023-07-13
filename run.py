import time
from datetime import datetime, timedelta
from common.mail import send_email
from data.data_value import get_data
from start.startegy import OkexStrategy

if __name__ == '__main__':
    data = get_data()
    strategy = OkexStrategy(data[0], data[1], data[2], data[3])
    if len(data[3]) == 0:
        print('建档中...')
        strategy.create_order()
    current_time = datetime.now()  # 获取当前时间
    target_time = current_time.replace(hour=21, minute=0, second=0)  # 设置每天的21:00发送邮件
    end_time = current_time.replace(hour=21, minute=5, second=0)
    while True:
        strategy.order_trade()
        time.sleep(2)
        current_time = datetime.now()  # 获取当前时间
        if target_time <= current_time <= end_time:
            message = strategy.get_earnings()
            send_email(message[0], message[1])  # 发送邮件
            target_time += timedelta(days=1)
            end_time += timedelta(days=1)
