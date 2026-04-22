#!/usr/bin/env python3
"""读取 /tmp/wechat-articles/ 下当天生成的 .md 文件，作为邮件附件发送"""

import smtplib
import os
import glob
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

ENV_FILE = '/root/.openclaw/wechat-writer-smtp.env'
ARTICLES_DIR = '/tmp/wechat-articles'

def load_env():
    env = {}
    with open(ENV_FILE) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k] = v
    return env

def send_email(env, subject, body, attachments):
    msg = MIMEMultipart()
    msg['From'] = env['SMTP_USER']
    msg['To'] = env['SMTP_TO']
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    for filepath in attachments:
        filename = os.path.basename(filepath)
        with open(filepath, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
        msg.attach(part)

    server = smtplib.SMTP_SSL(env['SMTP_HOST'], int(env['SMTP_PORT']))
    server.login(env['SMTP_USER'], env['SMTP_PASS'])
    server.sendmail(env['SMTP_USER'], env['SMTP_TO'], msg.as_string())
    server.quit()

def main():
    env = load_env()
    today = datetime.now().strftime('%Y-%m-%d')

    # 查找当天的 .md 文件
    pattern = os.path.join(ARTICLES_DIR, f'{today}*.md')
    files = sorted(glob.glob(pattern))

    if not files:
        print(f'no .md files found for {today}')
        return

    # 生成邮件正文摘要
    summaries = []
    for i, filepath in enumerate(files, 1):
        filename = os.path.basename(filepath)
        with open(filepath, 'r') as f:
            first_lines = f.read(200)
        summaries.append(f'{i}. {filename}\n   {first_lines.split(chr(10))[0]}')

    body = f'公众号文章 · {today}\n\n共 {len(files)} 篇，详见附件：\n\n' + '\n\n'.join(summaries)
    subject = f'公众号文章 · {today}（{len(files)} 篇）'

    send_email(env, subject, body, files)
    print(f'sent {len(files)} articles as attachments')

if __name__ == '__main__':
    main()
