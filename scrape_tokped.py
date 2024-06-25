import time
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

def scrape_tokopedia(url) :
    # open product link
    driver = webdriver.Chrome()
    driver.get(url)
    # scroll to a unloaded element
    driver.execute_script("window.scrollBy(0, 2000)")
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # go to review section
    all_review = soup.find_all('a', attrs={'data-testid' : 'btnViewAllFeedback'})
    link_all_review = all_review[0]['href']
    link_all_review = 'https://www.tokopedia.com' + link_all_review
    driver.get(link_all_review)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # get number of pages
    total_pages = soup.find_all('button', attrs={'class' : 'css-bugrro-unf-pagination-item'})
    num_page = 0
    for page in total_pages :
        if not page.text.isdigit() :
            continue
        if int(page.text) > num_page :
            num_page = int(page.text)

    # get all review
    reviews = []
    for i in range (0, num_page-1):
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        toped_reviews = soup.find_all('article', attrs={'class' : 'css-72zbc4'})
        for review in toped_reviews:
            text_review = review.find('span', attrs={'data-testid' : 'lblItemUlasan'}) if not None else "None"
            kendala = review.find("p", attrs={"class" : "css-zhjnk4-unf-heading e1qvo2ff8"}) if not None else "None"
            if text_review is not None : 
                text_review = review.find('span', attrs={'data-testid' : 'lblItemUlasan'}).text
                rating = review.find('div', attrs={'data-testid' : 'icnStarRating'})['aria-label']
                rating = rating.removeprefix('bintang ')
                reviews.append([text_review, rating])
            elif kendala is not None: 
                text_review = review.find('p', attrs={'class' : 'css-zhjnk4-unf-heading e1qvo2ff8'}).text[9:]
                rating = review.find('div', attrs={'data-testid' : 'icnStarRating'})['aria-label']
                rating = rating.removeprefix('bintang ')
                reviews.append([text_review, rating])
        time.sleep(3)
        # click next page  
        try :
            driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Laman berikutnya"]').click()
        except :
            break
        time.sleep(3)

    print(f'Jumlah review : {len(reviews)}')
    review_df = pd.DataFrame(reviews, columns=['review', 'rating'])
    review_df.sort_values(by='rating', ascending=True, inplace=True)
    
    return review_df

    
