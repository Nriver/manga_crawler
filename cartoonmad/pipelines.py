# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import scrapy
from scrapy.pipelines.images import ImagesPipeline
from cartoonmad.items import Dm5Item


class CartoonmadPipeline(object):

    def process_item(self, item, spider):
        return item


class ImagespiderPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):

        if isinstance(item, Dm5Item):
            print u'下载图片', item['imgurl']
            print u'保存路径', item['imgfolder'], item[imgname]
            yield scrapy.Request(item['imgurl'], headers={'referer': item['imgreferer'], 'DNT': 1, 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}, meta={'name': item['imgname'], 'folder': item['imgfolder']})
        else:

            # 循环每一张图片地址下载，若传过来的不是集合则无需循环直接yield
            if isinstance(item['imgurl'], str):
                yield scrapy.Request(item['imgurl'], meta={'name': item['imgname'], 'folder': item['imgfolder']})
            else:
                for image_url in item['imgurl']:
                    yield scrapy.Request(image_url, meta={'name': item['imgname'], 'folder': item['imgfolder']})

    # 重命名，若不重写这函数，图片名为哈希，就是一串乱七八糟的名字
    def file_path(self, request, response=None, info=None):

        # 提取url前面名称作为图片名。
        image_guid = request.url.split('/')[-1]
        # 接收上面meta传递过来的图片名称
        name = request.meta['name']
        folder = request.meta['folder']
        # 过滤windows字符串，不经过这么一个步骤，你会发现有乱码或无法下载
        # name = re.sub(r'[？\\*|“<>:/]', '', name)
        # # 分文件夹存储的关键：{0}对应着name；{1}对应着image_guid
        # filename = u'{0}/{1}'.format(name, image_guid)
        return folder + '/' + name
