from bs4 import BeautifulSoup
import pymysql.cursors
import requests

# 创建数据库连接池
connection = pymysql.connect(
    host="localhost",
    user="root",
    password="1234",
    database="spider_douban250",
    cursorclass=pymysql.cursors.DictCursor
)

h = {
    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"

}
proxies = {
    'http': 'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890'
}
base_url = "https://movie.douban.com/top250"

num = eval(input("请输入要爬取的页数："))
with connection:
    for i in range(num):
        url = f"{base_url}?start={i * 25}"
        response = requests.get(url, headers=h, proxies=proxies)
        soup = BeautifulSoup(response.content.decode(), "html.parser")
        items = soup.find_all("div", class_="item")
        for item in items:
            pic_div = item.find("div", class_="pic")
            top = pic_div.em.string
            img = pic_div.a.img
            name = img["alt"]
            url = img["src"]
            piv_hd = item.find("div", class_="hd")
            china_name = piv_hd.find("span", class_="title").string
            English = piv_hd.find_all('span')[1].get_text().split("/")[1]
            actor = item.find("p").get_text().split("\n")[1].split("\xa0")[0].replace("\n", "").replace(" ", "")
            if not item.find("p").get_text().split("\n")[1].split("\xa0")[-1].replace("\n", "").replace(" ", ""):
                actor_zhu = "暂时还无该数据"
            else:
                actor_zhu = item.find("p").get_text().split("\n")[1].split("\xa0")[-1].replace("\n", "").replace(" ", "")
            guo = item.p.get_text().split('/')[-2]
            time = item.find("p").get_text().split("\n")[2].split("/")[0].replace("\n", "").replace(" ", "")
            type = item.p.get_text().split('\n')[2].split('/')[-1]
            pingfen = item.find("div", class_="star").get_text().split('\n')[2]
            pingfen_num = item.find("div", class_="star").get_text().split('\n')[4]
            if not item.find("p", class_="quote"):
                que = "暂时还无简介"
            else:
                que = item.find("p", class_="quote").get_text().replace("\n", "")

            print(top, name, url, china_name, English, guo, time, actor, actor_zhu, type, pingfen, pingfen_num, que)

            with connection.cursor() as cursor:
                sql = "INSERT INTO douban_test1(海报名,海报地址,电影中文名,电影别名,出版地,导演,主演,上架时间,类型,评分,评价人数,宣传简介) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                cursor.execute(sql, (name, url, china_name, English, guo, actor, actor_zhu, time, type, pingfen, pingfen_num, que))
        connection.commit()