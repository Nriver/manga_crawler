# manga_crawler
Download manga from online website with scrapy.
Spider names and the supported sites:

| Spider Name | Website |
| ------ | ------ |
| manga | https://www.cartoonmad.com/ | 
| comicer | http://www.comicer.com/ | 
| dm5 | http://www.dm5.com | 

# install
install requirements
```
pip install -r requirements.txt
```
If you are on widnows, you need to install pywin32 as well
```
pip install pywin32
```

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

# other features
There is a comicer_redis spider that works as a distributed crawler. Thanks to [scrapy-redis](https://github.com/rmax/scrapy-redis/).