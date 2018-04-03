# encoding=utf-8
import datetime
import re
import logging
import requests
from scrapy.selector import Selector
from scrapy.spiders import CrawlSpider
from sinaspiders.items import InformationItem, TweetsItem, FollowsItem, FansItem
from bs4 import BeautifulSoup
from scrapy.http import Request
import sinaspiders.tool as tool


class Spider(CrawlSpider):
    name = "sinaspiders"
    host = "http://weibo.cn"
    #logging.getLogger("requests").setLevel(logging.WARNING)
    #query='%25E8%2599%259A%25E6%258B%259F%25E7%258E%25B0%25E5%25AE%259E' #虚拟现实
    #start_urls = ['http://weibo.cn/comment/EwFJ67kHu?rl=1&page=1']
    '''
    start_urls=[]
    before_urls= []
    for i in range(0, 1):
        with open('C:/Users/Administrator/Desktop/sina/sina/sina_peron_info_%s.txt' % str(i), 'r',
                  encoding='utf-8') as f:
            for line in f:
                before_urls.append(line.split('{]')[0].strip())
    for i in range(0,11):
        with open('C:/Users/Administrator/Desktop/sina/sina/sina_fans_%d.txt' %i,'r',encoding='utf-8') as f:
            for line in f:
                #if 'http://weibo.com/u/' in line.split('[}')[1]:
                    #temp_id=line.split('[}')[1].split('?')[0].split('/')[-1]
                temp_id=line.split('{]')[1].replace('\n','')
                if temp_id not in before_urls:
                   start_urls.append(temp_id)
    for i in range(0, 13):
        with open('C:/Users/Administrator/Desktop/sina/sina/sina_follows_%d.txt' % i, 'r',encoding='utf-8') as f:
            for line in f:
                # if 'http://weibo.com/u/' in line.split('[}')[1]:
                # temp_id=line.split('[}')[1].split('?')[0].split('/')[-1]
                temp_id = line.split('{]')[1].replace('\n', '')
                if temp_id not in before_urls:
                    start_urls.append(temp_id)
    #url='http://s.weibo.com/weibo/%s&Refer=index&page=%d'%(query,1)
    '''
    start_urls = ['1008085010']
    before_urls=[]
    scrawl_ID = set(start_urls)  # 记录待爬的微博ID
    finish_ID = set(before_urls)  # 记录已爬的微博ID

    '''
    def parse(self, response):
        page=int(response.url.split('=')[-1])
        for sel in response.xpath('//div[@class="c"]'):
            id=sel.xpath('@id').extract_first()
            if id==None:
                continue
            user_name=''.join(sel.xpath('a[1]/text()').extract())
            content_data=''.join(sel.xpath('span[1]/text()').extract())
            content=''.join(re.findall( u"[\u4e00-\u9fa5_a-zA-Z0-9]|[\（\）\《\》\——\；\，\。\‘\’\“\”\<\>\！\《\》\【\】\*\&\……\￥\#\@\~]|[\^,.!`?+=\_\-:;\']",content_data))
            if '回复:' in content:
               huifu=sel.xpath('span[1]/a/text()').extract()[0]
            else:
               huifu=' '
            zan=''.join(sel.xpath('span[2]/a/text()').extract())
            data= '%s[}%s[}%s[}%s[}%s' %(id,user_name,content,huifu,zan)
            with open('C:/Users/Administrator/Desktop/commons/weibo.txt', 'a', encoding='utf-8') as f:
                f.write(data)
                f.write('\n')
        if page==50:
            return None
        follow_url='http://weibo.cn/comment/EwFJ67kHu?rl=1&page=%d' %(page+1)
        yield Request(url=follow_url,callback=self.parse)
    '''
    #'''
    def start_requests(self):
        while self.scrawl_ID.__len__():
            ID = self.scrawl_ID.pop()
            self.finish_ID.add(ID)  # 加入已爬队列
            ID = str(ID)
            follows = []
            followsItems = FollowsItem()
            followsItems["_id"] = ID
            followsItems["follows"] = follows
            fans = []
            fansItems = FansItem()
            fansItems["_id"] = ID
            fansItems["fans"] = fans
            url_follows = "http://weibo.cn/%s/follow" % ID
            url_fans = "http://weibo.cn/%s/fans" % ID
            url_tweets = "http://weibo.cn/%s/profile?filter=0&page=1" % ID
            url_information0 = "http://weibo.cn/attgroup/opening?uid=%s" % ID
            yield Request(url=url_follows, meta={"item": followsItems, "result": follows },callback=self.parse3)  # 去爬关注人

            yield Request(url=url_information0, meta={"ID": ID}, callback=self.parse0)  # 去爬个人信息

            yield Request(url=url_tweets, meta={"ID": ID}, callback=self.parse2)  # 去爬微博

            yield Request(url=url_fans, meta={"item": fansItems, "result": fans}, callback=self.parse4)  # 去爬粉丝

    def parse0(self, response):
        """ 抓取个人信息1 """
        informationItems = InformationItem()
        selector = Selector(response)
        text0 = selector.xpath('body/div[@class="u"]/div[@class="tip2"]').extract_first()
        if text0:
            num_tweets = re.findall(u'\u5fae\u535a\[(\d+)\]', text0)  # 微博数
            num_follows = re.findall(u'\u5173\u6ce8\[(\d+)\]', text0)  # 关注数
            num_fans = re.findall(u'\u7c89\u4e1d\[(\d+)\]', text0)  # 粉丝数
            if num_tweets:
                informationItems["Num_Tweets"] = int(num_tweets[0])
            if num_follows:
                informationItems["Num_Follows"] = int(num_follows[0])
            if num_fans:
                informationItems["Num_Fans"] = int(num_fans[0])
            informationItems["_id"] = response.meta["ID"]
            url_information1 = "http://weibo.cn/%s/info" % response.meta["ID"]
            yield Request(url=url_information1, meta={"item": informationItems}, callback=self.parse1)

    def parse1(self, response):
        """ 抓取个人信息2 """
        informationItems = response.meta["item"]
        ID = informationItems["_id"]
        num_Tweets=informationItems['Num_Tweets']
        num_follows=informationItems['Num_Follows']
        num_fans=informationItems['Num_Fans']
        selector = Selector(response)
        text1 = ";".join(selector.xpath('body/div[@class="c"]/text()').extract())  # 获取标签里的所有text()
        nickname = re.findall(u'\u6635\u79f0[:|\uff1a](.*?);', text1)  # 昵称
        gender = re.findall(u'\u6027\u522b[:|\uff1a](.*?);', text1)  # 性别
        place = re.findall(u'\u5730\u533a[:|\uff1a](.*?);', text1)  # 地区（包括省份和城市）
        signature = re.findall(u'\u7b80\u4ecb[:|\uff1a](.*?);', text1)  # 个性签名
        birthday = re.findall(u'\u751f\u65e5[:|\uff1a](.*?);', text1)  # 生日
        sexorientation = re.findall(u'\u6027\u53d6\u5411[:|\uff1a](.*?);', text1)  # 性取向
        marriage = re.findall(u'\u611f\u60c5\u72b6\u51b5[:|\uff1a](.*?);', text1)  # 婚姻状况
        url = re.findall(u'\u4e92\u8054\u7f51[:|\uff1a](.*?);', text1)  # 首页链接

        if nickname:
            informationItems["NickName"] = nickname[0]
        else:
            informationItems["NickName"] = ' '

        if gender:
            informationItems["Gender"] = gender[0]
        else:
            informationItems["Gender"] = ' '

        if place:
            place = place[0].split(" ")
            informationItems["Province"] = place[0]
            if len(place) > 1:
                informationItems["City"] = place[1]
            else:
                informationItems["City"] = ' '
        else:
            informationItems["Province"] = ' '
            informationItems["City"] = ' '

        if signature:
            informationItems["Signature"] = signature[0]
        else:
            informationItems["Signature"] = ' '

        if birthday:
            try:
                birthday = datetime.datetime.strptime(birthday[0], "%Y-%m-%d")
                informationItems["Birthday"] = birthday - datetime.timedelta(hours=8)
            except Exception:
                informationItems["Birthday"] = ' '
        else:
            informationItems["Birthday"] = ' '

        if sexorientation:
            if sexorientation[0] == gender[0]:
                informationItems["Sex_Orientation"] = "gay"
            else:
                informationItems["Sex_Orientation"] = "Heterosexual"
        else:
            informationItems["Sex_Orientation"] = ' '

        if marriage:
            informationItems["Marriage"] = marriage[0]
        else:
            informationItems["Marriage"] = ' '

        if url:
            informationItems["URL"] = url[0]
        else:
            informationItems["URL"] = ' '

        data = '%s{]%s{]%s{]%s{]%s{]%s{]%s{]%s{]%s{]%s{]%s{]%s{]%s' % (ID,informationItems["NickName"], informationItems["Gender"], informationItems["Province"],informationItems["City"],informationItems["Signature"],informationItems["Birthday"],informationItems["Sex_Orientation"],informationItems["Marriage"],informationItems["URL"],num_Tweets,num_follows,num_fans)
        tool.GetFile('peron_info', data, 3, 50000)
        #yield informationItems

    def parse2(self, response):
        """ 抓取微博数据 """
        selector = Selector(response)
        tweets = selector.xpath('body/div[@class="c" and @id]')
        for tweet in tweets:
            tweetsItems = TweetsItem()
            id = tweet.xpath('@id').extract_first()  # 微博ID
            content = tweet.xpath('div/span[@class="ctt"]/text()').extract_first()  # 微博内容
            cooridinates = tweet.xpath('div/a/@href').extract_first()  # 定位坐标
            like = re.findall(u'\u8d5e\[(\d+)\]', tweet.extract())  # 点赞数
            transfer = re.findall(u'\u8f6c\u53d1\[(\d+)\]', tweet.extract())  # 转载数
            comment = re.findall(u'\u8bc4\u8bba\[(\d+)\]', tweet.extract())  # 评论数
            others = tweet.xpath('div/span[@class="ct"]/text()').extract_first()  # 求时间和使用工具（手机或平台）

            tweetsItems["ID"] = response.meta["ID"]
            tweetsItems["_id"] = response.meta["ID"] + "-" + id
            if content:
                tweetsItems["Content"] = content.strip(u"[\u4f4d\u7f6e]")  # 去掉最后的"[位置]"
            else:
                tweetsItems["Content"] = ' '

            if cooridinates:
                cooridinates = re.findall('center=([\d|.|,]+)', cooridinates)
                if cooridinates:
                    tweetsItems["Co_oridinates"] = cooridinates[0]
                else:
                    tweetsItems["Co_oridinates"] = ' '
            else:
                tweetsItems["Co_oridinates"] = ' '

            if like:
                tweetsItems["Like"] = int(like[0])
            else:
                tweetsItems["Like"] = ' '

            if transfer:
                tweetsItems["Transfer"] = int(transfer[0])
            else:
                tweetsItems["Transfer"] = ' '

            if comment:
                tweetsItems["Comment"] = int(comment[0])
            else:
                tweetsItems["Comment"] = ' '

            if others:
                others = others.split(u"\u6765\u81ea")
                tweetsItems["PubTime"] = others[0]
                if len(others) == 2:
                    tweetsItems["Tools"] = others[1]
                else:
                    tweetsItems["Tools"] = ' '
            else:
                tweetsItems["PubTime"] = ' '
                tweetsItems["Tools"] = ' '

            data = '%s{]%s{]%s{]%s{]%s{]%s{]%s{]%s{]%s' % (response.meta["ID"],id,tweetsItems["Content"],  tweetsItems["Co_oridinates"], tweetsItems["Like"], tweetsItems["Transfer"], tweetsItems["Comment"], tweetsItems["PubTime"],tweetsItems["Tools"] )
            tool.GetFile('weibo', data, 3, 5000)
            #yield tweetsItems
        url_next = selector.xpath( u'body/div[@class="pa" and @id="pagelist"]/form/div/a[text()="\u4e0b\u9875"]/@href').extract()
        if url_next:
            yield Request(url=self.host + url_next[0], meta={"ID": response.meta["ID"]}, callback=self.parse2)

    def parse3(self, response):
        """ 抓取关注"""
        items = response.meta["item"]
        selector = Selector(response)
        text2 = selector.xpath(u'body//table/tr/td/a[text()="\u5173\u6ce8\u4ed6" or text()="\u5173\u6ce8\u5979"]/@href').extract()
        for elem in text2:
            elem = re.findall('uid=(\d+)', elem)
            if elem:
                response.meta["result"].append(elem[0])
                ID = int(elem[0])

                if ID not in self.finish_ID:  # 新的ID，如果未爬则加入待爬队列
                    self.scrawl_ID.add(ID)
        url_next = selector.xpath(u'body//div[@class="pa" and @id="pagelist"]/form/div/a[text()="\u4e0b\u9875"]/@href').extract()
        if url_next:
            yield Request(url=self.host + url_next[0], meta={"item": items, "result": response.meta["result"]},callback=self.parse3)
        else:  # 如果没有下一页即获取完毕
            for id in items["follows"]:
                data = '%s{]%s' % (items["_id"], id)
                tool.GetFile('follows', data, 3, 10000)
            #yield items

    def parse4(self, response):
        """ 抓取粉丝 """
        items = response.meta["item"]
        selector = Selector(response)
        text2 = selector.xpath(u'body//table/tr/td/a[text()="\u5173\u6ce8\u4ed6" or text()="\u5173\u6ce8\u5979"]/@href').extract()
        for elem in text2:
            elem = re.findall('uid=(\d+)', elem)
            if elem:
                response.meta["result"].append(elem[0])
                ID = int(elem[0])

                if ID not in self.finish_ID:  # 新的ID，如果未爬则加入待爬队列
                    self.scrawl_ID.add(ID)
        url_next = selector.xpath(u'body//div[@class="pa" and @id="pagelist"]/form/div/a[text()="\u4e0b\u9875"]/@href').extract()
        if url_next:
            yield Request(url=self.host + url_next[0], meta={"item": items, "result": response.meta["result"]},callback=self.parse4)
        else:  # 如果没有下一页即获取完毕
            for id in items["fans"]:
                data = '%s{]%s' % (items["_id"], id)
                tool.GetFile('fans', data, 3, 10000)
            #yield items
     #'''