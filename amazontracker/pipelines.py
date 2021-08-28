# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from scrapy.http.request import Request
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline
import pymongo
from urllib.parse import quote_plus

class MongoPipeline:

    collection_name = 'products'

    def __init__(self, host,  port, user, passwd, db_name):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.db_name = db_name

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host = crawler.settings.get('MONGO_HOST', 'localhost'),
            port = crawler.settings.get('MONGO_PORT', '27017'),
            user = crawler.settings.get('MONGO_USER', None),
            passwd = crawler.settings.get('MONGO_PASS', None),
            db_name = crawler.settings.get('MONGO_DB', 'items')
        )

    def open_spider(self, spider):
        mongo_uri = f'mongodb://{self.user}:{quote_plus(self.passwd)}@{self.host}:{self.port}'
        self.client = pymongo.MongoClient(mongo_uri)
        self.db = self.client[self.db_name]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.collection_name].insert_one(ItemAdapter(item).asdict())
        return item

class AmazonImagePipeline(ImagesPipeline):
    # DEFAULT_IMAGES_URLS_FIELD = 'product_image'

    def get_media_requests(self, item, info):
        # print('get_media_requests info:\n %s', info)
        for image_url in item['image_urls']:
            yield Request(image_url, meta={'item': item})

    def item_completed(self, results, item, info):
        # print("item_completed results: %s\n %s", type(results), list(results))
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        adapter = ItemAdapter(item)
        adapter['images'] = image_paths
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        # print("File path request: %s", repr(request))
        item = request.meta.get('item')
        img_base_name = item.get('product_url').split('/')[3]
        img_no = item.get('image_urls').index(request.url)
        ext = request.url.split('.')[-1]
        return f'images/{img_base_name}-{img_no}.{ext}'