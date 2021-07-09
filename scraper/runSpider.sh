#!/bin/sh

echo =====================================================
echo LISTINGS ARE BEING SCRAPED.  PLEASE WAIT...
echo =====================================================

cd scraper/crawler
[ ! -d "oldData" ] && mkdir oldData
[ -f "amazon.json" ] && mv amazon.json oldData/amazon_$(date +'%m-%d-%Y').json.bkup

#To avoid eating up space, clear up oldest backup after 5 have been made.
if [ $(ls oldData | wc -l) -gt 5 ]
then
	oldestFile="oldData/$(basename $(find oldData -type f -printf '%T+ %p\n' | sort | head -n 1 | awk '{print $2}'))"
	rm $oldestFile
fi

#scrapy crawl amazon -o amazon.json

echo =====================================================
echo LISTINGS HAVE BEEN SCRAPED.  THANK YOU FOR WAITING
echo =====================================================
