# coding=utf-8

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Field, Item


class CorpItem(Item):
    corp_id = Field()  # id 标识
    corp_name = Field()  # 企业名称
    certification = Field()  # 认证部门
    update_time = Field()  # 更新时间
    province = Field()  # 省份
    city = Field()  # 城市
    area = Field()  # 区域
    """
    联系方式 contact start
    """
    contact = Field()  # 联系人
    postal = Field()  # 邮编
    phone = Field()  # 电话
    cellphone = Field()  # 手机
    fax = Field()  # 传真
    email = Field()  # 传真
    website = Field()  # 网址
    qq = Field()  # qq号
    address = Field()  # 地址
    """
    contact end
    """

    """
    工商档案 commercial file start
    """
    organization = Field() # 机构代码
    registration = Field() # 工商注册号
    establishment = Field() # 成立日期
    capital = Field() # 注册资本
    corp_status = Field() # 企业状态
    qualification = Field() # 企业资质
    representative = Field() # 法人代表
    operating_period = Field() # 经营期限
    register_address = Field() # 注册地址
    """
    commercial file end
    """

    """
    招聘信息 job start
    """
    job = Field()
    """
    job end
    """

    """
    产品和服务 product start
    """
    product = Field()
    """
    product end
    """

    """
    简介 corp info start
    """
    info = Field()
    """
    info end
    """

    """
    相关企业 relate start
    """
    relate = Field()
    """
    relate end
    """

    """
    法人相同企业 artificial start
    """
    artificial = Field()
    """
    relate end
    """

