"""
完成三个任务：
    1.爬取网易云热搜榜歌曲，收集每首歌的详细信息
    2.爬取网易云音乐评论数最多的10音乐的所有评论，并做数据分析
    3.尝试爬取用户信息
"""
import requests
from bs4 import BeautifulSoup
import time
###1.爬取热搜榜歌曲
# 1.2.7 存入数据库中
import pymongo

# 1. 建立与数据库的链接
client = pymongo.MongoClient("localhost", 27017)

# 2. 得到数据库信息
PopSongs = client["PopSongs"]


#爬取网易云音乐热搜榜歌曲信息
class pop_music:
    def __init__(self):
        self.url = "http://music.163.com/discover/toplist?id=3778678" #热搜榜地址
        self.name = "hot_list" #列表名称
        self.headers = {
            "Host":"music.163.com",
            "Cookie":"__f_=1524528575328; _ntes_nnid=4cba2fd344f585bfe0e03cbbb3c9c17e,1524528574442; _ntes_nuid=4cba2fd344f585bfe0e03cbbb3c9c17e; NTES_PASSPORT=0jkbIt1UVGa3pXx7o3jO7wHk31Lmr6DQuZbMp6m4ez99mVb8mPEkn1P4fgjrN2kciThyiDiB2QWXZ2XGS_if3XogCjZwz01YbBgAutC8iSCT3cwipr42GcGknZ0kmuCtDYgKofho8ds5S0F27Xv_w_6ezL9YOGshEuS9dp6tcZvlkuNArGnGXz8zk; P_INFO=m17600413737@163.com|1524528623|1|study|00&99|bej&1521962174&study#bej&null#10#0#0|176737&1||17600413737@163.com; _iuqxldmzr_=32; WM_TID=IxNUGDEIqy8zld2pNxNBzYxvWjYOcesL; __remember_me=true; JSESSIONID-WYYY=a%2BJr3OQNqQNaGUuRxcQFTv6iapxcvKFGt9j%2B5XhiYNYYYSjpKE6IcdBiob1SQY8b1foXv%2BlNw2hwcN0wtYVYFlgxlwsZhmyeM4V%5C0WnsBeO8g%2FYVZESXAyeRRSmlFDHxkC2%5CtnoCApIpt4DrlFiqsPHvyQDBlB669fqJp3hFlIeypXg0%3A1524621208113; __utma=94650624.591314524.1524561402.1524561402.1524619408.2; __utmc=94650624; __utmz=94650624.1524619408.2.2.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; MUSIC_U=1e5fcc5a112a9cb997236190990736a15053be85f4706fa644cb2cd130ffeea3a94699c38349c04a3df5895304d6b6656e89c43dc31bab57305842396b5dfc01; __csrf=2cd55686431f3be3a525d97d24a57d6a; __utmb=94650624.6.10.1524619408",
            "Referer":"http://music.163.com/",
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
        }
    def get_songs_id(self):
        """1.1 获取热搜榜歌曲id """
        web_data = requests.get(self.url,headers=self.headers)
        soup = BeautifulSoup(web_data.text,"lxml")
        songs_with_infos = soup.select("ul.f-hide")[0].find_all("a") #获取歌曲的id和名称
        ids = []
        for song in songs_with_infos:
            id = song.get("href")[9:]
            ids.append(id)
        return ids

    def get_songs_info(self):
        """1.2 爬取每首歌曲的信息
         1.歌曲名称
         2.歌手及id
         3.所属专辑及id
         """

        ids = self.get_songs_id()

        data = {}
        collection_name = self.name
        collection_name = PopSongs[collection_name]

        for id in ids:
            url = "http://music.163.com/song?id={}".format(id)
            #print(url)
            #1.2.1 获取网页信息
            songs_data = requests.get(url,headers=self.headers)
            soup = BeautifulSoup(songs_data.text,"lxml")
            songs_info = soup.select("p.des.s-fc4")

            #1.2.2 获取歌曲名称
            title = soup.select("em.f-ff2")[0].get_text()
            data["title"] = title

            #1.2.3 获取歌手及专辑id
            try:
                artist_id = songs_info[0].find_all("a")[0].get("href")[11:]
                album_id = songs_info[1].find_all("a")[0].get("href")[10:]
            except:
                pass
            data["artist_id"] = artist_id
            data["album_id"] = album_id

            #1.2.4 获取歌手姓名及专辑姓名
            for item in songs_info:
                artist_and_album = item.get_text().split("：")
                data[artist_and_album[0]] = artist_and_album[1]

            #1.2.5 获取被收藏到的歌单名称
            stored_albums = soup.select("p.f-thide > a")
            Albums = []
            for stored_album in stored_albums[:3]:
                albums = stored_album.get("title")
                if albums == None:
                    pass
                Albums.append(albums)
            data["包含这首歌的歌单"] = Albums

            #1.2.6 获取相似歌曲
            likely_songs = soup.select("a.s-fc1")
            likely_songs_all = []
            for likely_song in likely_songs:
                like = likely_song.get("title")
                likely_songs_all.append(like)
            data["相似歌曲"] = likely_songs_all
            data["_id"] = id

            print(data)

            collection_name.insert_one(data)

            #return data
        #print(songs_info)

#一、爬取飙升榜音乐信息
class upgrade_music(pop_music):
    def __init__(self):
        self.url = "http://music.163.com/discover/toplist?id=19723756"
        self.name = "upgrade_list"
        self.headers = pop_music().headers

#二、爬取新歌榜音乐信息
class new_music(pop_music):
    def __init__(self):
        self.url = "http://music.163.com/discover/toplist?id=3779629"
        self.name = "new_list"
        self.headers = pop_music().headers

#三、爬取原创歌曲榜音乐信息
class original_music(pop_music):
    def __init__(self):
        self.url = "http://music.163.com/discover/toplist?id=2884035"
        self.name = "original_list"
        self.headers = pop_music().headers

#四、爬取电音榜音乐信息
class electric_music(pop_music):
    def __init__(self):
        self.url = "http://music.163.com/discover/toplist?id=1978921795"
        self.name = "electric_list"
        self.headers = pop_music().headers

#五、爬取嘻哈榜音乐信息
class hip_pop_music(pop_music):
    def __init__(self):
        self.url = "http://music.163.com/discover/toplist?id=991319590"
        self.name = "hip_pop_list"
        self.headers = pop_music().headers

#六、爬取古典型榜音乐信息
class classical_music(pop_music):
    def __init__(self):
        self.url = "http://music.163.com/discover/toplist?id=71384707"
        self.name = "classical_list"
        self.headers = pop_music().headers

#七、爬取Billboard榜音乐信息
class billboard_music(pop_music):
    def __init__(self):
        self.url = "http://music.163.com/discover/toplist?id=60198"
        self.name = "billboard_list"
        self.headers = pop_music().headers

#八、爬取中国top榜音乐信息
class china_top_music(pop_music):
    def __init__(self):
        self.url = "http://music.163.com/discover/toplist?id=64016"
        self.name = "china_top_list"
        self.headers = pop_music().headers

# for item in [china_top_music(),upgrade_music(),new_music(),original_music(),electric_music(),hip_pop_music(),classical_music(),billboard_music()]:
#     item.get_songs_info()

m = pop_music()
m.get_songs_info()
