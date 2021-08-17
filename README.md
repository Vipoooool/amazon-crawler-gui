This scrapy projects scrapes each product's detail from the amazon search or category url provided.

User can provide the url from GUI built using tkinter.
There are also options available to choose spiders, scraped items dumping location and file format from the GUI.

Install dependencies:
pip install -r requirements.txt

Run a spider through GUI:

python desktop_app.py

Run a spider through command line:

scrapy crawl amazon -o "amazon.json"