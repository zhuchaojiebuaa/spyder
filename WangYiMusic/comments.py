"""
爬取网易云音乐歌曲评论及点赞数

"""
import requests
from bs4 import BeautifulSoup
import time
import pprint
import json
import pymongo

#1.链接已有数据库
client = pymongo.MongoClient("localhost", 27017)
PopSongs = client["PopSongs"]

#2.从数据库中获取待爬取的歌曲id
class songs_info:
    def __init__(self,name):
        self.name = name #数据库列名称

    def return_songs_info(self):
        #1.1 读取数据库中的信息

        list_name = PopSongs[self.name] #新建列表信息
        ids = []
        titles = []
        for item in list_name.find():
            id = item["_id"]
            title = item["title"]
            ids.append(id)
            titles.append(title)
        return ids,titles

comments_info = client["comments_info"]

#3.抓取评论，并存入数据库
class comment:
    def __init__(self,name):
       self.headers = {
            "Host":"music.163.com",
            "Cookie":"__f_=1524528575328; _ntes_nnid=4cba2fd344f585bfe0e03cbbb3c9c17e,1524528574442; _ntes_nuid=4cba2fd344f585bfe0e03cbbb3c9c17e; NTES_PASSPORT=0jkbIt1UVGa3pXx7o3jO7wHk31Lmr6DQuZbMp6m4ez99mVb8mPEkn1P4fgjrN2kciThyiDiB2QWXZ2XGS_if3XogCjZwz01YbBgAutC8iSCT3cwipr42GcGknZ0kmuCtDYgKofho8ds5S0F27Xv_w_6ezL9YOGshEuS9dp6tcZvlkuNArGnGXz8zk; P_INFO=m17600413737@163.com|1524528623|1|study|00&99|bej&1521962174&study#bej&null#10#0#0|176737&1||17600413737@163.com; _iuqxldmzr_=32; WM_TID=IxNUGDEIqy8zld2pNxNBzYxvWjYOcesL; __remember_me=true; JSESSIONID-WYYY=a%2BJr3OQNqQNaGUuRxcQFTv6iapxcvKFGt9j%2B5XhiYNYYYSjpKE6IcdBiob1SQY8b1foXv%2BlNw2hwcN0wtYVYFlgxlwsZhmyeM4V%5C0WnsBeO8g%2FYVZESXAyeRRSmlFDHxkC2%5CtnoCApIpt4DrlFiqsPHvyQDBlB669fqJp3hFlIeypXg0%3A1524621208113; __utma=94650624.591314524.1524561402.1524561402.1524619408.2; __utmc=94650624; __utmz=94650624.1524619408.2.2.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; MUSIC_U=1e5fcc5a112a9cb997236190990736a15053be85f4706fa644cb2cd130ffeea3a94699c38349c04a3df5895304d6b6656e89c43dc31bab57305842396b5dfc01; __csrf=2cd55686431f3be3a525d97d24a57d6a; __utmb=94650624.6.10.1524619408",
            "Referer":"http://music.163.com/",
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
        }
       self.pxs = {
           "http":"http://183.159.85.34:18118",
           "https":"http://183.159.94.146:18118",

       }
       self.name = name


    def get_comment_data(self):
        #2.1 获取评论信息
        #2.1.1 获取歌曲id
        Songs_info = songs_info(self.name)
        ids,titles = Songs_info.return_songs_info()

        i = 1 #进行计数
        for id in ids:
            title = titles[ids.index(id)]
            TITLE = {}

            comments_list = []
            url = "http://music.163.com/api/v1/resource/comments/R_SO_4_{}".format(id)
            time.sleep(9)
            web_data = requests.get(url,headers = self.headers)
            soup = BeautifulSoup(web_data.text,"lxml")
            #获取评论信息
            music_comments = soup.find_all("p")[0].get_text()
            #格式转换
            try:
                music_comments = json.loads(music_comments)["hotComments"]
            except:
                pass

            for item in music_comments:
                data = {}
                try :
                    data["评论"] = item["content"]
                    data["用户"] = item["user"]["nickname"]
                    data["用户id"] = item["user"]["userId"]
                    data["用户VIP等级"] = item["user"]["vipType"]
                    data["评论点赞数"] = item["likedCount"]
                    #将时间格式化处理
                    time_ = item["time"]
                    time_ = int(str(time_)[:10])
                    timeArray = time.localtime(time_)
                    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                    data["评论时间"] = otherStyleTime
                    comments_list.append(data)
                except:
                    pass

            TITLE[title] = comments_list

            print("正在爬取第: {}首歌曲".format(i),TITLE)
            i += 1

            #contents[title] = DATA
            #contents["_id"] = id
            comments_info_name = comments_info[self.name]
            #print(contents)
            try:
                comments_info_name.insert_one(TITLE)
            except:
                pass
        #pprint.pprint(music_comments["hotComments"])

#4. 循环爬取所有信息
list_names = ["original_list","upgrade_list"]
for list_name in list_names:
    comments = comment(name=list_name)
    comments.get_comment_data()
