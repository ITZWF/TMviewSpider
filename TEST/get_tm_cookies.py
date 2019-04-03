import json
import time
from io import BytesIO
import redis

import requests
from PIL import Image
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

ip_cookie_key = 'ip_cookie_key'


class IPCookie(object):

    def __init__(self):
        self.connect = redis.Redis(host='127.0.0.1', port=6379, db=15)

    @staticmethod
    def ip_for_selenium():
        # 获取代理IP的网址填这里， 改吧改吧能用
        text = requests.get('').text
        json_text = json.loads(text)
        host = json_text['RESULT'][0]['ip']
        port = json_text['RESULT'][0]['port']

        return 'http://' + host + ':' + port

    def get_cookies(self):

        # ip = self.ip_for_selenium()

        # 本地开蓝灯测试
        ip = 'http://127.0.0.1:8000'

        service_args = [
            # '--proxy=%s' % ip,       # 代理 IP：prot    （eg：192.168.0.28:808）
            '--proxy-type=http',                # 代理类型：http/https
            '--load-images=no',             # 关闭图片加载（可选）
            # '--disk-cache=yes',              # 开启缓存（可选）
            # '--ignore-ssl-errors=true'      # 忽略https错误（可选）
        ]
        # 使用phantomjs， 服务器搭建比较好
        # driver = webdriver.Chrome(chrome_options=chrome_options)
        # Windows 下
        driver = webdriver.PhantomJS(executable_path='D:\\ChromeDownload\\phantomjs-2.1.1-windows\\phantomjs-2.1.1-windows\\bin\\phantomjs.exe', service_args=service_args)
        # Linux 下, 目录挂载在数据卷上
        # driver = webdriver.PhantomJS(executable_path='/home/tools/phantomjs-2.1.1-linux-x86_64/bin/phantomjs', service_args=service_args)

        url = 'https://www.tmdn.org/tmview/welcome#'

        try:
            driver.get(url)
            wait = WebDriverWait(driver, 300, 5)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '._button')))
            driver.find_elements_by_css_selector('._button')[0].click()
            time.sleep(5)
            screenshots = driver.get_screenshot_as_png()
            screenshots = Image.open(BytesIO(screenshots))
            driver.get_screenshot_as_file('DATA_TEXT.png')

            cookies = driver.get_cookies()
            cookie_jar = {}
            for cookie in cookies:
                name = cookie['name']
                value = cookie['value']
                cookie_jar[str(name)] = str(value)

            str_cookie = json.dumps(dict(cookie_jar), ensure_ascii=False)
            cookie_ip_ls = [ip, str_cookie]
            print(cookie_ip_ls)
            driver.close()

            return self.connect.lpush(ip_cookie_key, str(cookie_ip_ls))
        except Exception as e:
            print(e)
            self.get_cookies()


t = IPCookie()
t.get_cookies()
