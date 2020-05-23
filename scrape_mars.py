import pandas as pd
import pymongo
from splinter import Browser
from bs4 import BeautifulSoup


import time
import requests

def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": r"C:\Users\cpata\Documents\uofa-phx-data-pt-02-2020-u-c\01-Lesson-Plans\12-Web-Scraping-and-Document-Databases\2\Activities\08-Stu_Splinter\Solved\chromedriver"}
    return Browser("chrome", **executable_path, headless=False)


def scrape_info():
    browser = init_browser()
    # create mars_data dict that we can insert into mongo

    #Latest Mars News
    url = "https://mars.nasa.gov/news/"
    browser.visit(url)
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    news_title = soup.find_all('div', class_='content_title')[1].text
    news_p = soup.body.find('div',class_='article_teaser_body').text

    #JPL Mars Space Images - Featured Image
    featured_image_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(featured_image_url)
    html_image = browser.html
    soup = BeautifulSoup(html_image, 'html.parser')
    featured_image_url  = soup.find('article')['style'].replace('background-image: url(','').replace(');', '')[1:-1]
    main_url = 'https://www.jpl.nasa.gov'
 
    featured_image_url = main_url + featured_image_url


    mars_weather_url = 'https://twitter.com/marswxreport?lang=en'
    #  Retrieve page with the requests module
    response = requests.get(mars_weather_url)
    # Create BeautifulSoup object; parse with 'lxml'
    soup2 = BeautifulSoup(response.text, 'lxml')
    
    #make empty list for weather tweets
    weather_tweets = []

    #iterate through soup and get tweet text
    for li in soup2.find_all("li", {"data-item-type": "tweet"}):
        #make empty lists for all available tweets on page
        all_tweets = []
        text_p = li.find("p", class_="tweet-text")
        if text_p is not None:
            all_tweets.append(text_p.get_text()) #from STACKOVERFLOW
            for i in all_tweets: 
                t = []
                t.append(i)
                if any("sol" in s for s in t):
                    weather_tweets.append(i)

    #assign just the first *most current* one to variable 
    mars_current_weather = str(weather_tweets[0])

   
    #Mars Fscts Information
    url = 'https://space-facts.com/mars/'
    tables = pd.read_html(url)
    mars_df=tables[0]
    mars_df.columns=["description","value"]
    mars_df.set_index("description",inplace=True)
    mars_html_table=mars_df.to_html()
    mars_facts_html = mars_html_table.replace('\n','')

    #Mars Hemisphere Images
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    hemi1=soup.find("div",class_='collapsible results')
    hemisphere1=hemi1.find_all('a')
    main_url="https://astrogeology.usgs.gov/"

    hemisphere_image_urls=[]
    for hemi in hemisphere1:
        if hemi.h3:
            title=hemi.h3.text
            link=hemi["href"]
            forward_url=main_url+link
            browser.visit(forward_url)
            html = browser.html
            soup = BeautifulSoup(html, 'html.parser')
            hemi2=soup.find("div",class_= "downloads")
            image=hemi2.ul.a["href"]
            hemi_dict={}
            hemi_dict["title"]=title
            hemi_dict["img_url"]=image
            hemisphere_image_urls.append(hemi_dict)
            browser.back()

    mars_py_dict={
        "mars_news_title": news_title,
        "mars_news_paragraph": news_p,
        "featured_mars_image": featured_image_url,
        "mars_weather": mars_current_weather,
        "mars_facts": mars_facts_html,
        "mars_hemisphers": hemisphere_image_urls
    }

    browser.quit()
    return mars_py_dict