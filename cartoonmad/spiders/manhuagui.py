# -*- coding: utf-8 -*-
# @Author: Zengjq
# @Date:   2019-03-04 16:25:03
# @Last Modified by:   Zengjq
# @Last Modified time: 2020-05-27 20:07:47

# 调试用代码1
"""
# scrapy shell

from scrapy import Request
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "zh-CN,zh;q=0.9,ja;q=0.8,en;q=0.7",
    "cache-control": "max-age=0",
    # "cookie": "_ga=GA1.2.692256411.1590490270; _gid=GA1.2.750460053.1590490270; country=US",
    # "dnt": "1",
    # "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36",
}

url = 'https://www.manhuagui.com/comic/19430/'
url = 'https://www.manhuagui.com/comic/26497/'
# url = 'https://www.manhuagui.com/comic/36278/'
# url = 'https://www.manhuagui.com/comic/2807/'

# url = 'https://www.manhuagui.com/comic/36278/497203.html'

req = Request(url, headers=headers)
fetch(req)

response.css(".chapter-list")

chapters = []
for chapter_list in response.css(".chapter-list"):
    for chapter_ul in chapter_list.css('ul'):
        chapters += chapter_ul.css("li")[::-1]

for chapter in chapters:
    print(chapter.css("a")[0].attrib['title'])

"""

# 调试用代码2
"""
import re
import json
import lzstring
import jsbeautifier
import jsbeautifier.unpackers.packer as packer
packer.beginstr = ''
packer.endstr = ''
import requests


def solve_js(html):
    js = '(function' + re.findall('function(.*?)</script>', html)[0]
    encrpyted_js = js.split(',')[-3][1:-15]
    decrypted_js = lzstring.LZString().decompressFromBase64(encrpyted_js)
    original_js = js.split(',')
    original_js[-3] = "'" + decrypted_js + "'.split('|')"
    packed_js = 'eval(' + ','.join(original_js) + ')'
    # print('packed_js', packed_js)
    unpack = packer.unpack(packed_js)
    # print(unpack)
    # js_result = jsbeautifier.beautify(unpack)
    # print('js_result', js_result)
    imgData = re.findall("SMH\.imgData\((.*?)\)\.preInit\(\)\;", unpack)[0]
    res = json.loads(imgData)
    return res


if __name__ == '__main__':
    import requests
    url = 'https://www.manhuagui.com/comic/25190/479516.html'
    url = 'https://www.manhuagui.com/comic/19430/250824.html'
    referer = url
    r = requests.get(url)
    res = solve_js(r.text)
    print(res)
    # with open('第02话.txt', 'r', encoding='utf-8') as f:
    #     res = solve_js(f.read())
    file_download_list = res['files']
    print('图片列表', file_download_list)
    prefix = res['path']
    params = {
        'e': res['sl']['e'],
        'm': res['sl']['m']
    }
    headers = {
        'DNT': '1',
        'Referer': referer,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0',
    }
    print('参数', params)

    # 下载漫画
    # for index, x in enumerate(file_download_list):
    #     image_url = 'https://i.hamreus.com%s%s?e=%s&m=%s' % (prefix, x,  params['e'], params['m'])
    #     print(image_url)
    #     image_save_path = str(index + 1) + '.jpg.webp'
    #     res = requests.get(image_url, headers=headers)
    #     with open(image_save_path, 'wb') as f:
    #         f.write(res.content)
"""

import scrapy
from cartoonmad.items import ManhuaguiItem
import os
import re
import json
import base64
import lzstring
import jsbeautifier
import jsbeautifier.unpackers.packer as packer
from jsbeautifier.unpackers import UnpackingError
packer.beginstr = ''
packer.endstr = ''


def solve_js(html):
    js = '(function' + re.findall('function(.*?)</script>', html)[0]
    encrpyted_js = js.split(',')[-3][1:-15]
    decrypted_js = lzstring.LZString().decompressFromBase64(encrpyted_js)
    original_js = js.split(',')
    original_js[-3] = "'" + decrypted_js + "'.split('|')"
    packed_js = 'eval(' + ','.join(original_js) + ')'
    # print('packed_js', packed_js)
    unpack = packer.unpack(packed_js)
    print(unpack)
    # js_result = jsbeautifier.beautify(unpack)
    # print('js_result', js_result)
    imgData = re.findall("SMH\.imgData\((.*?)\)\.preInit\(\)\;", unpack)[0]
    res = json.loads(imgData)
    print(res['bname'])
    return res


class ManhuaguiSpider(scrapy.Spider):
    name = 'manhuagui'
    # allowed_domains = ['www.manhuagui.com', ]
    # allowed_domains = ['*', ]
    download_folder = 'manhuagui'
    handle_httpstatus_list = [200, 404, 410]

    def start_requests(self):
        manga_no = getattr(self, 'no', None)
        manga_url = getattr(self, 'url', None)
        urls = []
        if manga_no != None:
            mangas = manga_no.split(' ')
            for manga in mangas:
                new_url = 'https://www.manhuagui.com/comic/' + manga_no + '/'
                if new_url not in urls:
                    urls.append(new_url)
        if manga_url != None:
            mangas = manga_url.split(' ')
            for new_url in mangas:
                if new_url not in urls:
                    urls.append(new_url)
        if (manga_no is None or manga_no == '') and (manga_url == None or manga_url == ''):
            urls = ['https://www.manhuagui.com/comic/36278/', ]
            # urls = ['https://www.manhuagui.com/comic/19430/', ]
            # urls = ['https://www.manhuagui.com/comic/26497/', ]
        print('urls', urls)

        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9,ja;q=0.8,en;q=0.7",
            # "cache-control": "max-age=0",
            # "cookie": "_ga=GA1.2.692256411.1590490270; _gid=GA1.2.750460053.1590490270; country=US",
            "dnt": "1",
            "upgrade-insecure-requests": "1",
            "referer": "https://www.manhuagui.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36",
        }

        for url in urls:
            # url = 'http://127.0.0.1:5000/'
            print(url)
            yield scrapy.Request(url, headers=headers, callback=self.parse)

    def parse(self, response):
        # scrapy shell https://www.manhuagui.com/comic/36278/
        #
        # with open('tmp.txt', 'wb') as f:
        #     f.write(response.body)
        #
        print(1111111)
        print(response.status)
        # return
        with open('tmp.txt', 'wb') as f:
            f.write(response.body)
        # # 漫画id
        manga_no = response.url.split('/')[-2]
        manga_name = str(response.css('div.book-title > h1::text').extract()[0].strip().replace('?', ''))
        print('漫画名称', manga_name)
        manga_save_folder = os.path.join(self.download_folder, manga_no + '_' + manga_name)
        # 提取章节
        chapters = []
        # 单话
        # 番外篇
        for chapter_list in response.css(".chapter-list"):
            for chapter_ul in chapter_list.css('ul'):
                chapters += chapter_ul.css("li")[::-1]

        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9,ja;q=0.8,en;q=0.7",
            "cache-control": "max-age=0",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36",
        }

        for index, chapter in enumerate(chapters):
            chapter_link = chapter.css("a")[0].attrib['href']
            if chapter_link.startswith('/'):
                chapter_link = 'https://www.manhuagui.com' + chapter_link
            # chapter_name = chapter.css("span::text")[0].extract()
            chapter_name = chapter.css("a")[0].attrib['title']
            print(chapter_name)
            chapter_no = str(index)

            yield scrapy.Request(chapter_link, headers=headers, meta={'manga_no': manga_no, 'chapter_no': chapter_no, 'manga_name': manga_name, 'chapter_name': chapter_name, 'manga_save_folder': manga_save_folder}, callback=self.parse_page)

            # dirty hack
            # break

    def parse_page(self, response):
        """
        scrapy shell https://www.manhuagui.com/comic/36278/497203.html
        """
        print(222222)
        print(response.status)
        print(response.url)
        # dirty hack
        # return
        manga_no = response.meta['manga_no']
        chapter_no = response.meta['chapter_no']
        manga_name = response.meta['manga_name']
        chapter_name = response.meta['chapter_name']
        manga_save_folder = response.meta['manga_save_folder']

        response_body_str = str(response.body, response.encoding)
        with open(chapter_name + '.txt', 'wb') as f:
            f.write(response.body)
        try:
            image_data = solve_js(response_body_str)
            print(image_data)
        except UnpackingError as e:
            print('解包js错误 访问地址', response.url)
            # print('返回内容', response_body_str)
            return

        file_download_list = image_data['files']
        print('图片列表', file_download_list)
        image_count = image_data['len']
        print('本话图片数', image_count)
        prefix = image_data['path']
        params = {
            'e': image_data['sl']['e'],
            'm': image_data['sl']['m']
        }
        headers = {
            'DNT': '1',
            'Referer': response.url,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0',
        }
        print('参数', params)
        item = ManhuaguiItem()
        for index, x in enumerate(file_download_list):
            image_url = 'https://i.hamreus.com%s%s?e=%s&m=%s' % (prefix, x,  params['e'], params['m'])
            image_save_path = str(index + 1) + '.jpg.webp'
            print(image_url)
            item['imgurl'] = image_url
            item['imgname'] = str(index + 1) + '.jpg.webp'
            item['imgfolder'] = manga_save_folder + '/' + chapter_name
            item['imgheaders'] = headers
            img_file_path = item['imgfolder'] + '/' + item['imgname']
            # skip files that already downloaded
            # print img_file_path
            if os.path.exists(img_file_path):
                continue
            yield item
