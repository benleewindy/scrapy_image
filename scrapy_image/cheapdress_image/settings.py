# Scrapy settings for tutorial project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#
import os

BOT_NAME = 'cheapdress_image'

SPIDER_MODULES = ['cheapdress_image.spiders']
NEWSPIDER_MODULE = 'cheapdress_image.spiders'

ITEM_PIPELINES = ['cheapdress_image.pipelines.CheapDressImagePipeline']

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
IMAGES_STORE = os.path.join(BASE_PATH, "dress")

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'tutorial (+http://www.yourdomain.com)'
