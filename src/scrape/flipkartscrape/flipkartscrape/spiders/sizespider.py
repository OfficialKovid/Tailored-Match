import scrapy
from scrapy_splash import SplashRequest
from scrapy.selector import Selector  # Import Selector to parse the HTML string

class SizeSpider(scrapy.Spider):
    name = "sizespider"

    def start_requests(self):
        url = "https://www.flipkart.com/rv/sizechart?pid=SHTGN5ASEHMCJQE9"
        
        yield SplashRequest(url, callback=self.parse, 
                            args={
                                'viewport': '411x731',  # Use a tuple for the viewport instead of a list
                                'wait': 2
                            })

    def parse(self, response):
        # Print the raw HTML content for debugging
        self.log(f"Response URL: {response.url}")

        # Select the rows containing size information (class "_1MdUKU")
        sizeChartRows = response.css(".LkzXxD tbody tr._1MdUKU")

        sizes = {}

        for row in sizeChartRows:
            # Extract the size name (e.g., M, L, XL)
            size = row.css('td._2uOdGc::text').get()

            # Extract the measurements (chest, shoulder, length, sleeve length)
            chest = row.css('td._3mlAv4:nth-child(2)::text').get()
            shoulder = row.css('td._3mlAv4:nth-child(4)::text').get()
            length = row.css('td._3mlAv4:nth-child(5)::text').get()
            sleeve_length = row.css('td._3mlAv4:nth-child(6)::text').get()

            # Update the sizes dictionary
            sizes[size] = {
                "chest": chest,
                "shoulder": shoulder,
                "length": length,
                "sleeve-length": sleeve_length
            }

        # Yield the result, including size chart data
        yield {
            "title": response.css("._3y4WWE::text").get(),  # Extract the title (size chart name or heading)
            "size-chart": sizes
        }
