import requests
import time
import random
from lxml import etree
from queue import Queue
from threading import Thread


def get_ip():
    while True:
        if not q.empty():
            # 验证IP是否可用网址
            url = 'http://httpbin.org/get'
            proxies = q.get()
            try:
                html = requests.get(url, headers=headers, proxies=proxies, timeout=3).text
                print('ip可以用')
                with open('ip.txt', 'a')as f:
                    f.write(str(proxies))
                    f.write('\n')
            except:
                print('ip不可用  下一个')
        else:
            break


def main():
    t_list = []
    for i in range(5):
        t = Thread(target=get_ip)
        t_list.append(t)
        t.start()

    for t in t_list:
        t.join()


ip_list = []
q = Queue()
# 爬取的是800到1000页   靠后的代理可能用的人少点，。自我安慰。。
for i in range(5, 1000):
    url = 'https://www.kuaidaili.com/free/inha/{}'.format(i)
    print(url)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
    }
    # proxies = {'http': 'http://211.159.219.225:8118', 'https': 'https://211.159.219.225:8118'}
    # html = requests.get(url, headers=headers,proxies=proxies).text
    html = requests.get(url, headers=headers).text
    # print(html)
    parse_html = etree.HTML(html)
    tr_list = parse_html.xpath('//*[@id="list"]/table/tbody/tr')
    # 延迟访问6到11秒。
    sleep = random.randint(1, 3)
    print(f'等待{sleep}秒')
    time.sleep(sleep)
    print('开始')
    for tr in tr_list[1:]:
        ip = tr.xpath('./td[1]/text()')[0]
        port = tr.xpath('./td[2]/text()')[0]
        proxies = {
            'http': f'http://{ip}:{port}',
            'https': f'https://{ip}:{port}',
        }
        print(proxies)
        # 存入队列
        q.put(proxies)
    main()

print(ip_list)
