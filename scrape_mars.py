from flask import Flask, render_template
import pymongo

conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)

db = client.mars_db
collection = db.scrape_contents

def scrape():
    # dependencies
    from splinter import Browser
    from bs4 import BeautifulSoup
    import pandas as pd

    mars_dict = {}

    # NASA Mars News
    browser = Browser('chrome', executable_path='chromedriver', headless=False)
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    news_titles = soup.find('div', class_='content_title').text
    news_paras = soup.find('div', class_='article_teaser_body').text

    mars_dict['news_titles'] = news_titles
    mars_dict['news_paras'] = news_paras

    # JPL Mars Space Images - Featured Image
    browser = Browser('chrome', executable_path='chromedriver', headless=False)
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    image_urls = soup.find_all('a', class_='fancybox')

    featured_image_url = 'https://www.jpl.nasa.gov' + image_urls[1]['data-fancybox-href']

    mars_dict['featured_image_url'] = featured_image_url

    # Mars Weather
    browser = Browser('chrome', executable_path='chromedriver', headless=False)
    url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(url)

    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    mars_weathers = soup.find_all('div', class_='js-tweet-text-container')

    mars_weather = mars_weathers[0].find('p').text

    mars_dict['mars_weather'] = mars_weather

    # Mars Facts
    url = 'https://space-facts.com/mars/'

    tables = pd.read_html(url)
    tables

    df = tables[0]
    df.columns = ['Description', 'Value']
    df.set_index('Description', inplace=True)

    html_table = df.to_html()
    mars_dict['mars_facts'] = html_table

    df.to_html('./templates/mars_facts.html')

    # Mars Hemispheres
    browser = Browser('chrome', executable_path='chromedriver', headless=False)
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    hemisphere_pages = soup.find_all('div', class_='description')

    hemisphere_image_urls = []

    for hemisphere_page in hemisphere_pages:
        browser = Browser('chrome', executable_path='chromedriver', headless=False)
        page_url = 'https://astrogeology.usgs.gov' + hemisphere_page.find('a', class_='itemLink product-item').get('href')
        browser.visit(page_url)
        
        dict = {}
        html = browser.html
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find('h2', class_='title').text.replace(' Enhanced', '')
        image_url = soup.find('a', text='Sample').get('href')
        dict = {'title': title, 'image_url': image_url}
        hemisphere_image_urls.append(dict)

    mars_dict['hemisphere_image_urls'] = hemisphere_image_urls

    collection.insert_one(mars_dict)

app = Flask(__name__)

@app.route("/scrape")
def scrapeNew():
    collection.remove()
    scrape()
    mars_contents = db.scrape_contents.find_one()
    return render_template('index.html', mars_contents=mars_contents)

@app.route("/")
def home():
    mars_contents = db.scrape_contents.find_one()
    return render_template('index.html', mars_contents=mars_contents)

if __name__ == "__main__":
    app.run(debug=True)