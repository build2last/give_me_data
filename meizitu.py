"""
author: 萤火 YingHuo
python  2.7
date:   2016
多种方式爬取妹子图网站图片(http://www.meizitu.com/)
主要是用来练手多线程的
多线程爬取网页，子线程中用多线程下载图片，确实蛮快的
=========
过程描述：
遍历主页地址 page_list ，从每个主页获取多个相册链接，访问相册，获取每个相册中的图片链接，制作图片链接队列，
用多线程对图片队列进行下载
多种抓取方法
"""
import os
import Queue
import threading
import urllib
import urllib2
import logging
from time import ctime,sleep
from bs4 import BeautifulSoup

page_list = []
page_html = []
folder_count = 0


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


# 多线程下载器
class DownLoad(threading.Thread):
    """
    :ivar que: the urls of the files
    :ivar folder_name: the folder name where to put the downloaded files
    """
    def __init__(self, que, folder_name = "PyDownload"):
        self.que = que
        self.folder_name = folder_name
        threading.Thread.__init__(self)
        self.que = que
        # print("Make folder Exception:" + str(e))

    def run(self):
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
                    with open(u'images/'+self.folder_name+"/"+self.folder_name+file_name, 'wb') as pic_code:
                            pic_code.write(img_data)
                except Exception as e:
                    logging.warning(str(e))
                    print (e)
            else:
                break


# 任务调度执行，管理下载器
class PicDownloader:
    global folder_count
    folder_count += 1

    def __init__(self, pic_set_name, pic_url_list):
        self.set_name = pic_set_name
        self.pic_list = pic_url_list
        self.folder_name = pic_set_name
        try:
            if not os.path.exists(u'images/'+self.folder_name):
                os.mkdir(u'images/'+self.folder_name)
        except Exception as e:
            logging.exception(str(e))

    def start_download(self):
        try:
            que = Queue.Queue()
            # que=queue.Queue()#py 3
            for img in self.pic_list:
                que.put(img)
            for i in range(5):
                d = DownLoad(que, self.set_name)
                d.start()
        except Exception as e:
            print ("pic_downloader exception:" + str(e))


# 主页html分析，获取相册集的链接
def home_page_seek(url):
    p_request = urllib.urlopen(url)
    p_html = p_request.read()
    soup = BeautifulSoup(p_html, "lxml")
    set_list = []
    # 获取相册集页面信息
    try:
        for i in soup(class_="wp-item"):
            # print len(i(class_="tit"))
            set_url = i(class_="tit")[0].a.get('href')
            set_name = i(class_="tit")[0].a.string
            # set_list.append((set_name,set_url))
            set_page_seek(set_name,set_url)
            print set_name + " " + set_url
    except Exception as e:
        print(e)
        # print soup(class_="wp-item")


# 相册页面html分析，获取图片url
def set_page_seek(set_name, url):
    p_request = urllib.urlopen(url)
    p_html = p_request.read()
    soup = BeautifulSoup(p_html, "lxml")
    url_list = []
    # 获取目标url
    for i in soup.select("#picture > p > img"):
        # print(soup.select("#picture > p > img"))
        url_list.append(i.get('src'))
    pd = PicDownloader(set_name, url_list)
    pd.start_download()


def url_request(url):
    req_timeout = 20
    req = urllib2.Request(url, None, headers)
    resp = urllib2.urlopen(req, None, req_timeout)
    return resp.read()
    # urllib.urlopen(img_url)


# 多线程方式访问多个主页
def muti_thread():
    threads = []
    for page_url in page_list:
        t = threading.Thread(target=home_page_seek, args=(page_url,))
        threads.append(t)
    for t in threads:
        t.start()


# 单线程下载，每次访问一个主页
def single_thread():
    for page in page_list:
        home_page_seek(page)


# postContent
def daily_report_seek(url):
    # 获取相册集页面信息 get img url
    try:
        p_html = url_request(url)
        soup = BeautifulSoup(p_html, "lxml")
        content = soup(class_="postContent")[0]
        title = "daily " + url.split("/")[-1].replace(".html", "")
        # content.select("p > img")[0].get("title")
        img_list = []
        for i in content.select("p > img"):
            img_list.append(i.get("src"))
        pd = PicDownloader(title, img_list)
        pd.start_download()
    except Exception as e:
        print(e)
        # print soup(class_="wp-item")


# 一种爬取方式，抓取历史上每日精选
def browse_by_day():
    threads = []
    # 人工观察发现链接变化规律
    for i in range(5000,5010):
        page_url = "http://www.meizitu.com/a/%d.html" % i
        threads.append(threading.Thread(target=daily_report_seek, args=(page_url,)))
    while True:
        if threading.active_count() < 6:
            t = threads.pop()
            t.start()
            if len(threads) < 1:
                break
        else:
            print "Threads number " + str(threading.active_count())
            sleep(1)
if __name__ == "__main__":
    # page_number = int(raw_input("How many pages do you want? "))
    # for i in range(page_number,page_number+10):
    #    page_list.append("http://www.meizitu.com/a/list_1_%d.html"%i)
    if not os.path.exists('images'):
        os.mkdir("images")
    # muti_thread()
    # single_thread()
    # while threading.active_count() >1:#主程序本身也是一个线程
    #    print "Current thread number: "+str(threading.active_count())
    #    sleep(5)
    # daily_report_seek("http://www.meizitu.com/a/150.html")
    browse_by_day()

