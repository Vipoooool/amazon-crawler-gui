# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from scrapy.http.request import Request
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline

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