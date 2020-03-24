# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import scrapy
from scrapy.pipelines.images import ImagesPipeline
from cartoonmad.items import Dm5Item, CartoonmadItem

# 修复truncated图片
# 针对类似https://www.cartoonmad.com/75566/5531/138/001.jpg
# 这里的Dr.Stone 138话类似的图片格式处理 需要特殊处理
# https://stackoverflow.com/questions/12984426/python-pil-ioerror-image-file-truncated-with-big-images
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True


class CartoonmadPipeline(object):

    def process_item(self, item, spider):
        return item


class ImagespiderPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):

        if isinstance(item, Dm5Item):
            print('下载图片', item['imgurl'])
            print('保存路径', item['imgfolder'], item['imgname'])
            # print u'自定义header', item['imgheaders']
            # print 'proxy', item['imgproxy']
            yield scrapy.Request(item['imgurl'], headers=item['imgheaders'], meta={'proxy': item['imgproxy'], 'name': item['imgname'], 'folder': item['imgfolder']})
        elif isinstance(item, CartoonmadItem):
            print('pipeline 下载图片', item['imgurl'])
            print('下载路径', item['imgfolder'])
            if isinstance(item['imgurl'], str):
                yield scrapy.Request(item['imgurl'], headers=item['imgheaders'], meta={'name': item['imgname'], 'folder': item['imgfolder']})
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
        image_file_path = folder + '/' + name
        print('重命名', image_file_path)
        # dm5 特殊处理
        if any(image_file_path.startswith(x) for x in['download/', 'download\\']):
            image_file_path = image_file_path[9:]
        return image_file_path
