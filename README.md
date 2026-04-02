# Web-Data-Searcher
Project contains web crawler referenced in resume
Launching the Website
This project includes a small web application built with the Flask framework. It serves as the source of the pages that will be scraped.

WebSearcher Class
The WebSearcher class provides a way to traverse a graph whose nodes are webpages. It extends GraphSearcher and uses a Selenium Chrome WebDriver to load pages, extract links, and collect table data.

I created a WebSearcher by passing in an existing WebDriver instance:

python
ws = scrape.WebSearcher(driver)
Visiting Pages and Discovering Links
  -The visit_and_get_children method treats each node as a URL. When called, it should:
  -Use Selenium to load the page.
  -Identify all hyperlinks on the page and return their URLs as the node’s children.
  -Extract any table fragments on the page using pandas.read_html and store them for later use.
Some pages contained extra tables/data, so I sliced/filtered the list of extraced tables 
