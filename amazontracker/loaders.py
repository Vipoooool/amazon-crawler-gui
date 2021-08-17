from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose

class ProductLoader(ItemLoader):
    default_input_processor = MapCompose(str.strip)
    default_output_processor = TakeFirst()
    