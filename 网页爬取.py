#!/usr/bin/env python
#encoding=utf-8

from selenium import webdriver
import re
import time
import pymysql

a = []#储存<h3>
b = []#存储连接
c = []#存储标题
d = []#存储上传时间
e = [] #存储公众号标题

driver = webdriver.Chrome()
#打开网页
def _open_url(url):
    driver.get(url)
    return driver

#找出网页对应的所有代码,我们可以发现我们所需要的连接和标题都在<h3>标签里面
def _daima_url(driver):
    html=driver.page_source
    for match in re.finditer(r'<h3>[\s\S]*?</h3>', html):
        a.append(match.group(0))
    return a

def _lianjie(a):
    b.clear()
    #开始抽取连接
    for i in a:
        match = re.findall(r'href="[\s\S]*?"', i)
    # 清除href=" str(match[0]) 解释 因为match变量是一个列表 无法进行下一个正则匹配 我们要吧里面内容全部换成str类型才能匹配下一个正则

        result = re.sub('href="', "", str(match[0]))
    #清除amp;
        result2 = re.sub("amp;", "", result)
    #现在我们将正确连接储存到b中
        b.append('https://weixin.sogou.com'+result2)
    return b



def _biaoti(a):
    c.clear()
    for i in a:
        result = re.findall(r"uigs=[\s\S]*?</a>", i)

        result1 = re.sub(r"uigs=[\S\s]*?>", "", str(result[0]))
        result2 = re.sub("<em><!--red_beg-->", "", result1)
        result3 = re.sub("<!--red_end--></em>", "", result2)
        result4 = re.sub("</a>", "", result3)
        c.append(result4)
    return c


#上传时间

def _shangchuantime(driver):
    #可以根据元素看起来上传时间都保存在class=“s2”的标签中 我们用selenium中的CSS查找元素找出所有的class=“s2”的元素并用for循环保存每一个
    #element.get_attribute('outerHTML') 是网页的源代码
    elements = driver.find_elements_by_css_selector('.s2')
    for element in elements:
        #<span class="s2"><script>document.write(timeConvert('1604116776'))</script>2020-10-31</span>
        #这是其中的一条 我们用找标题的方法将2020-10-31找出来
        result = re.findall(r"</script>[\S\s]*?<", element.get_attribute('outerHTML'))
        result1 = re.sub("</script>", "", str(result[0]))
        result2 = re.sub("<", "", result1)
        d.append(result2)
    return d



def _GZHtitle(driver):
    elements = driver.find_elements_by_css_selector('.account')

    #按照上述方法把标题找出来
    for element in elements:
        result0 = re.findall(r"uigs=[\S\s]*?<", element.get_attribute('outerHTML'))
        result1 = re.sub("</script>", "", str(result0[0]))
        result2 = re.sub(r"uigs=[\S\s]*?>", "", result1)
        result3 = re.sub("<", "", result2)
        e.append(result3)
    return e



def chucun(driver):
    a = _daima_url(driver)
    b = _lianjie(a) #结束后所有连接在b中
    c = _biaoti(a) #结束后所有标题在c中
    d = _shangchuantime(driver) #结束后所有上传时间在d中
    e = _GZHtitle(driver) #结束后所有公众号标题在e中


def zhixing():
    url = 'https://weixin.sogou.com/weixin?type=2&s_from=input&query=%E6%96%B0%E5%8D%8E%E7%BD%91&ie=utf8&_sug_=y&_sug_type_=&w=01019900&sut=10037&sst0=1610508420602&lkt=0%2C0%2C0'
    for k in range(5):
        driver = _open_url(url)
        chucun(driver)
        # 我们找到下一页的连接
        next_daima = driver.find_element_by_id("sogou_next")
        # 下一页连接的源代码
        next_url0 = re.search(r"href[\s\S]*?class", next_daima.get_attribute('outerHTML'))
        # 取出连接
        next_url1 = next_url0.group(0).replace('href="', "")
        next_url2 = 'https://weixin.sogou.com/weixin' + next_url1.replace('class', '')
        url = next_url2.replace('amp;', '')
        time.sleep(3)


if __name__ == "__main__":
    zhixing()
    db = pymysql.connect(host='localhost', user='root', password='root', port=3306, db='微信公众号')
    cursor = db.cursor()
    sql = 'INSERT INTO text(biaoti,lianjie,time,gongzhonghaopingtai) values(%s,%s,%s,%s)'
    for i in range(len(a)):
        try:
            cursor.execute(sql, (c[i], b[i], d[i], e[i]))
            db.commit()
        except:
            db.rollback()

