import requests
import re
import socket
import json
import threading
if socket.gethostname() == "ISZ4DI1Z6MV6Z6K":
    import config
else:
    import product_config as config
import tools
import time
import pymongo
SEM = threading.BoundedSemaphore(10)
NUMBER = 0
class GetWeiboLinks(object):
    def __init__(self):
        self.number = NUMBER
        self.user_mongo = self.get_mongo("users_id")
        self.user_id = self.get_user_id()
        self.weibo_links_mongo = self.get_mongo("weibo_links")
        self.link_urls = []
        self.distinguish_link_urls = []


    def get_mongo(self, collection_name):
        client = pymongo.MongoClient(config.MONGO_URL)
        mongodb = client['weibo']
        collection = mongodb[collection_name]
        return collection

    def get_user_id(self):
        tag = socket.gethostname() + str(self.number)
        self.user_mongo.update_one({"tag":0},{'$set': {"tag": tag }})
        user_id = self.user_mongo.find_one({"tag": tag})
        print(user_id)
        return user_id["id"]

    def get_real_url(self):
        url = "https://weibo.com/u/%s?is_all=1" % self.user_id
        try_times = 0
        while True:
            try:
                page = requests.post(tools.base_url,
                                     json={"url": url,
                                           "headers": tools.headers})
            except Exception as e:
                print(e)
                try_times += 1
                if try_times > 10:
                    return ""
                continue
            page = json.loads(page.text)
            if page["type"] == "error":
                try_times += 1
                if try_times > 10:
                    return ""
                continue

            break
        print(page["status_code"])
        if page["status_code"] == 200:
            print(200)
            return "/u/%s" % self.user_id
        elif page["status_code"] == 302:
            print(302)
            headers = json.loads(page["headers"])
            print(headers)
            if headers["Location"] == "/":
                return ""
            else:
                return headers["Location"].split("?")[0]
        else:
            return "wrong"

    def parse_links_page(self, page):
        flag = False
        page = page["text"]
        links_pattern = re.compile(r"\\\/(\d+?)\\\/([\d\w]+?)\?from=page_(\d+?)_profile&wvr=6&mod=weibotime")
        all_links = links_pattern.findall(page)
        if len(all_links) != 0:
            flag = True
        for link in all_links:
            if str(link[0]) in str(link[2]):
                url_link = "https://weibo.com/%s/%s?from=page_%s_profile&wvr=6&mod=weibotime&type=comment" % (
                    link[0], link[1], link[2])
                if url_link not in self.distinguish_link_urls:
                    self.distinguish_link_urls.append(url_link)
                    self.link_urls.append({"url": url_link,"tag":0})
        return flag

    def get_basic_params(self, page):
        page = page["text"]
        domain_pattern = re.compile("CONFIG\['domain'\]='(\d+?)'")
        domid_pattern = re.compile('"domid":"Pl_Official_MyProfileFeed__(\d+?)"')
        id_pattern = re.compile("CONFIG\['page_id'\]='(\d+?)'")
        nickName_pattern = re.compile("CONFIG\['onick'\]='([\s\S]+?)'")
        domain = domain_pattern.findall(page)
        domid = domid_pattern.findall(page)
        id = id_pattern.findall(page)
        nick_name = nickName_pattern.findall(page)
        domain = domain[0]
        domid = "Pl_Official_MyProfileFeed__" + str(domid[0])
        id = id[0]
        nick_name = nick_name[0]
        return {
            "domain": domain,
            "id": id,
            "pl_name": domid,
            "nick_name": nick_name
        }

        pass

    def mongo_delete_id(self):
        self.user_mongo.delete_one({"id": str(self.user_id)})

    def mongo_save_urls(self):
        print("time:%s, YYYYYYYYYYYYYYYYYY" % (time.strftime("%Y/%m/%d  %H:%M:%S"),))
        self.user_mongo.update_one({"id": self.user_id}, {'$set': {"tag": 2}})
        try:
            self.weibo_links_mongo.insert_many(self.link_urls)
        except Exception as e:
            print(e)
            print(self.user_id)

    def get_links(self):
        real_id = self.get_real_url()
        if real_id == "":
            print("real_id is None, id is %s" % self.user_id)
            # self.mongo_delete_id()
            return
        elif real_id == "wrong":
            print("real_id is Wrong, id is %s" % self.user_id)
            return
        page_num = 0
        params = {}
        while True:
            page_num += 1
            while True:
                url_one = "https://weibo.com%s?is_search=0&visible=0&is_all=1&is_tag=0&profile_ftype=1&page=%s" % (
                    real_id, page_num)
                try:

                    page = requests.post(tools.base_url,
                                         json={"url": url_one,
                                               "headers": tools.headers})
                except Exception as e:

                    continue
                page = json.loads(page.text)
                if page["type"] == "error":
                    continue

                flag = self.parse_links_page(page)
                break
            if not flag:
                break
            if page_num == 1:
                params = self.get_basic_params(page)
            while True:
                url_two = "https://weibo.com/p/aj/v6/mblog/mbloglist?ajwvr=6&domain=%s&is_search=0&" \
                          "visible=0&is_all=1&is_tag=0&profile_ftype=1&page=%s&pagebar=0&pl_name=%s" \
                          "&id=%s&script_uri=%s&" \
                          "feed_type=0&pre_page=%s&domain_op=%s&__rnd=%s" % (
                              params["domain"], page_num, params["pl_name"], params["id"], real_id, page_num,
                              params["domain"], int(time.time()))
                try:
                    page = requests.post(tools.base_url,
                                         json={"url": url_two,
                                               "headers": tools.headers})
                except Exception as e:
                    # print(e)
                    # print(url_two)
                    # print("aaaaaaaab")
                    continue
                page = json.loads(page.text)
                if page["type"] == "error":
                    continue

                flag = self.parse_links_page(page)
                break
            if not flag:
                break
            while True:
                url_three = "https://weibo.com/p/aj/v6/mblog/mbloglist?ajwvr=6&domain=%s&is_search=0&" \
                            "visible=0&is_all=1&is_tag=0&profile_ftype=1&page=%s&pagebar=1&pl_name=%s" \
                            "&id=%s&script_uri=%s&" \
                            "feed_type=0&pre_page=%s&domain_op=%s&__rnd=%s" % (
                                params["domain"], page_num, params["pl_name"], params["id"], real_id, page_num,
                                params["domain"], int(time.time()))
                try:
                    page = requests.post(tools.base_url,
                                         json={"url": url_two,
                                               "headers": tools.headers})
                except Exception as e:
                    # print(e)
                    # print(url_three)
                    # print("aaaaaaaac")
                    continue
                page = json.loads(page.text)
                if page["type"] == "error":
                    continue
                flag = self.parse_links_page(page)
                break
            if not flag:
                break
        self.mongo_save_urls()
def get_weibo_links():
    crawl_class = GetWeiboLinks()
    crawl_class.get_links()
    SEM.release()
def init():
    client = pymongo.MongoClient(config.MONGO_URL)
    mongodb = client['weibo']
    collection = mongodb["weibo_links"]
    collection.update_many({},{'$set': {"tag":0}})
    collection = mongodb["users_id"]
    collection.update_many({"tag":{"$ne":2}}, {'$set': {"tag": 0}})
if __name__ == "__main__":
    # init()
    total  = 0
    tsk = []
    while True:
        NUMBER += 1
        total += 1
        print("time: %s, number: %s" % (time.strftime("%Y/%m/%d  %H:%M:%S"),total))
        SEM.acquire()
        t = threading.Thread(target=get_weibo_links, args=())
        t.start()
        tsk.append(t)

    # for task in tsk:
    #     task.join()


# if __name__ == "__main__":
#     total  = 0
#     pool = Pool(processes=4)
#     for i in range(1,600):
#         total += 1
#         print(total)
#         pool.apply_async(get_weibo_links, args=(1,))
#         # if total > 600:
#         #     break
#     pool.close()
#     pool.join()