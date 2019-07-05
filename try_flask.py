from gevent import monkey

monkey.patch_all()
import requests
from flask import Flask, request
from gevent.pywsgi import WSGIServer
import json
import time
import tools
app = Flask(__name__)


@app.route("/")
def hello_world():
    return "Hello World"


@app.route("/get", methods=["POST"])
def get():
    data = request.get_data()
    json_data = json.loads(data)
    try:
        proxies = tools.get_proxy()
    except Exception as e:
        print("*" * 100)
        return json.dumps({
            "type": "error",
            "text": "proxy ip occur error"})
    # try:
    #     page = requests.get(json_data["url"], headers=json_data["headers"], proxies=proxies,
    #                         timeout=3)
    # except Exception as e:
    #     return json.dumps({
    #         "type": "error",
    #         "text": str(e)})
    # print("%s get url: %s" % (time.strftime("%Y/%m/%d  %H:%M:%S"),json_data["url"]))
    # return json.dumps({"type": "content",
    #         "status_code": page.status_code,
    #         "text": page.text,
    #         # "content": page.content,
    #         "encoding": page.encoding,
    #         "headers": str(page.headers).replace("'","\"")
    #                    })
    try_times = 0
    while True:
        try:
            print("aa")
            page = requests.get(json_data["url"], headers=json_data["headers"], proxies=proxies,
                                timeout=3, allow_redirects=False)
        except Exception as e:
            return json.dumps({
                "type": "error",
                "text": str(e)})
        print("%s get url: %s" % (time.strftime("%Y/%m/%d  %H:%M:%S"),json_data["url"]))
        if try_times  > 10:
            return json.dumps({
                "type": "error",
                "text": str("ERROR")})
        try_times += 1
        if int(page.status_code) == 302 and ("https://weibo.com" in json_data["url"]):
            json_data["url"] = "https://weibo.com" + page.headers["Location"]
            continue
        return json.dumps({"type": "content",
                "status_code": page.status_code,
                "text": page.text,
                # "content": page.content,
                "encoding": page.encoding,
                "headers": str(page.headers).replace("'","\"")
                           })


if __name__ == "__main__":
    http_server = WSGIServer(("0.0.0.0", 5000), app)
    http_server.serve_forever()
