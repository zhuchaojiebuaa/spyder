import requests
import pandas as pd
from bs4 import BeautifulSoup
import time


url = "https://www.leiphone.com/category/ai/page/1"
web_data = requests.get(url)
soup = BeautifulSoup(web_data.text,"lxml")


def get_url_category():
    category = ["sponsor","ai","transportation","aijuejinzhi","fintech","aihealth","letshome","arvr","robot","yanxishe","weiwu","iot"]
    return category

def get_urls(num,category):
    url = "https://www.leiphone.com/category/{}/page/".format(category)
    urls = [url + str(i) for i in range(1,num)]
    return urls

def get_web_data(num,category):
    urls = get_urls(num,category)
    #print(urls)
    for url in urls:
        time.sleep(2)
        web_data = requests.get(url)
        soup = BeautifulSoup(web_data.text,"lxml")
        title_imgUrl = soup.select("img.lazy")
        authors = soup.select("a.aut")
        #print(title_imgUrl)
        article_url = soup.select("div.box > div.word > h3 > a")
        Times = soup.select("div.time")
        for titleANDimg,author,article,Time in zip(title_imgUrl,authors,article_url,Times):
            data = {
                "Category":category,
                "Time":Time.get_text(),
                "Title":titleANDimg.get("title"),
                "Author":author.get_text().replace("\t","").replace("\n",""),
                "Image Url": titleANDimg.get("data-original"),
                "Article Url":article.get("href"),

            }
            print(data)
            dictFile = open("F:\pythons\spyders\LeiFengWang\\News.text","a",encoding="utf-8")
            #print("{}{}".format(data.keys(),data.values()),file=dictFile)
            CiYun_file = open("F:\pythons\spyders\LeiFengWang\\ciyun.txt","a",encoding="utf-8")
            CiYun_file.write(str(data["Title"] + "    "))
            dictFile.write(str(data)+"\n")


#get_web_data(2,"ai")
categories = get_url_category()
for category in categories:
     data = get_web_data(30,category)