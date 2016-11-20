# coding: utf-8
"""
    网页下可能让你感兴趣的图片
"""
import re
import os
import sys
import Queue
import threading
import urllib
import urllib2
import logging
from time import ctime,sleep

python_version = 2.7
# 模拟浏览器访问参数
user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
headers = {
    'Connection': 'Keep-Alive',
    'Accept': 'text/html, application/xhtml+xml, */*',
    'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko'
}
# log settings 抓取记录日志的设置
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='pythonDown.log',
                    filemode='w')


def agent_request(url):
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    headers = {
        'Accept': 'text/html, application/xhtml+xml, */*',
        'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko'
    }
    req_timeout = 40
    req = urllib2.Request(url, None, headers)
    resp = urllib2.urlopen(req, None, req_timeout)
    html_content = resp.read()
    return html_content      
    
    
# 多线程下载器,  针对图片url以.jpg结尾
class DownLoad(threading.Thread):
    """
    :ivar que: the urls of the files
    :ivar folder_name: the folder name where to put the downloaded files
    """
    def __init__(self, pic_url_que, folder_name = u"PyDownload"):
        if not os.path.exists(u'PyDownload') and folder_name == u"PyDownload":
            os.mkdir(u'PyDownload')
        self.que = Queue.Queue()
        if isinstance(pic_url_que, list):
            for i in pic_url_que:
                self.que.put(i)
        else:
            self.que = pic_url_que
        self.folder_name = folder_name
        threading.Thread.__init__(self)
        # print("Make folder Exception:" + str(e))

    def run(self):
        print("One thread is start working!")
        while True:
            if not self.que.empty():
                try:
                    img_url = self.que.get()
                    # req = urllib2.Request(img_url, headers = headers)
                    req_timeout = 20
                    req = urllib2.Request(img_url, None, headers)
                    resp = urllib2.urlopen(req, None, req_timeout)
                    img_data = resp.read()
                    # urllib.urlopen(img_url)
                    file_name = img_url.split('/')[-1]
                    if file_name.split(".")[-1] != "jpg" and ("jpg" in file_name or "jpeg" in file_name): 
                        file_name = file_name + ".jpg"
                    if not file_name.endswith(".jpg"):
                        file_name += ".jpg"
                    with open(self.folder_name+"/"+file_name, 'wb') as pic_code:
                            pic_code.write(img_data)
                except Exception as e:
                    logging.warning("DownLoad error:" + str(e))
                    print (e)
            else:
                break

# 获取目标 url 列表                
def get_pic_url(html_content):
    pat_string = r"img.*?src=\"(.*?)\""
    img_pattern =  re.compile(pat_string, re.S)
    img_urls = re.findall(img_pattern, html_content)
    urls = [i for i in img_urls if isinstance(i, str) and i.startswith("http") and ".js" not in i]
    print(urls)
    return urls

def exe(page_url):
    html_content = agent_request(page_url)
    url_list = get_pic_url(html_content)
    d = DownLoad(url_list)
    d.run()

if __name__ == "__main__":
    if len(sys.argv) == 2:
        exe(str(sys.argv[1]))
    else:
        exe(raw_input())
    
