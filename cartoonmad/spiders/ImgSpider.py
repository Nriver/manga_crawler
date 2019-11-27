# -*- coding: utf-8 -*-
# @Author: Zengjq
# @Date:   2018-09-21 12:54:57
# @Last Modified by:   Zengjq
# @Last Modified time: 2019-11-27 21:42:26

import scrapy
from cartoonmad.items import CartoonmadItem
import os
from scrapy.crawler import CrawlerProcess


class ChapterSpider(scrapy.Spider):
    name = 'manga'
    allowed_domains = ['cartoonmad.com']
    download_folder = 'cartoonmad'

    custom_settings = {
        'MEDIA_ALLOW_REDIRECTS': True,
    }

    def start_requests(self):
        manga_no = getattr(self, 'no', None)
        manga_url = getattr(self, 'url', None)
        urls = []
        if manga_no != None:
            mangas = manga_no.split(' ')
            for manga in mangas:
                new_url = 'https://www.cartoonmad.com/comic/' + manga_no + '.html'
                if new_url not in urls:
                    urls.append(new_url)
        if manga_url != None:
            mangas = manga_url.split(' ')
            for new_url in mangas:
                if new_url not in urls:
                    urls.append(new_url)

        if (manga_no is None or manga_no == '') and (manga_url == None or manga_url == ''):
            urls = ['https://www.cartoonmad.com/comic/3899.html']

        for url in urls:
            yield scrapy.Request(url, self.parse)

    def parse(self, response):
        # with open('tmp.txt', 'wb') as f:
        #     f.write(response.body)
        # 漫画id
        manga_no = response.url.split('/')[-1].split('.')[0]
        # 名称含有中文
        manga_name = str(response.css('title::text').extract()[0][:-14].strip().replace('?', ''))
        manga_save_folder = os.path.join(self.download_folder, manga_no + '_' + manga_name)

        chapters = response.css("body > table > tr:nth-child(1) > td:nth-child(2) > table > tr:nth-child(4) > td > table > tr:nth-child(2) > td:nth-child(2) > table:nth-child(3) > tr > td a")

        chapters_list = []
        for chapter in chapters:
            chapter_name = chapter.css('::text').extract()[0]
            chapter_no = chapter_name.split(' ')[1]
            chapters_list.append([chapter_name, chapter_no])

        # 页数比较麻烦 selector 怎么取都会取多
        chapters_pages = response.css("body > table > tr:nth-child(1) > td:nth-child(2) > table > tr:nth-child(4) > td > table > tr:nth-child(2) > td:nth-child(2) > table:nth-child(3) > tr > td font::text")
        # 每个章节的页数
        chapters_pages_count = []
        # 简单粗暴的处理
        for x in range(len(chapters)):
            page_count = chapters_pages[x].extract()[1:-2]
            chapters_pages_count.append(page_count)
        # 找到图片存储路径
        for index, chapter in enumerate(chapters):
            chapter_link = 'https://www.cartoonmad.com' + response.css("body > table > tr:nth-child(1) > td:nth-child(2) > table > tr:nth-child(4) > td > table > tr:nth-child(2) > td:nth-child(2) > table:nth-child(3) > tr > td a::attr(href)")[index].extract()
            chapter_name = chapter.css('::text').extract()[0]
            chapter_no = chapter_name.split(' ')[1]

        #     # 下载图片
        #     # https://web.cartoonmad.com/c37sn562e81/3899/001/010.jpg

        #     item = CartoonmadItem()
        #     for y in range(int(chapters_pages_count[index])):
        #         item['imgurl'] = ['https://web.cartoonmad.com/c37sn562e81/' + manga_no + '/' + chapter_no + '/' + str(y).zfill(3) + '.jpg']
        #         item['imgname'] = str(y).zfill(3) + '.jpg'
        #         item['imgfolder'] = manga_no + '_' + manga_name + '/' + chapter_name
        #         yield item
            yield scrapy.Request(chapter_link, meta={'manga_no': manga_no, 'chapter_no': chapter_no, 'manga_name': manga_name, 'chapter_name': chapter_name, 'chapters_pages_count': chapters_pages_count, 'chapters_list': chapters_list, 'manga_save_folder': manga_save_folder}, callback=self.parse_page)

    def parse_page(self, response):
        """
        scrapy shell https://www.cartoonmad.com/comic/469500002025001.html
        scrapy shell https://www.cartoonmad.com/comic/169800012046001.html
        """
        manga_no = response.meta['manga_no']
        chapter_no = response.meta['chapter_no']
        manga_name = response.meta['manga_name']
        chapter_name = response.meta['chapter_name']
        chapters_pages_count = response.meta['chapters_pages_count']
        chapters_list = response.meta['chapters_list']
        manga_save_folder = response.meta['manga_save_folder']

        # image_url = response.css("img::attr(src)")[7].extract()
        # print response.url
        # if 'cartoonmad.com' not in image_url or '/image/panen.png' in image_url:
        #     image_url = response.css("img::attr(src)")[6].extract()
        image_urls = response.css("img::attr(src)").extract()
        image_url = ''

        # https://www.cartoonmad.com/comic/comicpic.asp?file=/4695/000/001
        # https://www.cartoonmad.com/home75378/4695/000/001.jpg
        #
        # https://www.cartoonmad.com/comic/comicpic.asp?file=/3080/001/001&rimg=1
        # https://web3.cartoonmad.com/home13712/3080/001/001.jpg
        image_url_prefix = ''
        is_asp_request = False
        has_suffix = False
        for x in image_urls:
            # new rule
            if 'comicpic.asp' in x:
                is_asp_request = True
                if '&rimg=1' in x:
                    has_suffix = True
                break
            elif 'cartoonmad' in x:
                image_url = x
                image_url_parts = image_url.split('/')
                # print image_url
                # print image_url_parts
                image_url_prefix = image_url_parts[0] + '//' + image_url_parts[2] + '/' + image_url_parts[3] + '/'
                break

        for index, chapter in enumerate(chapters_list):
            chapter_name = chapter[0]
            chapter_no = chapter[1]

            # 下载图片
            # https://web.cartoonmad.com/c37sn562e81/3899/001/010.jpg

            item = CartoonmadItem()
            item['imgfolder'] = manga_save_folder + '/' + chapter_name
            for y in range(1, int(chapters_pages_count[index]) + 1):
                if is_asp_request:
                    item['imgurl'] = 'https://www.cartoonmad.com/comic/comicpic.asp?file=/' + manga_no + '/' + chapter_no + '/' + str(y).zfill(3)
                    if has_suffix:
                        item['imgurl'] += '&rimg=1'
                else:
                    item['imgurl'] = [image_url_prefix + manga_no + '/' + chapter_no + '/' + str(y).zfill(3) + '.jpg']
                print('download image: ', item['imgurl'])
                item['imgname'] = str(y).zfill(3) + '.jpg'
                img_file_path = item['imgfolder'] + '/' + item['imgname']
                # skip files that already downloaded
                # print img_file_path
                if os.path.exists(img_file_path):
                    # print 'skip', img_file_path
                    continue
                headers = {
                    "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Accept-Language": "zh-CN,zh;q=0.9,ja;q=0.8,en;q=0.7",
                    "Connection": "keep-alive",
                    "DNT": "1",
                    "Host": "www.cartoonmad.com",
                    "Referer": response.url,
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36",
                }
                item['imgheaders'] = headers

                yield item
