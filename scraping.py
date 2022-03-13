
# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt
import numpy as np

def scrape_all():
    # Initiate headless driver for deployment
    executable_path= {'executable_path': ChromeDriverManager().install()}
    browser= Browser('chrome', **executable_path, headless=True)

    # run scraping functions
    news_title, news_p= mars_news(browser)

    hemisphere_image_urls = more_mars_img(browser)

    # store results in dictionary
    data = {
        'news_title': news_title,
        'news_paragraph': news_p,
        'featured_image': feature_image(browser),
        'facts': mars_facts(),
        'hemispheres': hemisphere_image_urls,
        'last_modified': dt.datetime.now()
    }

    # Stop webdriver and return data
    browser.quit()
    return data

# ### Nasa website

def mars_news(browser):
    # Visit the mars nasa news site
    url= 'https://redplanetscience.com'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_test', wait_time=1)


    # parse website as html
    html = browser.html
    news_soup= soup(html, 'html.parser')
    
    try:
        slide_elem= news_soup.select_one('div.list_text')

        # find first tile
        new_titles= slide_elem.find('div', class_= 'content_title').get_text()


        # use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    except AttributeError:
        return None, None
    
    return new_titles, news_p


# ### Featured image

def feature_image(browser):
    # visit url

    url= 'https://spaceimages-mars.com'

    browser.visit(url)


    # Find and click the full image button
    full_image_elem= browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup

    html = browser.html
    img_soup = soup(html, 'html.parser')

    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url= f'{url}/{img_url_rel}'
    
        
    return img_url

    
# ### Mars Facts

def mars_facts():    
    # Add try/except for error handling
    try:
        # use 'read_html" to scrape the facts table into a dataframe
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
    except BaseException:
        return None
    
    # Assign columns and set index of dataframe
    df.columns=['description', 'Mars', 'Earth']
    df.set_index('description', inplace=True)
    df

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html()

# More mars imgs

def more_mars_img(browser):
    # 1. Use browser to visit the URL 
    url = 'https://marshemispheres.com/'

    browser.visit(url)

    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    # Navigate to page, parse the resulting html with soup

    for x in range(4):
        # Navigate to page
        browser.links.find_by_partial_text('Hemisphere Enhanced')[x].click()
        html = browser.html
        
        #  parse the resulting html with soup
        img_soup= soup(html, 'html.parser')
        
        # Get image url and title
        img_url= img_soup.find('img', class_= 'wide-image').get('src')
        title= img_soup.find('h2', class_= 'title').getText()
        
        # append dic to list
        hemisphere_image_urls.append({'img_url': f'https://marshemispheres.com/{img_url}',
                                'title': title})
        # back to index
        browser.links.find_by_partial_text('Back').click()

    return hemisphere_image_urls

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())
