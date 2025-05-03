
import scrapy
from urllib.parse import urlparse, parse_qs # to parse url find pid

class FlipscrapeSpider(scrapy.Spider):
    name = "flipscrape"
    allowed_domains = ["flipkart.com"]
    # only work for cloths,shoue,etc which give 40 proguct in total 4 product in row 
    # will not work for mobile phone
    start_urls = ["https://www.flipkart.com/search?q=shirt"]

    def parse(self, response):
        shirts = response.css("div._1sdMkc")

        for shirt in shirts:
            
            relativeUrl = shirt.css("div.hCKiGj a").attrib["href"]
            shirtUrl = "https://www.flipkart.com" + relativeUrl
            yield scrapy.Request(shirtUrl, callback=self.shirtparse)

        #next page
        page = response.meta.get('page', 1)
            
        if page <= 25:
            nextPageUrl = f"https://www.flipkart.com/search?q=shirt&page={page+1}"
            yield response.follow(nextPageUrl, callback=self.parse, meta={'page': page + 1})
    
    def shirtparse(self,response):
        # finding pid 
        url = response.url
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        pid = query_params.get('pid', [None])[0]


        #size prosessing
        sizes = response.css("ul.hSEbzK li.aJWdJI")
        # for verfication of product avalable
        # oZZD+x
        listedSizes = []
        for size in sizes:
            listedSizes.append(size.css("a::text").get())

        yield {
        "pid" : pid,
        "title" : response.css("h1 span.VU-ZEz::text").get(),
        "price" : response.css("div.Nx9bqj::text").get(),
        "rating" : response.css("div.XQDdHH::text").get(),
        "sizesListed" : listedSizes,
        "imgUrl" : response.css("img._53J4C-").attrib["src"],
        "url" : url,


        }
        

