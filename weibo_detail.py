# -*- coding: utf-8 -*-
import requests

import re
import tools
import pymongo
import socket
if socket.gethostname() == "ISZ4DI1Z6MV6Z6K":
    import config
else:
    import product_config as config
import socket
import time
import string
import threading
import json
List = []
sem = threading.BoundedSemaphore(50)
NUMBER = 0
sleep_time = 60


def get_mongo(collection_name):
    client = pymongo.MongoClient(config.MONGO_URL)
    mongodb = client['weibo']
    collection = mongodb[collection_name]
    return collection
mongo_links = get_mongo("weibo_links")
mongo_comments = get_mongo("comments_%s" % socket.gethostname())
class WeiboDetail(object):
    def __init__(self, number):
        self.mongo_links = mongo_links
        self.mongo_comments = mongo_comments
        self.number = number
        self.url = self.get_url()
        # print(self.url)
        self.content_block = {
            "url": self.url,
            "content": "",
            "comments": []
        }
        self.repeat_times = 0
        self.num_before = 0


    def save_to_mongo(self):
        print("time:%s %s" % (time.strftime("%Y/%m/%d  %H:%M:%S"), "Y" * 100))
        print(self.content_block)

        self.content_block["content"] = self.content_block["content"].replace(" ","")
        for key in ["转发微博","分享图片","分享视频","Repost","轉發微博"]:
            if key in self.content_block["content"]:
                self.content_block["content"] = ""
                break
        if self.content_block["content"] == "" and len(self.content_block["comments"]) == 0:
            self.mongo_links.delete_one({"tag": self.get_hostname() + str(self.number)})
            return
        try:
            self.mongo_comments.insert_one(self.content_block)
            self.mongo_links.delete_one({"tag": self.get_hostname() + str(self.number)})
        except Exception as e:
            print(e)

    def get_mongo(self, collection_name):
        client = pymongo.MongoClient(config.MONGO_URL)
        mongodb = client['weibo']
        collection = mongodb[collection_name]
        return collection

    def get_hostname(self):
        return socket.gethostname()
    # def shuchu(self):
    #     t = self.mongo_comments.find_one()
    #     for url in t["comments"]:
    #         # print(url.encode("utf8").decode("unicode_escape"))
    def get_url(self):
        host_name = self.get_hostname()
        self.mongo_links.update_one({"tag": 0}, {'$set': {"tag": host_name+str(self.number)}})
        url = self.mongo_links.find_one({"tag": host_name+str(self.number)})

        return url["url"]

    def get_page(self, url):
        for i in range(10):
            try:
                # page = requests.get(url, timeout=3, proxies=tools.get_proxy(), headers=tools.headers)
                page = requests.post(tools.base_url, json={"url": url, "headers": tools.headers})

            except Exception as e:
                continue
            page = json.loads(page.text)
            if page["type"] == "error":
                continue
            return page
        else:
            return ""

    def parse_start_page(self, page):
        page = page["text"]
        # print(page)
        content_pattern  = re.compile(r'<div class=\\"WB_text W_f14\\"([\s\S]+?)>\\n([\s\S]+?)<\\/div>')
        content = content_pattern.findall(page)
        try:
            content = content[0][1]
        except Exception as e:
            print(e)
            self.mongo_links.delete_one({"tag": self.get_hostname() + str(self.number)})
            global sleep_time
            sleep_time += 1
            if sleep_time > 500:
                sleep_time = 60
            return ""
        at_pattern = re.compile('@([\s\S]+?)<')
        at_pattern_list = re.findall(at_pattern,content)
        for at in at_pattern_list:
            content = content.replace("@%s<" % at, "@%s=+=<" % at)
        content = content.replace(" ","")
        content = re.sub("<img([\s\S]+?)>","",content)
        content = re.sub('<iclass=\\\\"W_ficonficon_cd_video\\\\">([\s\S]+?)<\\\\/i>([^<]+)',"",content)
        content = re.sub('<iclass=\\\\"W_ficonficon_cd_link\\\\">([\s\S]+?)<\\\\/i>([^<]+)',"",content)
        content = re.sub('<iclass=([\s\S]+?)<\\\\/i>([^<]+)', "", content)
        content = re.sub("<\\\\/a>", "",content)
        content = re.sub("<a([\s\S]+?)>", "", content)
        content = re.sub("\\\\/\\\\/([\s\S]+)", "", content)
        content = re.sub("\u200b","", content)
        content = content.replace("&nbsp;","")
        content = content.replace("<br>"," ")
        content = content.replace("#", "")
        # content = content.replace("@","")
        content = content.replace(" ","")


        try:
            # Wide UCS-4 build
            myre = re.compile(u'['
                              u'\U0001F300-\U0001F64F'
                              u'\U0001F680-\U0001F6FF'
                              u'\u2600-\u2B55]+',
                              re.UNICODE)
        except re.error:
            # Narrow UCS-2 build
            myre = re.compile(u'('
                              u'\ud83c[\udf00-\udfff]|'
                              u'\ud83d[\udc00-\ude4f\ude80-\udeff]|'
                              u'[\u2600-\u2B55])+',
                              re.UNICODE)

        content = myre.sub('', content)
        content = re.sub('\[([\s\S]+?)\]',"",content)
        content = content.replace("&quot;","")
        temp_content = content
        temp_content = re.sub("@([\s\S]+?)=\+=","", temp_content)
        if temp_content == "":
            content = ""
        id_pattern = re.compile(r"value=comment:(\d+?)\\")
        id = id_pattern.findall(page)
        try:
            id = id[1]
        except Exception as e:
            try:
                id = id[0]
            except Exception as e:
                print("--" * 100)
                print(page)
                print("--" * 100)

        return {
            "content": content,
            "id": id
        }

    def parse_comment_page(self, page):
        page = page["text"]
        # page = r"""{"code":"100000","msg":"","data":{"html":"<!-- \u8bc4\u8bba\u76d6\u697c\u5927\u8bc4\u8bba\u5217\u8868 -->\n<div class=\"list_box\">\n    <div class=\"list_ul\" node-type=\"comment_list\" >\n        <!-- \u7981\u6b62\u8bc4\u8bba -->\n                <!-- \u8bc4\u8bba\u5217\u8868\u4e0d\u4e3a\u7a7a -->\n        <!-- \u61d2\u52a0\u8f7d -->\n                <!-- \u61d2\u52a0\u8f7d -->\n        <!-- \u67e5\u770b\u66f4\u591a -->\n                    <a  action-type = \"click_more_comment\" href=\"javascript:void(0);\"  suda-uatrack=\"key=click comments&value=click:singl_weibo:1\" action-data=\"id=4359179735265288&root_comment_max_id=4359501828308381&root_comment_max_id_type=1&root_comment_ext_param=&page=22&filter=hot&sum_comment_number=299&filter_tips_before=1\" class=\"WB_cardmore S_txt1 S_line1 clearfix\"><span class=\"more_txt\">\u67e5\u770b\u66f4\u591a<i class=\"W_ficon ficon_arrow_down S_ficon\">c<\/i><\/span><\/a>\n                <!-- \u67e5\u770b\u66f4\u591a -->\n    <\/div>\n<\/div>\n<!-- \u5927\u8bc4\u8bba\u5217\u8868 -->\n","count":3667}}"""
        page = page.replace(" ", "")
        # 获得子url连接
        url_list = []
        sub_comment_urls_pattern = re.compile(r'more_comment=big([\s\S]+?)\\"')
        next_comment_urls_pattern = re.compile(r'comment_loading\\"action-data=\\"([\s\S]+?)\\')
        click_next_comment_urls_pattern = re.compile(r'click_more_comment\\"([\s\S]+?)action-data=\\"([\s\S]+?)\\')
        sub_comment_urls = sub_comment_urls_pattern.findall(page)
        next_comment_urls = next_comment_urls_pattern.findall(page)
        click_next_comment_urls  = click_next_comment_urls_pattern.findall(page)
        for sub_comment_url in sub_comment_urls:
            url_list.append("more_comment=big" + sub_comment_url)
        for next_comment_url in next_comment_urls:
            url_list.append(next_comment_url)
        for click_next_comment_url in click_next_comment_urls:
            url_list.append(click_next_comment_url[1])

        # 获得当前页的评论
        page = page.replace(r"\n", "")
        page = re.sub(r"<a([\s\S]+?)<\\/a>", "", page)
        page = re.sub(r"<img([\s\S]+?)>", "", page)
        comments_pattern = re.compile(r'<divclass=\\"WB_text\\">([\s\S]+?)<\\/div>')
        comments_list = comments_pattern.findall(page)
        for comment in comments_list:
            if comment != r"\u7b49\u4eba" and comment != r"\uff1a":
                comment = comment.replace(r"\uff1a","")
                # comment = comment.decode("raw_unicode_escape")
                comment = comment.encode('utf8').decode("raw_unicode_escape")
                temp_comment = comment
                # comment = re.sub(r"\\u([\s\S]{4})","",comment)
                # re.compile(r"[\s\w]+")
                # chre = re.compile(ur".*[\u4E00-\u9FA5]+.*")
                # jpre = re.compile(ur".*[\u3040-\u30FF\u31F0-\u31FF]+.*")
                # hgre = re.compile(ur".*[\u1100-\u11FF\u3130-\u318F\uAC00-\uD7AF]+

                temp_comment = re.sub("[\u4E00-\u9FA5]+","",temp_comment)
                temp_comment = re.sub("[\u3040-\u30FF\u31F0-\u31FF]+", "", temp_comment)
                temp_comment = re.sub("[\u1100-\u11FF\u3130-\u318F\uAC00-\uD7AF]+", "", temp_comment)
                temp_comment = re.sub("[\s\w]+", "", temp_comment)
                temp_comment = re.sub(r'[{}]+'.format(string.punctuation),'', temp_comment)
                for symbol in config.symbol_list:
                    temp_comment = re.sub(symbol, "", temp_comment)
                if len(temp_comment) > 0:
                    try:
                        print(temp_comment)
                    except Exception as e:
                        # print(e)
                        pass
                    else:
                        for i in temp_comment:
                            if i not in List:
                                List.append(i)
                # for i in ["、","，","！"]:
                #     temp_comment = re.sub(i, "", temp_comment)
                # try:
                #     if len(temp_comment) > 0:
                #         print(temp_comment)
                # except:
                #     pass
                for i in temp_comment:
                    if i == "\\":
                        # print(comment)
                        continue
                    comment = re.sub(i,"",comment)
                comment = re.sub(r"<\\/div>", "", comment)
                comment = re.sub(r"\\/\\/([\s\S]+)","",comment)
                comment = comment.replace("&nbsp;","")
                comment = comment.replace("回复:","")
                comment = re.sub(r"\\","",comment)

                # flag = True
                if comment == "转发微博":
                    continue
                if comment == "\u56de\u590d\u7684\u8868\u6001\u003a":
                    continue
                comment = re.sub('\[([\s\S]+?)\]', "", comment)
                comment = re.sub("图片评论","", comment)
                comment = re.sub("<([\s\S]+?)>","", comment)
                if len(comment) > 0:
                    self.content_block["comments"].append(comment)
                # print(comment)
        # if flag:
        #     return url_list
        # else:
        #     return []
        return url_list
        # return url_list

    def comment_crawler(self, url):
        if "sum_comment_number" in url:
            number_pattern = re.compile("sum_comment_number=([\d]+)")
            number = number_pattern.findall(url)[0]
            if number == self.num_before:
                self.repeat_times += 1
            else:
                self.repeat_times = 0
                self.num_before = number
        # print("6")
        if self.repeat_times > 5:
            # print(7)
            return
        page = self.get_page(url)
        if page == "":
            return
        # print(9)
        url_list = self.parse_comment_page(page)
        # print(url_list)
        for url in url_list:
            self.comment_crawler(
                "https://weibo.com/aj/v6/comment/big?ajwvr=6&" + url + "&from=singleWeiBo&__rnd=%s" % int(time.time()))

    def detail_crawler(self):
        # print("2")

        start_page = self.get_page(self.url)
        # print("3")
        if start_page == "":
            print("time:%s %s" % (time.strftime("%Y/%m/%d  %H:%M:%S"), "E" * 100))
            print(self.url)
            return

        content_and_id = self.parse_start_page(start_page)
        if content_and_id == "":
            time.sleep(sleep_time)
            return
        # print("4")
        self.content_block["content"] = content_and_id["content"]
        "4165962447475313&from=singleWeiBo&__rnd=1556011879728"
        self.comment_crawler("https://weibo.com/aj/v6/comment/big?ajwvr=6&id=%s&from=singleWeiBo&__rnd=%s" % (
            content_and_id["id"], int(time.time())))
        self.save_to_mongo()
def fuck(number):
    # print("1")
    temp = WeiboDetail(number)
    # temp.parse_comment_page("")
    temp.detail_crawler()
    sem.release()
if __name__=="__main__":
    tsk = []
    while True:
        NUMBER += 1
        print("time:%s, number is %s" % (time.strftime("%Y/%m/%d  %H:%M:%S"), NUMBER))
        sem.acquire()
        t = threading.Thread(target=fuck,args=(NUMBER,))
        t.start()
        tsk.append(t)
    # for task in tsk:
    #     task.join()
    # print(List)
# fuck(1)
# temp.shuchu()
