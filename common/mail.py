import smtplib
from email.mime.text import MIMEText
from email.header import Header

from data.data_value import time_date


def send_email(earnings, transfer_earnings):
    # 邮件服务器的配置信息
    smtp_server = 'smtp.163.com'  # 网易邮箱的SMTP服务器地址
    smtp_port = 465  # 网易邮箱的SMTP服务器端口号
    smtp_username = 'fushangzxc@163.com'  # 发件人邮箱
    smtp_password = 'TOBFQXYXYPGKGFQP'  # 发件人邮箱授权码

    # 邮件内容的配置信息
    sender = 'fushangzxc@163.com'  # 发件人邮箱
    receiver = 'fushangzxc@163.com'  # 收件人邮箱
    subject = '收益提醒'  # 邮件主题
    if earnings or transfer_earnings is None:  # 判断是否有数据
        body = f'API为模拟交易模式，无法使用资金划转功能！'  # 邮件内容
    else:
        body = f'截止{time_date()}，您的收益为{earnings}，' \
               f'从交易账户转到资金账户的金额为:{earnings}美元，划转状态：{transfer_earnings}。'  # 邮件内容

    # 创建邮件内容
    message = MIMEText(body, 'plain', 'utf-8')
    message['From'] = Header(sender, 'utf-8')
    message['To'] = Header(receiver, 'utf-8')
    message['Subject'] = Header(subject, 'utf-8')

    # 发送邮件
    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(smtp_username, smtp_password)
            server.sendmail(sender, receiver, message.as_string())
        print('邮件发送成功！')
    except Exception as e:
        print('邮件发送失败:', str(e))
