# -*- coding: utf-8 -*-
# @Time : 2018/5/1 14:47
# @Author : 朱超杰
# @contact:zhuchaojie@buaa.edu.cn
# @File : boss_jobs.py

"""
完成BOSS直聘网对自然语言处理相关岗位信息的爬取
需要的信息：
    1.招聘信息标题和对应的url(方面对具体要求进行爬取)
    2.工作地点(可在详细url中进行抓取)
    3.工作经历要求
    4.学历要求
    5.企业名称
    6.企业所属行业
    7.融资阶段
    8.企业规模
    9.HR姓名和职称
    10.发布日期
    11.工资待遇
    12职位描述
    13.任职要求
    14.所属标签
"""
import requests
from bs4 import BeautifulSoup
import pprint
import pymongo
import time
import random
import pandas as pd

# 生成随机user_agent
from fake_useragent import UserAgent
ua = UserAgent()

client = pymongo.MongoClient("localhost", 27017)
boss_jobs = client["boss_jobs"]
BOSS_Job = client["BOSS_Job"]

job_url_client = client["job_url_client"] #每个岗位的url

#"https://www.zhipin.com/c101010100-p100117/?page=1&ka=page-1"
df = pd.read_csv("ips.txt",names=["ip"])
ip_list_avi = []
for ip in df["ip"]:
    ip_list_avi.append(ip)

class BossJobs:
    def __init__(self,key,value):
        #1. 初始化所需要的全局信息
        self.key = key
        self.value = value
        self.url = "https://www.zhipin.com/c101010100-{}/".format(value)
        self.headers = {
            "cookie":"JSESSIONID=""; __c=1525172071; __g=-; __l=l=%2Fwww.zhipin.com%2Fgeek%2Fnew%2Findex%2Fresume&r=; Hm_lvt_194df3105ad7148dcf2b98a91b5e727a=1524963720,1525059037,1525134896,1525172073; Hm_lpvt_194df3105ad7148dcf2b98a91b5e727a=1525172092; __a=83103721.1524025828.1525134895.1525172071.134.15.6.134",
            "referer":"https://www.zhipin.com/?ka=header-home",
            "user-agent":ua.random,
            "upgrade-insecure-requests":"1",
            "accept-encoding":"gzip, deflate, br"

        } #最基本的反反爬机制
        self.proxies = {
            'http:': 'http://{}'.format(random.choice(ip_list_avi)),
            'https:': 'https://{}'.format(random.choice(ip_list_avi))
        } #代理信息

        self.job_category = BOSS_Job[key]
        self.job_url = job_url_client[key]
    def generate_pages(self):
        #2. 生成NLP岗位界面链接信息
        urls = [] #存储生成的链接
        for page in range(1,11):
            url = self.url+"?page={}&ka=page-{}".format(page,page)
            urls.append(url)
        return urls

    def get_jobs_url(self):
        #3. 获得每个工作岗位的详情页面介绍的链接
        urls = self.generate_pages()
        print("正在获取{}的全部岗位链接。。。。。。".format(self.key))
        Urls = {}
        Urls[self.key] = {}
        URLS = []
        for url in urls:
            time.sleep(random.randint(1, 15))

            headers = {
                "cookie": "JSESSIONID=""; __c=1525172071; __g=-; __l=l=%2Fwww.zhipin.com%2Fgeek%2Fnew%2Findex%2Fresume&r=; Hm_lvt_194df3105ad7148dcf2b98a91b5e727a=1524963720,1525059037,1525134896,1525172073; Hm_lpvt_194df3105ad7148dcf2b98a91b5e727a=1525172092; __a=83103721.1524025828.1525134895.1525172071.134.15.6.134",
                "referer": "https://www.zhipin.com/?ka=header-home",
                "user-agent": ua.random,
                "upgrade-insecure-requests": "1",
                "accept-encoding": "gzip, deflate, br"

            }
            proxies = {
                'http:': 'http://{}'.format(random.choice(ip_list_avi)),
                'https:': 'https://{}'.format(random.choice(ip_list_avi))
            }

            web_data = requests.get(url,headers = headers,proxies=proxies)
            soup = BeautifulSoup(web_data.text,"lxml")
            jobs_url = soup.select("div.info-primary > h3.name > a")
             #用来存储页面链接
            for id in jobs_url:
                job_url = "https://www.zhipin.com"+id.get("href")
                URLS.append(job_url)
                print(job_url)
        Urls[self.key]["URLS"] = URLS
        self.job_url.insert_one(Urls)
        return Urls

    def get_job_details(self):
        #4. 获取每个岗位的具体要求
        #4.1 获取岗位链接
        urls = self.job_url.find()
        # 为每一个岗位构建一个独立的字典
        number = 1
        for url in urls[40:]:
            JOBS = {}

            headers = {
                "cookie": "JSESSIONID=""; __c=1525172071; __g=-; __l=l=%2Fwww.zhipin.com%2Fgeek%2Fnew%2Findex%2Fresume&r=; Hm_lvt_194df3105ad7148dcf2b98a91b5e727a=1524963720,1525059037,1525134896,1525172073; Hm_lpvt_194df3105ad7148dcf2b98a91b5e727a=1525172092; __a=83103721.1524025828.1525134895.1525172071.134.15.6.134",
                "referer": "https://www.zhipin.com/?ka=header-home",
                "user-agent": ua.random,
                "upgrade-insecure-requests": "1",
                "accept-encoding": "gzip, deflate, br"

            }
            proxies = {
                'http:': 'http://{}'.format(random.choice(ip_list_avi)),
                'https:': 'https://{}'.format(random.choice(ip_list_avi))
            }
            #4.2 解析网页信息
            time.sleep(random.randint(1,15)) #加入停顿信息
            web_data = requests.get(url, headers=headers, proxies=proxies)
            soup = BeautifulSoup(web_data.text, "lxml")


            #4.3 岗位标题
            try:
                title = soup.select("div.name > h1")[0].get_text()
            except:
                pass
            JOBS[title] = {}
            #4.4 薪资
            try:
                salary = soup.select("div.name > span.badge")[0].get_text()
                #4.5 经验和学历要求

                requirement = soup.select("div.info-primary > p")[0].getText()          #岗位要求
                experience_and_education = requirement.split("经验")[1].split("学历")

                experience = experience_and_education[0][1:]                            #工作经验
                education = experience_and_education[1][1:]
                #4.6 招聘发布时间

                publish_time = soup.select("div.job-author > span")[0].get_text()[3:]
            except:
                pass
            #4.7 岗位标签
            tags = soup.select("div.job-tags > span")
            tag = []
            for i in tags:
                tag.append(i.get_text())
            #4.8 公司名称

            try:
                company_name = soup.select("div.info-company > h3.name > a")[0].get_text()
                #4.9 公司所属类型
                company_name_area = soup.select("div.info-company > p > a")[0].get_text()
                #4.10 公司融资情况和规模
                company_info = str(soup.select("div.info-company > p")[0]).split("</em>") #融资情况和规模
                financing = company_info[0].split("<p>")[1].split("<em")[0]
                company_size = company_info[1].split("<em")[0]
                #4.11 HR信息-姓名
                HR_name = soup.select("div.detail-op > h2")[0].get_text()
                hr_info = str(soup.select("div.detail-op > p")[0]).split("<em")
                hr_profession = hr_info[0].split(">")[1]
                hr_online_time = hr_info[1].split("em>")[1].split("<")[0]
            except:
                pass

            #4.12 获取职位描述

            try:
                job_description = soup.select("div.detail-content > div > div.text")[0].find_all(text=True)
                job_description[0] = job_description[0].strip()
            except:
                pass
            #4.13 工作地址
            try:
                location = soup.select("div.location-address")[0].get_text()
            except:
                pass
            #4. 整合信息
            data = {
                "薪资":salary.replace("K","000"),
                "工作经验":experience,
                "学历":education,
                "标签":tag,
                "发布时间":publish_time,
                "工作地址":location,
                "企业名称":company_name,
                "企业类型":company_name_area,
                "企业规模":company_size,
                "融资情况":financing,
                "HR姓名":HR_name,
                "HR职业":hr_profession,
                "HR在线情况":hr_online_time,
                "岗位描述":job_description


            }
            JOBS[title] = data
            JOBS["_id"] = time.time()
            self.job_category.insert_one(JOBS)


            print("正在爬取{}第：{}份工作信息".format(self.key,number),JOBS)

            if number % 19 ==0:
                print(".............."
                      "O.O.O=-->正在休息<--=O.O.O"
                      "..............")
                time.sleep(200)
            if number %40 ==0:
                break
            number+=1

categories = {
    "机器学习":"p101301",
     "深度学习":"p101302",
     "图像算法":"p101303",
     "图像处理":"p101304",
    #"语音识别":"p101305",
     #"图像识别":"p101306",
     #"算法研究员":"p101307",
    #"自然语言处理":"p100117"
}
# main_ = BossJobs()
# main_.get_job_details()

for key,value in categories.items():
    main_ = BossJobs(key,value)
    main_.get_jobs_url()
