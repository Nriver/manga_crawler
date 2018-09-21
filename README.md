# manga_crawler
Download manga from online website with scrapy.
Currently download from https://www.cartoonmad.com/

# how to use
In cmd type follows:
```
scrapy crawl manga -a no=MANGA_ID
```
The MANGA_ID is the id number of the manga on the cartoonmad site.
eg. For manga "Grand Blue", it is 3899, so the command would be like this:
```
scrapy crawl manga -a no=3899
```
