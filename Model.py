# 为了避免重复则要重新设计表结构，这里面设计模型
# 这里面实现表创建；
from peewee import *

db = MySQLDatabase('spider_example', host ="127.0.0.1",port =3306, user="root",password = "qq14733051")

class BaseModel(Model):
    class Meta:
        database = db

#建立类来是来生成表；
# 设计数据表的时候有几个重要点要注意
"""
1.char类型，要设置最大长度；默认最大长度255； 如果大于255则要自己设置一下
2.对于无法确定最大长度的字段可以设置为Text
3.设计表的时候采集到的数据尽量先做格式化处理；
default和null = True 的时候，能设置默认值则要设置默认值

"""


class Topic(BaseModel):
    title = CharField()
    id = IntegerField(primary_key=True) #用来提取ID
    author = CharField()
    create_time = DateTimeField()
    answer_nums = IntegerField(default=0)
    click_nums = IntegerField(default=0) #查看数量；
    score = IntegerField(default=0) #赏分
    status = CharField() #状态
    last_time = DateTimeField()

    jt1 = FloatField() #结帖率
    content = TextField(default="")
    praised_nums = IntegerField(default=0) #点赞数量


class Answer(BaseModel):
    post_id = IntegerField(primary_key=True)
    topic_id = CharField()
    author = CharField()
    content = TextField(default="")
    create_time = DateTimeField()
    praised_nums = IntegerField(default=0) #点赞数


class Author(BaseModel):
    name = CharField()
    author_id = CharField(primary_key=True)
    click_nums = CharField(default=0) #访问数
    original_nums = CharField(default=0) #原创数
    rate = CharField(default=-1) #排名
    answer_nums = CharField(default=0) #评论数
    praise_nums = CharField(default=0) #获赞数
    follower_nums = CharField(default=0) #粉丝数

# 生成表
if __name__ == "__main__":
    db.create_tables([Topic,Answer,Author])