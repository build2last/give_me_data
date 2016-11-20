# coding:utf-8
"""
    抓取知乎问题链接下所有回答中的图片
    通过API 
    https://www.zhihu.com/node/QuestionAnswerListV2
"""
from urlparse import urlsplit
from os.path import basename
import urllib2
import re
import requests
import os
import json

python_version = 2.7


def search_url(url=""):
    if url=="":
        url = raw_input("问题链接:")
    if not os.path.exists('images'):
        os.mkdir("images")
    # split the url to get the question_id  https://www.zhihu.com/question/51500078#answer-45990060
    question_id = url.split("/")[-1].split("#")[0]
        
    page_size = 50
    offset = 0
    url_content = urllib2.urlopen(url).read()
    answers = re.findall('h3 data-num="(.*?)"', url_content)
    limits = int(answers[0])
    img_urls = []
    while offset < limits:
        post_url = "https://www.zhihu.com/node/QuestionAnswerListV2"
        params = json.dumps({
            'url_token': question_id,
            'pagesize': page_size,
            'offset': offset
        })
        data = {
            '_xsrf': '',
            'method': 'next',
            'params': params
        }
        header = {
            'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
            'Host': "www.zhihu.com",
            'Referer': url
        }
        response = requests.post(post_url, data=data, headers=header)
        answer_list = response.json()["msg"]
        img_urls.extend(re.findall('data-actualsrc="(.*?_b.*?)">', ''.join(answer_list)))
        offset += page_size
    return img_urls
    
def url_list(question_url):
    return search_url(question_url)

if __name__ == "__main__":
    img_urls = search_url()
    for img_url in img_urls:
        try:
            img_data = urllib2.urlopen(img_url).read()
            file_name = basename(urlsplit(img_url)[2])
            output = open('images/' + file_name, 'wb')
            output.write(img_data)
            output.close()
        except:
            pass