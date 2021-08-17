# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field
from itemloaders.processors import Compose, Join, MapCompose, Identity
from w3lib.html import remove_tags
from scrapy.selector import Selector


def clean_brand(brand):
    return brand.strip().lower().replace('visit the', '').replace('store', '').strip().title()

def clean_attributes(attr):
    attrs_label = Selector(text=attr).xpath('//th//text()').get().strip()
    attrs_value = Selector(text=attr).xpath('//td//text()').get().strip()
    return {attrs_label: attrs_value}

class AmazontrackerItem(Item):
    # define the fields for your item here like:
    product_url = Field()
    product_name = Field()
    product_price = Field()
    product_availability = Field()
    product_dimension = Field()
    product_summary = Field(input_processor=MapCompose(remove_tags, str.strip), output_processor=Join())
    product_description = Field(input_processor=MapCompose(remove_tags, str.strip), output_processor=Join())
    product_safety = Field()
    image_urls = Field(output_processor=Compose(set, list))
    images = Field(output_processor=Identity())
    supplier_name = Field()
    suppliers_list_url = Field()
    brand_name = Field(input_processor=MapCompose(clean_brand))
    product_attributes = Field(input_processor=MapCompose(clean_attributes), output_processor=Compose(lambda x: {k:v for d in x for k,v in d.items()}))
    meta_category = Field(output_processor=Identity())
