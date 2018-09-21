# -*- coding: utf-8 -*-
# @Author: Zengjq
# @Date:   2018-09-21 12:54:57
# @Last Modified by:   Zengjq
# @Last Modified time: 2018-09-21 17:27:20

import scrapy
from cartoonmad.items import CartoonmadItem
import os
from scrapy.crawler import CrawlerProcess


class ChapterSpider(scrapy.Spider):
    name = 'manga'
    # allowed_domains = ['*.cartoonmad.com']
    download_folder = 'download'

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

        if manga_no is None and manga_url is None:
            urls = ['https://www.cartoonmad.com/comic/3899.html']

        for url in urls:
            yield scrapy.Request(url, self.parse)

    def parse(self, response):
        # with open('tmp.txt', 'wb') as f:
        #     f.write(response.body)
        # 漫画id
        manga_no = response.url.split('/')[-1].split('.')[0]
        # 名称含有中文
        manga_name = unicode(response.css('title::text').extract()[0][:-14])
        manga_save_folder = os.path.join(self.download_folder, manga_no + '_' + manga_name)
        if not os.path.exists(manga_save_folder):
            # 创建多级目录 os.makedirs
            os.makedirs(manga_save_folder)
        chapters = response.css("#info > table a")
        # 页数比较麻烦 selector 怎么取都会取多
        chapters_pages = response.css("#info > table font::text")
        # 每个章节的页数
        chapters_pages_count = []
        # 简单粗暴的处理
        for x in range(len(chapters)):
            page_count = chapters_pages[x].extract()[1:-2]
            chapters_pages_count.append(page_count)

        # 找到图片存储路径
        for index, chapter in enumerate(chapters):
            chapter_link = 'http://www.cartoonmad.com' + response.css("#info > table a::attr(href)")[index].extract()
            chapter_name = chapter.css('::text').extract()[0]
            chapter_no = chapter_name.split(' ')[1]

        #     # 下载图片
        #     # http://web.cartoonmad.com/c37sn562e81/3899/001/010.jpg

        #     item = CartoonmadItem()
        #     for y in range(int(chapters_pages_count[index])):
        #         item['imgurl'] = ['http://web.cartoonmad.com/c37sn562e81/' + manga_no + '/' + chapter_no + '/' + str(y).zfill(3) + '.jpg']
        #         item['imgname'] = str(y).zfill(3) + '.jpg'
        #         item['imgfolder'] = manga_no + '_' + manga_name + '/' + chapter_name
        #         yield item
            yield scrapy.Request(chapter_link, meta={'manga_no': manga_no, 'chapter_no': chapter_no, 'manga_name': manga_name, 'chapter_name': chapter_name, 'chapters_pages_count': chapters_pages_count, 'chapters': chapters}, callback=self.parse_page)

    def parse_page(self, response):
        item = CartoonmadItem()
        manga_no = response.meta['manga_no']
        chapter_no = response.meta['chapter_no']
        manga_name = response.meta['manga_name']
        chapter_name = response.meta['chapter_name']
        chapters_pages_count = response.meta['chapters_pages_count']
        chapters = response.meta['chapters']

        image_url = response.css("img::attr(src)")[7].extract()
        image_url_parts = image_url.split('/')
        image_url_prefix = image_url_parts[0] + '//' + image_url_parts[2] + '/' + image_url_parts[3] + '/'

        for index, chapter in enumerate(chapters):
            chapter_name = chapter.css('::text').extract()[0]
            chapter_no = chapter_name.split(' ')[1]

            # 下载图片
            # http://web.cartoonmad.com/c37sn562e81/3899/001/010.jpg

            item = CartoonmadItem()
            for y in range(int(chapters_pages_count[index])):
                item['imgurl'] = [image_url_prefix + manga_no + '/' + chapter_no + '/' + str(y).zfill(3) + '.jpg']
                item['imgname'] = str(y).zfill(3) + '.jpg'
                item['imgfolder'] = manga_no + '_' + manga_name + '/' + chapter_name
                yield item
