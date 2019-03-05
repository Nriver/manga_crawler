# -*- coding: utf-8 -*-
# @Author: Zengjq
# @Date:   2019-03-04 16:25:03
# @Last Modified by:   Zengjq
# @Last Modified time: 2019-03-05 20:50:31
import scrapy
from scrapy_redis.spiders import RedisSpider
from cartoonmad.items import ComicerItem
import os
import re


class ComicerRedisSpider(RedisSpider):
    name = 'comicer_redis'
    custom_settings = {
        'SCHEDULER': 'scrapy_redis.scheduler.Scheduler',
        'DUPEFILTER_CLASS': 'scrapy_redis.dupefilter.RFPDupeFilter',
        'SCHEDULER_PERSIST': True,
        # 'ITEM_PIPELINES': {
        #     'scrapy_redis.pipelines.RedisPipeline': 400,
        # },
        'REDIS_URL': 'redis://127.0.0.1:6379',
    }
    redis_key = 'comicer_redis:start_urls'
    allowed_domains = ['www.comicer.com', 'ltpic.sfacg.com']
    download_folder = 'comicer'

    def parse(self, response):
        # scrapy shell http://www.comicer.com/comic/9544.html
        # 漫画id
        manga_no = response.url.split('/')[-1].split('.')[0]
        manga_name = unicode(response.css('#intro_l > div.title > h1::text').extract()[0].strip().replace('?', ''))
        manga_save_folder = os.path.join(self.download_folder, manga_no + '_' + manga_name)
        # 提取章节
        chapters = response.css("#play_0 > ul > li > a")
        # 每个章节的页数(暂时不知道)
        # 获取每个章节页面
        for index, chapter in enumerate(chapters):
            chapter_link = 'http://www.comicer.com' + chapter.attrib['href']
            chapter_name = chapter.attrib['title'].replace('·', ' ')
            chapter_no = chapter_name
            if chapter_no[0] == '第':
                chapter_no = chapter_no[1:]
            if chapter_no[-1] == '话':
                chapter_no = chapter_no[:-1]

            yield scrapy.Request(chapter_link, meta={'manga_no': manga_no, 'chapter_no': chapter_no, 'manga_name': manga_name, 'chapter_name': chapter_name, 'manga_save_folder': manga_save_folder}, callback=self.parse_page)

    def parse_page(self, response):
        """
        scrapy shell http://www.comicer.com/comic/9544/234317.html
        """
        manga_no = response.meta['manga_no']
        chapter_no = response.meta['chapter_no']
        manga_name = response.meta['manga_name']
        chapter_name = response.meta['chapter_name']
        manga_save_folder = response.meta['manga_save_folder']
        image_urls = re.findall('var qTcms_S_m_murl_e="(.*)";', response.body)[0].decode('base64').split('$qingtiandy$')
        chapters_pages_count = len(image_urls)
        print chapters_pages_count
        # 下载图片
        item = ComicerItem()
        for image_url in image_urls:
            print image_url
            item['imgurl'] = image_url
            item['imgname'] = image_url.split('/')[-1].split('_')[0].zfill(3) + '.jpg'
            item['imgfolder'] = manga_save_folder + '/' + chapter_name
            img_file_path = item['imgfolder'] + '/' + item['imgname']
            # skip files that already downloaded
            # print img_file_path
            if os.path.exists(img_file_path):
                # print 'skip', img_file_path
                continue
            # print item['imgurl']
            yield item
