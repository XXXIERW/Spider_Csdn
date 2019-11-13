# Spider_Csdn
## 这里面是关于编写，爬取CSDN中用户的发帖，粉丝数，以及评论结帖率等等；并且将他们存入到Mysql中
### 关于Mysql的使用
**Model.py里面的模块存放的是关于Mysql里面的使用模块**

基本的数据库连接以及存储；

**关于spider**

### spider里面使用到的是：

1.peewee的模块，这个号称最简便的数据库使用，以及最统一的格式；这里面只是有关于Mysql里面的基本操作

2.Xpath正则表达式的关于选取内容

3.以及这里面的网页分析

**分析网页，拿到需要的需求是一个重要的步骤**

只有分析出自己的需求才知道自己需要什么；

知道自己需要什么才能知道要提取什么内容存储什么

要注意的是：Spider是不会自动过滤到之前爬取的地方，所以它会重复的爬取一个点，这时候就需要一个数据库的过滤来过滤重复爬取的内容，以达到最优状态；

**部分网站会做一些反爬来过滤掉一些基本的爬虫**

_关于Header的基本防爬_

我们这边使用的是通过获取到浏览器的Header来替换我们请求我们的网页，可以在spider里面见到这一项操作；
···
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
}
    author = Author()
    author_id = url.split("/")[-1]
    res_text = requests.get(url,headers=headers).text
··· 
  _这时候我们就可以看到我们又能访问到页面的内容了_
  
 **关于Spider就这写，可以下载下来尝试，思考里面一些基本的语法使用**
