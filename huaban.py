#coding=utf-8

"""
修改request请求的header，通过API快速抓取花瓣图片
"""
import requests as RQ
import json
# http://hbimg.b0.upaiyun.com/40fbdb4cb9c1fd3039a76cbcab187d27b04b860366b6b-yEMu2Y


def get_huaban_img_by_board_id(id):
    boards_url = "http://huaban.com/boards/%d/" %id

    hburl = boards_url + "?ipva9fpx&max=759391397&limit=100&wfl=1"
    heads = {
    'Host':"huaban.com",
    'Referer':boards_url,
    'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.84 Safari/537.36",
    'X-Request':"JSON",
    'X-Requested-With':"XMLHttpRequest"
    }
    try:
        api_content = RQ.get(hburl, headers=heads).content.decode("utf-8")
        # print api_content
        huaban_json = json.loads(api_content)
        img_list = []
        for i in huaban_json.get("board")["pins"]:
            img_list.append("http://hbimg.b0.upaiyun.com/" + i["file"].get("key", " "))
        return img_list
    except Exception as e:
        print("Error happened in huaban")
        return []
        
if __name__ == "__main__":
    for i in get_huaban_img_by_board_id(16026771):
        print(i)