# -*- coding: utf-8 -*-
# @Author: Zengjq
# @Date:   2019-03-04 16:25:03
# @Last Modified by:   Zengjq
# @Last Modified time: 2019-03-06 10:48:20
import scrapy
from cartoonmad.items import Dm5Item
import os
import re
import urllib.request
import urllib.parse
import urllib.error
import jsbeautifier
import jsbeautifier.unpackers.packer as packer
import requests
import urllib.request
import urllib.parse
import urllib.error
import urllib.request
import urllib.error
import urllib.parse
from jsbeautifier.unpackers import UnpackingError
from scrapy.utils.project import get_project_settings

settings = get_project_settings()
# jsbeautifier fix
packer.beginstr = ''

packer.endstr = ''

cookies = {'isAdult': '1'}
http_proxy_address = '127.0.0.1:1080'


def get_proxy():
    return 'http://' + http_proxy_address

# requests proxy
proxyDict = None


def use_proxy():
    # urllib2 proxy
    os.environ["http_proxy"] = 'http://' + http_proxy_address
    proxy = urllib.request.ProxyHandler({'http': http_proxy_address})
    opener = urllib.request.build_opener(proxy)
    urllib.request.install_opener(opener)

    # requests proxy
    proxyDict = {
        "http": get_proxy(),
    }


class Dm5Spider(scrapy.Spider):
    name = 'dm5'
    custom_settings = {
        # 'CONCURRENT_ITEMS': 2,
        # 'CONCURRENT_REQUESTS': 2,
        # 'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
        # 'CONCURRENT_REQUESTS_PER_IP': 2,
    }
    allowed_domains = ['dm5.com', 'cdndm5.com']
    download_folder = 'dm5'
    handle_httpstatus_list = [404]

    def start_requests(self):
        manga_no = getattr(self, 'no', None)
        manga_url = getattr(self, 'url', None)
        urls = []
        if manga_no != None and manga_no != '':
            mangas = manga_no.split(' ')
            for manga in mangas:
                if manga_no[0] == '/':
                    manga_no = manga_no[1:]
                if manga_no[-1] != '/':
                    manga_no = manga_no + '/'
                new_url = 'http://www.dm5.com/' + manga_no
                if new_url not in urls:
                    urls.append(new_url)
        if manga_url != None and manga_url != '':
            mangas = manga_url.split(' ')
            for new_url in mangas:
                if new_url[0] == '/':
                    new_url = new_url[1:]
                if new_url[-1] != '/':
                    new_url = new_url + '/'
                if new_url not in urls:
                    urls.append(new_url)

        if (manga_no is None or manga_no == '') and (manga_url == None or manga_url == ''):
            # urls = ['http://www.dm5.com/manhua-wudengfendehuajia']
            urls = ['http://www.dm5.com/manhua-huashengjiangsanmingzhi/']
            urls = ['http://www.dm5.com/manhua-qunzixiamianshiyeshou/']
            # urls = ['http://www.dm5.com/manhua-chengweimowangdefangfa/']
        for url in urls:
            print(url)
            yield scrapy.Request(url, meta={'proxy': ''}, cookies=cookies, callback=self.parse)

    def parse(self, response):
        # scrapy shell http://www.dm5.com/manhua-wudengfendehuajia

        # with open('111.html', 'wb') as f:
        #     f.write(response.body)

        if response.status == 404:
            if response.meta.get('dont_filter', None):
                return
            if '您当前访问的页面不存在' in response.css('html > body::text')[0].extract().strip():
                print('Detect 404, try use proxy')
                use_proxy()
                yield scrapy.Request(response.url, meta={'proxy': get_proxy()}, callback=self.parse, dont_filter=True)
            return

        if response.status == 200:
            if any('进行屏蔽处理' in x for x in response.css('body > div.view-comment > div > div.left-bar > div.warning-bar > p::text').extract()):
                print('Detect block, try use proxy')
                use_proxy()
                yield scrapy.Request(response.url, meta={'proxy': get_proxy()}, callback=self.parse, dont_filter=True)
                return

        proxy = response.meta['proxy']
        # 漫画id
        manga_no = response.url.split('/')[-2]
        manga_name = str(response.css('body > div:nth-child(9) > section > div.banner_detail_form > div.info > p.title::text').extract()[0].strip().replace('?', ''))
        manga_save_folder = os.path.join(self.download_folder, manga_name)
        # with open('111.txt', 'wb') as f:
        #     f.write(response.body)
        # 提取章节
        chapters = response.css("#detail-list-select-1 a")
        # print chapters
        for index, chapter in enumerate(chapters):
            chapter_link = 'http://www.dm5.com' + chapter.attrib['href']
            chapter_name = chapter.attrib['title'].replace('·', ' ')
            if chapter_name is None or chapter_name == '':
                # 空标题特殊处理
                chapter_name = '无标题'
                chapter_no = chapter.css('a::text')[0].extract().strip()[1:-1]
            else:
                chapter_no = chapter_name
                if chapter_no[0] == '第':
                    chapter_no = chapter_no[1:]
                if chapter_no[-1] == '话':
                    chapter_no = chapter_no[:-1]

            # if index != 3:
            #     continue
            yield scrapy.Request(chapter_link, cookies=cookies, meta={'proxy': proxy, 'manga_no': manga_no, 'chapter_no': chapter_no, 'manga_name': manga_name, 'chapter_name': chapter_name, 'manga_save_folder': manga_save_folder}, callback=self.parse_page)

    def parse_page(self, response):
        """
        scrapy shell http://www.dm5.com/m787329/

        """
        manga_no = response.meta['manga_no']
        chapter_no = response.meta['chapter_no']
        manga_name = response.meta['manga_name']
        chapter_name = response.meta['chapter_name']
        manga_save_folder = response.meta['manga_save_folder']
        proxy = response.meta['proxy']
        # 关键的东西
        # 旧版解析参考 https://gist.github.com/tpai/2e68ad86c0e34be6259a
        # 最新的是这个
        # http://css99tel.cdndm5.com/v201903011820/dm5/js/chapternew_v22.js
        mkey = ''
        DM5_CID = re.findall('var DM5_CID=(.*?);', response.body)[0]
        DM5_MID = re.findall('var DM5_MID=(.*?);', response.body)[0]
        DM5_VIEWSIGN_DT = re.findall('var DM5_VIEWSIGN_DT="(.*?)";', response.body)[0]
        DM5_VIEWSIGN = re.findall('var DM5_VIEWSIGN="(.*?)";', response.body)[0]
        DM5_PAGE = response.css('#chapterpager > span::text').extract()[0]
        DM5_IMAGE_COUNT = re.findall('var DM5_IMAGE_COUNT=(.*?);', response.body)[0]
        page_count = DM5_IMAGE_COUNT

        current_page = 0
        current_page += 1
        data = {'cid': DM5_CID, 'page': DM5_PAGE, 'key': mkey, 'language': 1, 'gtk': 6, '_cid': DM5_CID, '_mid': DM5_MID, '_dt': DM5_VIEWSIGN_DT, '_sign': DM5_VIEWSIGN}
        pages_url = 'http://www.dm5.com/m' + str(data['cid']) + '/chapterfun.ashx?' + urllib.parse.urlencode(data)
        yield scrapy.Request(pages_url, cookies=cookies, meta={'proxy': proxy, 'manga_no': manga_no, 'chapter_no': chapter_no, 'manga_name': manga_name, 'chapter_name': chapter_name, 'manga_save_folder': manga_save_folder, 'data': data, 'current_page': current_page, 'page_count': page_count}, callback=self.parse_page_ext2)

    def parse_page_ext2(self, response):
        """
        拿到跟图片地址有关的js
        """
        manga_no = response.meta['manga_no']
        chapter_no = response.meta['chapter_no']
        manga_name = response.meta['manga_name']
        chapter_name = response.meta['chapter_name']
        manga_save_folder = response.meta['manga_save_folder']
        data = response.meta['data']
        current_page = response.meta['current_page']
        page_count = response.meta['page_count']
        try_repr = response.meta.setdefault('try_repr', False)
        proxy = response.meta['proxy']
        # 返回一段js代码
        # jsbeautifier 1.7.5解码
        packed_js = response.body
        try:
            if try_repr == True:
                packed_js = repr(packed_js)
            unpacked_js = packer.unpack(packed_js).replace("\\'", "'")

            # 解码后找出图片路径
            cid = re.findall('var cid=(.*?);', unpacked_js)[0]
            key = re.findall("var key='(.*?)';", unpacked_js)[0]
            pix = re.findall('var pix="(.*?)";', unpacked_js)[0]
            pvalue = re.findall('var pvalue=\[(.*?)\];', unpacked_js)[0]
            pvalue = pvalue.replace('"', '')
            if (',' in pvalue):
                pvalue = pvalue.split(',')
            else:
                pvalue = [pvalue, ]
            image_url = pix + pvalue[0] + '?cid=' + cid + '&key=' + key + '&uk='

            item = Dm5Item()
            item['imgurl'] = image_url
            item['imgname'] = image_url.split('/')[-1].split('_')[0].zfill(3) + '.jpg'
            # 不使用pipeline下载需要特殊处理下载地址
            item['imgfolder'] = settings.get('IMAGES_STORE') + '/' + manga_save_folder + '/' + chapter_no
            # 准备下载图片
            image_save_path = os.path.join(item['imgfolder'], item['imgname'])

            # 跳过已经下载的图片
            if not os.path.exists(image_save_path):
                if not os.path.exists(item['imgfolder']):
                    os.makedirs(item['imgfolder'])
                print('当前页面', manga_name, chapter_no, chapter_name, current_page, '/', page_count)
                host = image_url.split('//')[1].split('/')[0]
                headers = {'Host': host,
                           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0',
                           'Accept': '*/*',
                           'Connection': 'close',
                           'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.5,en-US;q=0.3',
                           'Accept-Encoding': 'gzip, deflate',
                           'Referer': 'http://www.dm5.com/m' + str(data['cid']) + '-p' + str(current_page) + '/',
                           'DNT': '1',
                           }
                # print 1111, image_url

                # 使用urllib2下载图片
                # req = urllib2.Request(image_url, headers=headers)
                # res = urllib2.urlopen(req)
                # # print res
                # with open(image_save_path, 'wb') as f:
                #     f.write(res.read())

                # 使用requests下载图片
                # res = requests.get(image_url, headers=headers, proxies=proxyDict)
                # with open(image_save_path, 'wb') as f:
                #     f.write(res.content)

                # 使用自定义的imagepipeline下载图片
                item['imgheaders'] = headers
                item['imgproxy'] = proxy
                yield item

            # 准备访问下一页
            current_page += 1
            if int(current_page) > int(page_count):
                return
            data['page'] = current_page

            pages_url = 'http://www.dm5.com/m' + str(data['cid']) + '/chapterfun.ashx?' + urllib.parse.urlencode(data)
            yield scrapy.Request(pages_url, cookies=cookies, headers={'Referer': 'http://www.dm5.com/m' + str(data['cid']) + '/'},  meta={'proxy': proxy, 'manga_no': manga_no, 'chapter_no': chapter_no, 'manga_name': manga_name, 'chapter_name': chapter_name, 'manga_save_folder': manga_save_folder, 'data': data, 'current_page': current_page, 'page_count': page_count}, callback=self.parse_page_ext2)
        except UnpackingError as e:
            print('解包js错误 访问地址', response.url)
            print('当前页面', current_page)
            print('返回内容', response.body)
            if try_repr == True:
                # 准备访问下一页
                current_page += 1
                if int(current_page) > int(page_count):
                    return
                data['page'] = current_page

                pages_url = 'http://www.dm5.com/m' + str(data['cid']) + '/chapterfun.ashx?' + urllib.parse.urlencode(data)
                yield scrapy.Request(pages_url, cookies=cookies, headers={'Referer': 'http://www.dm5.com/m' + str(data['cid']) + '/'},  meta={'proxy': proxy, 'manga_no': manga_no, 'chapter_no': chapter_no, 'manga_name': manga_name, 'chapter_name': chapter_name, 'manga_save_folder': manga_save_folder, 'data': data, 'current_page': current_page, 'page_count': page_count}, callback=self.parse_page_ext2)
            else:
                yield scrapy.Request(response.url, cookies=cookies, meta={'proxy': proxy, 'manga_no': manga_no, 'chapter_no': chapter_no, 'manga_name': manga_name, 'chapter_name': chapter_name, 'manga_save_folder': manga_save_folder, 'data': data, 'current_page': current_page, 'page_count': page_count, 'try_repr': True}, callback=self.parse_page_ext2, dont_filter=True)
