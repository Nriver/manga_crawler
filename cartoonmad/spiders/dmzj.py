# -*- coding: utf-8 -*-
# @Author: Zengjq
# @Date:   2019-03-04 16:25:03
# @Last Modified by:   Zengjq
# @Last Modified time: 2020-05-27 22:54:46
import scrapy
from cartoonmad.items import DmzjItem
import os
import re
import base64
import json


class DmzjSpider(scrapy.Spider):
    name = 'dmzj'
    # allowed_domains = ['m.dmzj.com', ]
    download_folder = 'dmzj'

    def start_requests(self):
        manga_no = getattr(self, 'no', None)
        manga_url = getattr(self, 'url', None)
        urls = []
        if manga_no != None:
            mangas = manga_no.split(' ')
            for manga in mangas:
                new_url = 'https://m.dmzj.com/info/' + manga_no + '.html'
                if new_url not in urls:
                    urls.append(new_url)
        if manga_url != None:
            mangas = manga_url.split(' ')
            for new_url in mangas:
                if new_url not in urls:
                    urls.append(new_url)
        if (manga_no is None or manga_no == '') and (manga_url == None or manga_url == ''):
            urls = ['https://m.dmzj.com/info/49810.html', ]
            # urls = ['https://m.dmzj.com/info/54366.html', ]

        for url in urls:
            yield scrapy.Request(url, self.parse)

    def parse(self, response):
        # scrapy shell https://m.dmzj.com/info/49810.html
        # 漫画id
        manga_no = response.url.split('/')[-1].split('.')[0]
        manga_name = str(response.css('#comicName::text').extract()[0].strip().replace('?', ''))
        print(manga_name)
        manga_save_folder = os.path.join(self.download_folder, manga_no + '_' + manga_name)

        # 提取章节
        chapter_data = json.loads(re.findall('initIntroData\((.*)\);', str(response.body, response.encoding))[0])[0]
        chapters = chapter_data['data'][::-1]

        # 获取每个章节页面
        for index, chapter in enumerate(chapters):
            chapter_link = 'https://m.dmzj.com/view/%s/%s.html' % (manga_no, chapter['id'])
            chapter_name = chapter['chapter_name'].replace('·', ' ')
            chapter_no = chapter_name
            if chapter_no[0] == '第':
                chapter_no = chapter_no[1:]
            if chapter_no[-1] == '话':
                chapter_no = chapter_no[:-1]

            yield scrapy.Request(chapter_link, meta={'manga_no': manga_no, 'chapter_no': chapter_no, 'manga_name': manga_name, 'chapter_name': chapter_name, 'manga_save_folder': manga_save_folder}, callback=self.parse_page)

    def parse_page(self, response):
        """
        scrapy shell https://m.dmzj.com/view/49810/92507.html
        """
        manga_no = response.meta['manga_no']
        chapter_no = response.meta['chapter_no']
        manga_name = response.meta['manga_name']
        chapter_name = response.meta['chapter_name']
        manga_save_folder = response.meta['manga_save_folder']
        print(2222222)

        image_datas = json.loads(re.findall('mReader.initData\((.*\}),', str(response.body, response.encoding))[0])
        image_urls = image_datas['page_url']
        chapter_pages_count = len(image_urls)
        print(chapter_pages_count)

        # 下载图片
        headers = {
            # "Accept:": "image/webp,image/apng,image/*,*/*;q=0.8",
            # "Accept-Encoding: gzip, deflate,": "br",
            # "Accept-Language:": "zh-CN,zh;q=0.9,ja;q=0.8,en;q=0.7",
            # "Cache-Control:": "no-cache",
            # "Connection:": "keep-alive",
            # "DNT:": "1",
            # "Host:": "images.dmzj.com",
            # "Pragma:": "no-cache",
            "Referer:": response.url,
            "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86": "Safari/537.36",
        }
        item = DmzjItem()
        for index, image_url in enumerate(image_urls):
            print(image_url)
            item['imgurl'] = image_url
            item['imgname'] = str(index + 1).zfill(3) + '.jpg'
            item['imgfolder'] = manga_save_folder + '/' + chapter_name
            item['imgheaders'] = headers
            img_file_path = item['imgfolder'] + '/' + item['imgname']
            # skip files that already downloaded
            # print img_file_path
            if os.path.exists(img_file_path):
                print('skip', img_file_path)
                continue
            if not os.path.exists('download/' + item['imgfolder']):
                print('创建目录')
                os.makedirs(os.getcwd() + '/download/' + item['imgfolder'])
            yield item
