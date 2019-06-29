import requests
headers = {
            "Host": "weibo.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36",
            "Cookie": "SINAGLOBAL=1971032401731.4163.1551954096720; YF-V5-G0=451b3eb7a5a4008f8b81de1fcc8cf90e; Ugrow-G0=6fd5dedc9d0f894fec342d051b79679e; login_sid_t=e34618d77d877134bc5c3dc4061b2509; cross_origin_proto=SSL; _s_tentry=passport.weibo.com; Apache=4656873948018.445.1560395296973; ULV=1560395296978:1:1:1:4656873948018.445.1560395296973:; wb_view_log=1920*10801; un=15110248779; wb_view_log_5435529966=1920*10801; WBtopGlobal_register_version=3cccf158e973a877; SCF=AkxnN3UOg2_gI0lQpJs3Ce5OGPpjj6UqYzvn1zDxH3Uwl3b35CjAtVKOURGjNAkkh-iPd3fV3KdOrDRqiumv8x8.; SUHB=0wn1jo3H0zlFQX; webim_unReadCount=%7B%22time%22%3A1560429869784%2C%22dm_pub_total%22%3A0%2C%22chat_group_pc%22%3A0%2C%22allcountNum%22%3A2%2C%22msgbox%22%3A0%7D; SUB=_2AkMqXsoLdcPxrAZVm_0QzmLraotH-jyZi6P9An7uJhMyAxgv7nBXqSVutBF-XFJVO0gHZ69gfDqyu-jJLhcZggAo; SUBP=0033WrSXqPxfM72wWs9jqgMF55529P9D9WhQlbikHdp9PNYWkFUk2aa35JpVF02feK27eoBRS0M4; UOR=,,login.sina.com.cn; YF-Page-G0=536a03a0e34e2b3b4ccd2da6946dab22|1560431104|1560430826"
}
page = requests.get("https://weibo.com/mrjjxw?refer_flag=1001030103_", headers=headers,
                            timeout=3)
print(page)
print(page.text)