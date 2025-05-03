import scrapy
from urllib.parse import urlparse, parse_qs
from scrapy_splash import SplashRequest


class FlipscrapefullSpider(scrapy.Spider):
    name = "flipscrapefull"
    allowed_domains = ["flipkart.com"]
    start_urls = ["https://www.flipkart.com/search?q=tshirt"]

    def parse(self, response):
        shirts = response.css("div._1sdMkc")

        for shirt in shirts:
            relativeUrl = shirt.css("div.hCKiGj a").attrib["href"]
            shirtUrl = "https://www.flipkart.com" + relativeUrl
            yield scrapy.Request(shirtUrl, callback=self.shirtparse)

        # Handle pagination
        page = response.meta.get('page', 1)
        if page <= 25:
            nextPageUrl = f"https://www.flipkart.com/search?q=tshirt&page={page+1}"
            yield response.follow(nextPageUrl, callback=self.parse, meta={'page': page + 1})

    def shirtparse(self, response):
        # Scraping the product details
        url = response.url
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        pid = query_params.get('pid', [None])[0]

        # Scraping size information from the product page
        sizes = response.css("ul.hSEbzK li.aJWdJI")
        listedSizes = []
        for size in sizes:
            listedSizes.append(size.css("a::text").get())
        clearListedSizes = [item for item in listedSizes if item is not None]
        # for verfication of product avalable
        # oZZD+x

        # Prepare the product data
        product_data = {
            "pid": pid,
            "title": response.css("h1 span.VU-ZEz::text").get(),
            "price": response.css("div.Nx9bqj::text").get(),
            "rating": response.css("div.XQDdHH::text").get(),
            "sizesListed": clearListedSizes,
            "imgUrl": response.css("img._53J4C-").attrib["src"],
            "url": url,
        }

        # Use the PID to construct the size chart URL and request the size chart
        size_chart_url = f"https://www.flipkart.com/rv/sizechart?pid={pid}"
        yield SplashRequest(size_chart_url, callback=self.parse_size_chart, 
                            args={'viewport': '411x731', 'wait': 2, 'timeout': 30}, meta={'product_data': product_data})

    def parse_size_chart(self, response):
        # Parsing the size chart data
        pid = response.meta.get('product_data')['pid']
        sizeChartRows = response.css(".LkzXxD tbody tr._1MdUKU")

        sizes = {}

        for row in sizeChartRows:
            size = row.css('td._2uOdGc::text').get()
            chest = row.css('td._3mlAv4:nth-child(2)::text').get()
            shoulder = row.css('td._3mlAv4:nth-child(4)::text').get()
            length = row.css('td._3mlAv4:nth-child(5)::text').get()
            sleeve_length = row.css('td._3mlAv4:nth-child(6)::text').get()

            sizes[size] = {
                "chest": chest,
                "shoulder": shoulder,
                "length": length,
                "sleeve-length": sleeve_length
            }

        # Combine the product data with the size chart
        product_data = response.meta.get('product_data')
        product_data["size-chart"] = sizes

        # Yield the combined data
        yield product_data
