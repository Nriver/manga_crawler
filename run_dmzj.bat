@REM @Author: Zengjq
@REM @Date:   2018-10-06 09:27:31
@REM @Last Modified by:   Zengjq
@REM Modified time: 2020-05-27 21:56:02
@echo off
set /p id="Enter ID: "
scrapy crawl dmzj -a no=%id%
pause()