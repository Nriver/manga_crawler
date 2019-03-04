# manga_crawler
Download manga from online website with scrapy.
Spider names and the supported sites:

| Spider Name | Website |
| ------ | ------ |
| manga | https://www.cartoonmad.com/ | 
| comicer | http://www.comicer.com/ | 

# how to use
In cmd type follows:
```
scrapy crawl SPIDER_NAME -a no=MANGA_ID
```
The SPIDER_NAME is the spider name for the comic site.
The MANGA_ID is the id number of the manga on the comic site.
eg. To download manga "Grand Blue" from cartoonmad, the command would be like this:
```
scrapy crawl manga -a no=3899
```
