# coding:utf-8
import socket

if socket.gethostname() == "ISZ4DI1Z6MV6Z6K":
    import config
else:
    import product_config as config
import pymongo
import time
import re
import sys

detail_list = ["comments_78d7b3a2d07a", "comments_892952f82a64", "comments_90ff3a8ba5c6", "comments_ac4f14f88a79","comments_c2bc21fd8459",
               "comments_beb1d0742c17", "comments_d336ddb5ae77", "comments_d8f545a59f36","comments_1a01f75a26d0","comments_1f2eabc209d6"]





def detail_to_json(total_limit):
    # temp = open("detail_%s.json" % time.strftime("%Y_%m_%d"), "w")
    # temp.close()
    client = pymongo.MongoClient(config.MONGO_URL)
    mongodb = client['weibo']
    now_number = 0
    total1 = 0

    for mongo_name in detail_list:
        if now_number >= total_limit:
            break
        # url_list = []
        total2 = 0
        collection = mongodb[mongo_name]
        details = collection.find({},no_cursor_timeout=True)
        print("%s has %s" % (mongo_name, collection.count_documents({})))
        for detail in details:
            total1 += 1
            total2 += 1
            print(total2)
            # if detail["url"] in url_list:
            #     total2 += 1
            # else:
            #     url_list.append(detail["url"])
            #--------------------------------------------
            with open("detail_ori_%s.json" % time.strftime("%Y_%m_%d"), "ab+") as file:
                if detail["content"] in ["转发图片.", "转发视频.", "", "分享图片","分享微博群","链接查看评论 ​​​​"] and (len(detail["comments"]) == 0):
                    continue
                json_data = {
                    "url": detail["url"],
                    "content": detail["content"],
                    "comments": detail["comments"]
                }
                file.write(str(json_data).encode("utf8"))
                file.write(b"\n")
                collection.delete_one({"url":detail["url"]})
            with open("detail_%s.json" % time.strftime("%Y_%m_%d"), "ab+") as file:
                detail = parse_detail(detail)
                if detail["content"] in ["转发图片.", "转发视频.", "", "分享图片","分享微博群","链接查看评论 ​​​​"]:
                      detail["content"] = ""
                if detail["content"] in ["转发图片.", "转发视频.", "", "分享图片","分享微博群","链接查看评论 ​​​​"] and (len(detail["comments"]) == 0):
                    continue
                now_number += 1
                if now_number >= total_limit:
                    break
                json_data = {
                    "url": detail["url"],
                    "content": detail["content"],
                    "comments": detail["comments"]
                }
                file.write(str(json_data).encode("utf8"))
                file.write(b"\n")
        print(total2)
    print(total1)


def justTest():
    client = pymongo.MongoClient(config.MONGO_URL)
    mongodb = client['weibo']
    total1 = 0

    for mongo_name in detail_list:
        collection = mongodb[mongo_name]
        total1 +=  collection.count_documents({})
    print(total1)


def parse_detail(detail):
    block = {}
    content = detail["content"]
    comments = detail["comments"]
    content = content.replace("&quot;","")
    content = content.replace("&gt;","")
    content = re.sub('\[([\s\S]+?)\]',"", content)
    temp_content = content
    temp_content = re.sub("[\u4E00-\u9FA5]","",temp_content)
    temp_content = re.sub("[A-Za-z0-9]","",temp_content)
    symbol_list= ["？","，","…","！","。","（","）","、","—","“","”","～","－","《","》","’","「","」","•","'","；","➕","＋","【","･","｀","｡","】","＿","+","=","@","：","”",")","(","!","~","·","&",";",":","_","-",".","～","?","#","\\","/","%","*","↓",","]


    for symbol in symbol_list:
        temp_content = temp_content.replace(symbol,"")
    temp_content = temp_content.replace(" ","")
    if len(temp_content) != 0:
        block["content"] = ""
    else:
        block["content"] = content
    block["url"] = detail["url"]
    block["comments"] = []
    for comment in comments:
        comment = re.sub('\[([\s\S]+?)\]',"", comment)
        temp_comment = comment
        temp_comment = re.sub("[\u4E00-\u9FA5]","", temp_comment)
        temp_comment = re.sub("[A-Za-z0-9]", "", temp_comment)
        for symbol in symbol_list:
            temp_comment = temp_comment.replace(symbol, "")
        temp_comment = temp_comment.replace(" ","")
        if temp_comment == "":

            block["comments"].append(comment)
        else:
            print(temp_comment)
            print(comment)
    return block






def jiankong():
    temp = open("detail_%s.json" % time.strftime("%Y_%m_%d"), "w")
    temp.close()
    client = pymongo.MongoClient(config.MONGO_URL)
    mongodb = client['weibo']

    total1 = 0
    url_list = []
    for mongo_name in detail_list:

        total2 = 0
        collection = mongodb[mongo_name]
        details = collection.find()
        print("%s has %s" % (mongo_name, collection.count_documents({})))
        for detail in details:
            total1 += 1
            if detail["url"] in url_list:
                total2 += 1
            else:
                url_list.append(detail["url"])
            with open("detail_%s.json" % time.strftime("%Y_%m_%d"), "ab+") as file:
                if detail["content"] in ["转发图片.", "转发视频."] and (len(detail["comments"]) == 0):
                    continue
                json_data = {
                    "url": detail["url"],
                    "content": detail["content"],
                    "comments": detail["comments"]
                }
                file.write(str(json_data).encode("utf8"))
                file.write(b"\n")
        print(total2)
    print(total1)


if __name__ == "__main__":
    # detail_to_json()

    if str(sys.argv[1]) == "1":
        total_number = sys.argv[2]
        detail_to_json(int(total_number))
    if str(sys.argv[1]) == "2":
        justTest()
