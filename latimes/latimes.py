"""
1.获取当前时间主页新闻信息：
    a).所属类别
    b).链接地址
    c).封面图片地址
    d).作者
2.获取late report新闻信息(与上述内容一致)
3.按照类别爬取
ENTERTAINMENT，LOCAL，SPORTS，NATION & WORLD，POLITICS，OPINION，TRAVEL，BUSINESS，CALIFORNIA LIFE & STYLE
"""

import requests
from bs4 import BeautifulSoup
import pprint
import pymongo
import time

client = pymongo.MongoClient("localhost", 27017)
latimes = client["latimes"]

latimes_news = latimes["latimes_news"]
#1.获取当前页面的信息
class news_id:
    def __init__(self):
        #1.1 初始化信息
        self.url = "http://www.latimes.com/"
        self.headers = {
            "Cookie":"_ga=GA1.3.962825603.1524811741; _gid=GA1.3.1626064694.1524811741; s_fid=3A994A9B91289B3B-2F1CAA9EAB5F7AD1; s_cc=true; _cb_ls=1; _cb=P8OP4CBN0UJDfIz-F; _cb_svref=https%3A%2F%2Fwww.baidu.com%2Flink%3Furl%3D_oqAlajunZwjFRhZE_LKohCzIOoZsRbpsSdszPj-6BIgNG59BO5j60Vrh_X1gpZU%26wd%3D%26eqid%3Df6fdb12e00044e8e000000065ae2c7d7; bounceClientVisit1762v=N4IgNgDiBcIBYBcEQKQGYCCKBMAxHuA7sQHRgCGCAlgLYCmAziQMYD2NBIANCAE4whihEgCNyVACYBXFuxABfIA; _parsely_session={%22sid%22:1%2C%22surl%22:%22http://www.latimes.com/%22%2C%22sref%22:%22https://www.baidu.com/link?url=_oqAlajunZwjFRhZE_LKohCzIOoZsRbpsSdszPj-6BIgNG59BO5j60Vrh_X1gpZU&wd=&eqid=f6fdb12e00044e8e000000065ae2c7d7%22%2C%22sts%22:1524811743054%2C%22slts%22:0}; _parsely_visitor={%22id%22:%22e023bd82-51cd-4899-9be2-94b6b1ec6151%22%2C%22session_count%22:1%2C%22last_session_ts%22:1524811743054}; uuid=863da752-983d-4958-8f85-d821dc99e522; psync_uuid=087915ed-e4a8-4bc4-90a5-710a484a26da; _sp_ses.8129=*; __qca=P0-1023606549-1524811774624; __ibxl=1; s_sq=%5B%5BB%5D%5D; _chartbeat2=.1524811741835.1524812596462.1.CUYK-GBdX_0HCzWY6zBp5OS4DvB8Zb.9; _uetsid=_uet18d0b7fd; _sp_id.8129=b94aec3749170f08.1524811746.1.1524812599.1524811746; RT=\"sl=8&ss=1524811736485&tt=207732&obo=0&bcn=%2F%2F36f1f340.akstat.io%2F&sh=1524812623780%3D8%3A0%3A207732%2C1524812595317%3D7%3A0%3A179337%2C1524812521092%3D6%3A0%3A176558%2C1524812071362%3D5%3A0%3A144049%2C1524812069556%3D4%3A0%3A123437&dm=latimes.com&si=c42144bd-0fa4-41f7-bc3a-b688a040808b&ld=1524812623780&r=http%3A%2F%2Fwww.latimes.com%2F&ul=1524813093621\"",
            "Host":"www.latimes.com",
            "Referer":"http://www.latimes.com/local/lanow/la-me-ln-oc-homeless-lawsuit-20180426-story.html",
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
        }
        self.pxs = {
            'http:': 'http://121.232.146.184',
            'https:': 'https://144.255.48.197'
        }

        """ 网页分析结果：将内容分为三个section，每个section中包含若干个类别
        #c36L4R1iZbQoQq > div.flex-grid
        section下的div.data-pb-id为类别信息，每个类别信息中包含两部分：div.card-content border-bottom为当前
        类别的顶部新闻；div.card-content card-content-no-space-top为其他新闻
        """

    def get_web_data(self,url):
        #1.2 返回网页信息
        time.sleep(2)
        web_data = requests.get(url,headers = self.headers,proxies = self.pxs)
        soup = BeautifulSoup(web_data.text,"lxml")
        return soup

    def header_news(self):
        #1.3 读取每个section下的head新闻信息
        soup = self.get_web_data(url=self.url)

        titles_url_1 = soup.select("h5 > a")
        titles_url_2 = soup.select("a.recommender")
        titles = titles_url_2 + titles_url_1

        for item in titles:
            DATA = {}
            Url = item.get("href")
            category = Url.split("/")[1]


            #1.3.1 获取网页信息
            id = self.url + Url

            #1.3.2 获取新闻内容
            Soup = self.get_web_data(id)
            texts = Soup.select("p")
            text = []
            for content in texts:
                text.append(content.get_text() + "\n")

            #1.3.3 获取图片地址
            images = Soup.select("img.full-width")
            image = []
            for i in images:
                src = i.get("src")
                if src[:4] == "http":
                    image.append(src)

            #1.3.4 获取图片字幕
            try:
                image_caption = Soup.select("figcaption.caption-text > div")[0].get_text()
            except:
                pass

            #1.3.5 获取发布日期
            pub_time = ""
            for ti in Soup.select("span.timestamp.timestamp-article"):
                pub_time += ti.get_text()

            #1.3.6 获取作者信息
            for i in Soup.select("span.uppercase"):
                author = i.get_text()

            #1.3.7 数据整合
            DATA[item.get_text()] = {}
            DATA[item.get_text()]["author"] = author  # 作业信息
            DATA[item.get_text()]["category"] = category            #新闻所属类别
            DATA[item.get_text()]["pub_time"] = pub_time            #发布日期
            DATA[item.get_text()]["url"] = Url                      #新闻url的部分
            DATA[item.get_text()]["images"] = image                 #图片地址-完整
            DATA[item.get_text()]["content"] = text                 #文本内容
            DATA[item.get_text()]["img_caption"] = image_caption    #图片字幕
            print(DATA)

            #1.3.8 插入数据库
            try:
                latimes_news.insert_one(DATA)
            except:
                pass


test = news_id()

print(test.header_news())
