# SHELL := /bin/bash

PATH_JS = "./autozygosity/static/js"
PATH_CSS = "./autozygosity/static/css"

all:
	java -jar ./misc/yui/build/yuicompressor-2.4.7.jar --charset utf-8 --type js  $(PATH_JS)/site.js   > $(PATH_JS)/site.min.js
	java -jar ./misc/yui/build/yuicompressor-2.4.7.jar --charset utf-8 --type css $(PATH_CSS)/site.css > $(PATH_CSS)/site.min.css
