@REM @Author: Zengjq
@REM @Date:   2018-10-06 09:27:31
@REM @Last Modified by:   Zengjq
@REM Modified time: 2019-03-05 07:04:18
@echo off
set /p id="Enter ID: "
scrapy crawl dm5 -a no=%id%
pause()