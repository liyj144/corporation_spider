# coding=utf-8
import re


class CorpParseModel(object):
    def __init__(self):
        self.re_link_href = re.compile(ur'href="(.*?)".*>(.*)</a>')
        self.re_corp_id = re.compile(ur'.*/company/(.*?)/')
        self.re_page_url = re.compile(ur'href="(.*?)".*>(?:.*)</a>')
        self.re_corp_tips = re.compile(ur'认证部门：(.*?)(?:\s|&nbsp;|&amp;nbsp|\xa0)*更新时间：(.*?)\s')

    """
    根据level值获取下一级地区信息，level值代表如下：
        10：省
        20：市
        30：区
    """
    def get_city_list(self, response, level="10"):
        ar_city = response.xpath("//li[@class='level%s']/a" % level).re(self.re_link_href)
        city_list = []
        if not ar_city:
            return city_list
        for i in xrange(0, len(ar_city), 2):
            url = ar_city[i]
            name = ar_city[i + 1]
            if name in [u"全国"]:
                continue
            city_list.append((url, name))
        return city_list

    """
    获取页面上企业列表
    """
    def get_corp_list(self, response):
        ar_corp = response.xpath("//div[@class='regionEntList']/ul/li/a/@href").extract()
        if not len(ar_corp):
            return []
        return ar_corp

    """
    获取下一页链接地址
    """
    def get_next_page_url(self, response):
        next_page = response.css(".pag-numble").xpath(u"//a[@title='下一页']/@href").extract()
        if next_page:
            return next_page[0]
        return False

    """
    根据url获取到企业id
    """
    def get_corp_id(self, response):
        re_corp = self.re_corp_id.match(response.url)
        if re_corp:
            return re_corp.group(1)
        return False

    def get_corp_id_by_url(self, url):
        re_corp = self.re_corp_id.match(url)
        if re_corp:
            return re_corp.group(1)
        return False

    """
    获取企业名称、认证部门、更新时间等信息
    """
    def get_corp_tips(self, response, item):
        corp_name = response.xpath("//div[@class='entDetailHeader']/h3/text()").extract()
        corp_name = corp_name[0] if corp_name else ""
        corp_tips = response.xpath("//div[@class='entDetailHeader']/div[@class='tips']").re(self.re_corp_tips)
        certification = corp_tips[0] if corp_tips else ''
        update_time = corp_tips[1] if corp_tips else ''
        item['corp_name'] = corp_name
        item['certification'] = certification
        item['update_time'] = update_time

    """
    联系人信息
    """
    def get_contact(self, response, item):
        ar_contact = response.xpath("//div[@class='entDetailSum'][1]//td/text()").extract()
        ar_contact_item = ("contact", "postal", "phone", "cellphone", "fax", "email", "website", "qq", "address")
        for index, contact in enumerate(ar_contact_item):
            if len(ar_contact) > index:
                item[ar_contact_item[index]] = ar_contact[index].strip()

    """
    工商档案
    """
    def get_commercial(self, response, item):
        #print response.xpath("//div[@class='entDetailSum'][contains(text(), '工商档案')]")
        ar_xpath = response.css(".weixin-img").xpath("preceding-sibling::table//td")
        xpath_len = len(ar_xpath)
        item['organization'] = ar_xpath[0].xpath("text()").extract()[0].strip() if xpath_len > 0 else ""
        item['registration'] = ar_xpath[1].xpath("text()").extract()[0].strip() if xpath_len > 1 else ""
        item['establishment'] = ar_xpath[2].xpath("text()").extract()[0].strip() if xpath_len > 2 else ""
        item['capital'] = ar_xpath[3].xpath("text()").extract()[0].strip() if xpath_len > 3 else ""
        item['corp_status'] = ar_xpath[4].xpath("em/text()").extract()[0].strip() if xpath_len > 4 else ""
        item['qualification'] = ar_xpath[5].xpath("text()").extract()[0].strip() if xpath_len > 5 else ""
        if xpath_len > 6 and len(ar_xpath[6].xpath("a/text()").extract()) > 0:
            item['representative'] = ar_xpath[6].xpath("a/text()").extract()[0].strip()
        else:
            item['representative'] = ""
        item['operating_period'] = ar_xpath[7].xpath("text()").extract()[0].strip() if xpath_len > 7 else ""
        if  xpath_len > 8 and len(ar_xpath[8].xpath("a/text()").extract()) > 0:
            item['register_address'] = ar_xpath[8].xpath("a/text()").extract()[0].strip()
        else:
            item['register_address'] = ""

    """
    招聘信息
    """
    def get_job(self, response):
        print response.css("#divBDZhaoPin")
        pass

    """
    公司产品和公司简介
    """
    def get_corp_info(self, response, item):
        xpath_info = response.css("div.entDetailSum2")
        item["product"] = xpath_info.xpath("preceding-sibling::div[@class='entDetailSum']//div[@class='content']/div[@class='left']/text()")[0].extract()
        item["info"] = xpath_info.css('fieldset').xpath("string(div[@class='content'])").extract()[0].strip()

    """
    获取相关企业信息
    """
    def get_relate_corp(self, response, item):
        xpath_relate = response.xpath(u"//div[@class='entDetailSum'][contains(.,'相关企业')]")[0].css("li")
        ar_link = xpath_relate.css("a").re(self.re_link_href)
        ar_status = xpath_relate.css("em::text")
        ar_corp = []
        if len(ar_link) / 2 == len(ar_status):
            for index, status in enumerate(ar_status):
                corp_status = status.extract().strip()
                corp_name = ar_link[2 * index + 1].strip()
                copr_id = ''
                link = ar_link[2 * index].strip()
                re_corp = self.re_corp_id.match(link)
                if re_corp:
                    copr_id =  re_corp.group(1)
                ar_corp.append({
                    "copr_id": copr_id,
                    "corp_name": corp_name,
                    "corp_status": corp_status
                })
        item['relate'] = ar_corp

    """
    法人名称相同的企业
    """
    def get_artificial_info(self, response):
        raise IndexError("just test")
        pass





