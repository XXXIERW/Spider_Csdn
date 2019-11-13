"""
抓取
解析
存储

"""
import re
import ast

from urllib import parse #用来拼接是否是完整的url
from scrapy import Selector #xpath数据提取；
from  datetime import datetime
# from A目录.包1.文件3.py import xxxx

import requests

import sys
sys.path.append("..")
from CSDN_spider.Model import *
# from CSDN_spider.Model.py import *

blog = "https://blog.csdn.net"
domain = "https://bbs.csdn.net"
# 定义一个函数来获取内容链接；
def get_nodes_json():
    left_menu_text = requests.get("https://bbs.csdn.net/dynamic_js/left_menu.js?csdn").text
    # 通过正则表达式来提取需要的内容   .*] 会匹配到内容里面最后一个]的地方；
    nodes_str_match = re.search("forumNodes: (.*])", left_menu_text)
    if nodes_str_match:
        nodes_str = nodes_str_match.group(1).replace("null","None")# 因为JSON里面可以识别null而Python里面只能识别None，但是结果相同；
        nodes_list = ast.literal_eval(nodes_str)  #这是Json里面的方法把JSON类型转为node_list类型；
        return  nodes_list
    return [] #如果上面数据为空的话返回值；


# 要把node_list转成list的内容；
# 将js的格式中url提取到list中；
url_list = []
def process_nodes_list(nodes_list):
    for item in nodes_list:
        if "url" in item and item["url"]:#判断url不为null的时候进行赋值，去null;
            url_list.append(item["url"])
            if "children" in item:
                process_nodes_list(item["children"]) #提取子链接并进行存储


# 去除多余的链接； 这是第一次拿到的url,也就是第一层的url_list
def get_level1_list(node_list):
    level1_url = []
    for item in nodes_list:
        if "url" in item and item["url"]:
            level1_url.append(item["url"])
    return level1_url

nodes_list =[]
def get_last_urls():
    # 获取最终需要抓取的url
    nodes_list = get_nodes_json()  #拿到上面提取的url并且进行存储
    process_nodes_list(nodes_list) #通过这个方法进行格式转换并且存储到list里面
    level1_url = get_level1_list(nodes_list)  #拿到第一层的url
    last_urls = []
# 拿到提取url并且进行判断是否在第一次提取的url里面如果没有就进行添加，
# 然后在添加上所有的版块，就能提取到所有的url
    for url in url_list:
        if url not in level1_url:
            last_urls.append(url)

    all_urls = []
    for url in last_urls:
        all_urls.append(parse.urljoin(domain,url))
        all_urls.append(parse.urljoin(domain,url+"/recommend")) #精华贴；
        all_urls.append(parse.urljoin(domain,url+"/closed")) #已解决；
    return all_urls


def parse_topic(url):
    topic = Topic()
    topic_id = url.split("/")[-1]
    #获取帖子的详情，以及回复，结帖率
    res_text = requests.get(url).text
    sel = Selector(text=res_text)
    #     通过分析可以知道我们需要的div格式
    #     .//div[starts-with(@id,'post-')]  通过搜索所需要的内容所共有的属性提取；
    all_div = sel.xpath(".//div[starts-with(@id,'post-')]")
    topic_item = all_div[0]
    #拿到内容  需要分析内容在哪个标签下面
    content = topic_item.xpath(".//div[@class='post_body post_body_min_h']").extract()[0]
    praised_nums = topic_item.xpath(".//label[@class='red_praise digg']//em/text()").extract()[0]#点赞数；
    jt1 = 0
    if topic_item.xpath(".//div[@class='close_topic']/text()").extract():
        jt1_str = topic_item.xpath(".//div[@class='close_topic']/text()").extract()[0]
        jt1_match = re.search("(\d+)%",jt1_str)
        if jt1_match:
            jt1 = float(jt1_match.group(1))
    existed_topics = Topic.select().where(Topic.id==topic_id)
    if existed_topics:
        topic = existed_topics[0]
        topic.content = content
        topic.jt1 = jt1
        topic.praised_nums = int(praised_nums)
        topic.save()  #已经存在直接调用保存
    for answer_item in all_div[1:]:
        # 需要爬取一个id作为唯一值，避免出现重复；
        answer = Answer()

        post_id = int(answer_item.xpath(".//@data-post-id").extract()[0])
        answer.post_id = post_id
        answer.topic_id = topic_id
        author_info = answer_item.xpath(".//div[@class='nick_name']//a[1]/@href").extract()[0]
        answer.author = author_info.split("/")[-1]
        create_time_str = answer_item.xpath(".//label[@class='date_time']/text()").extract()[0]
        create_time = datetime.strptime(create_time_str,"%Y-%m-%d %H:%M:%S")
        answer.create_time = create_time
        content = answer_item.xpath(".//div[@class='post_body post_body_min_h']").extract()[0]
        answer.content = content
        praised_nums = answer_item.xpath(".//label[@class='red_praise digg']//em/text()").extract()[0]
        answer.praised_nums = int(praised_nums)
        existed_answer = Answer.select().where(Answer.post_id==post_id)
        if existed_answer:
            answer.save()
        else:
            answer.save(force_insert=True)

    # next_page = sel.xpath("//a[@class='pageliststy next_page']/@href").extract()
    # if next_page:
    #     next_url = parse.urljoin(domain,next_page[0])
    #     parse_topic(next_url)


def parse_author(url):
    #获取用户的详情
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
    }
    author = Author()
    author_id = url.split("/")[-1]
    res_text = requests.get(url,headers=headers).text
    sel = Selector(text=res_text)
    all_div_strs = sel.xpath("//div[@class='data-info d-flex item-tiling']/dl/dd/span/text()").extract()
    # 处理回车换行符调用strio()就可以直接去除；
    if sel.xpath("//div[@class='grade-box clearfix']/dl[4]/dd/a/text()").extract():
        rate = sel.xpath("//div[@class='grade-box clearfix']/dl[4]/dd/a/text()").extract()[0].strip()
        author.rate = rate
    if sel.xpath("//div[@class='user-info d-flex flex-column profile-intro-name-box']/div/span/a/text()").extract():
        name = sel.xpath("//div[@class='user-info d-flex flex-column profile-intro-name-box']/div/span/a/text()").extract()[0].strip()
        author.name = name
    if sel.xpath("//div[@class='data-info d-flex item-tiling']/dl/dd/a/span/text()").extract():
        original_nums = sel.xpath("//div[@class='data-info d-flex item-tiling']/dl/dd/a/span/text()").extract()[0]
        author.original_nums = original_nums
    if all_div_strs:
        follower_nums = all_div_strs[0]
        praise_nums = all_div_strs[1]
        answer_nums = all_div_strs[2]
        click_nums = all_div_strs[3]
        author.follower_nums = follower_nums
        author.praise_nums = praise_nums
        author.answer_nums = answer_nums
        author.click_nums = click_nums
    author.author_id = author_id

    existed_author = Author.select().where(Author.author_id==author_id)
    if existed_author:
        author.save()  #已经存在直接调用保存
    else:
        author.save(force_insert=True)

# all_div = sel.xpath(".//div[starts-with(@id,'post-')]")
# 提取列表页的url;
# xpath是从1开始不是从0开始； -1一般都是取最后一个
# 通过分析可以知道，每个子链接对应的是每个tr，则要去提取每个tr然后在遍历提取内容；
# 这边暂时使用xpath来提取； 需要注意的是寻找它可以重复使用的唯一定位值；
# 通过分析可以知道tr里面的td不仅存了需要的链接，也存储了我们所需要的每个信息；
# extract()[0]表示提取到准确的某个值的时候,如果extract()为空则会报异常
def parse_list(url):
    res_text = requests.get(url).text
    sel = Selector(text=res_text)
    all_trs = sel.xpath("//table[@class='forums_tab_table']//tr")[2:]
    for tr in all_trs:
        topic = Topic()
        # tr 再次xpath则会变成上面的xpath拼接，则要修改为在前面加个.则表示从当前路径开始；
        if tr.xpath(".//td[1]/span/text()").extract():
            status = tr.xpath(".//td[1]/span/text()").extract()[0]
        if tr.xpath(".//td[2]/em/text()").extract():
            score = tr.xpath(".//td[2]/em/text()").extract()[0]
        if len(tr.xpath(".//td[3]/a").extract()) > 1:
            topic_url = parse.urljoin(domain,tr.xpath(".//td[3]/a[2]/@href").extract()[0])
            topic_title = tr.xpath(".//td[3]/a[2]/text()").extract()[0]
        elif tr.xpath(".//td[3]/a").extract():
            topic_url = parse.urljoin(domain,tr.xpath(".//td[3]/a/@href").extract()[0]) # href标签 等属性要加上@
            topic_title = tr.xpath(".//td[3]/a/text()").extract()[0]
        if tr.xpath(".//td[4]/a/@href").extract():
            author_url = parse.urljoin(blog,tr.xpath(".//td[4]/a/@href").extract()[0])
        author_id = author_url.split("/")[-1] # 拿到用户id
        author_url1 = parse.urljoin(blog,author_id)
        if tr.xpath(".//td[4]/em/text()").extract():
            create_time_str = tr.xpath(".//td[4]/em/text()").extract()[0]
        if tr.xpath(".//td[5]/span/text()").extract():
            answer_info = tr.xpath(".//td[5]/span/text()").extract()[0]
        answer_nums = answer_info.split("/")[0]
        click_num = answer_info.split("/")[1]
        if tr.xpath(".//td[6]/em/text()").extract():
            last_time_str = tr.xpath(".//td[6]/em/text()").extract()[0]
        #         将时间类型转成datatime
        last_time = datetime.strptime(last_time_str,"%Y-%m-%d %H:%M")
        create_time = datetime.strptime(create_time_str,"%Y-%m-%d %H:%M")

        topic.id = int(topic_url.split("/")[-1])
        topic.title = topic_title
        topic.author = author_id
        topic.click_nums = int(click_num)
        topic.answer_nums = int(answer_nums)
        topic.create_time = create_time
        topic.last_time = last_time
        topic.score = int(score)
        topic.status = status

        #save的逻辑是既做了保存的逻辑，创建的逻辑；
        # force_insert=True 直接进行一个insert操作，则做不了更新；则要先进行查询；
        existed_topics = Topic.select().where(Topic.id==topic.id)
        if existed_topics:
            topic.save()  #已经存在直接调用保存
        else:
            topic.save(force_insert=True)
        parse_author(author_url1)
        parse_topic(topic_url)
    # 获取下一页的url
    next_page = sel.xpath("//a[@class='pageliststy next_page']/@href").extract()
    if next_page:
        next_url = parse.urljoin(domain,next_page[0])
        parse_list(next_url)


if __name__ == "__main__":
    last_urls = get_last_urls()
    for url in last_urls:
        parse_list(url)

