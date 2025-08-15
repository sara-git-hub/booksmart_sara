from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd


class BooksToScraper:
    def __init__(self, driver_path,headless=True):
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless")
        self.driver = webdriver.Chrome(service=Service(driver_path))
        self.wait = WebDriverWait(self.driver, 10) 

    def scrape_books(self):
        book_data = []
        try:
            page_number = 1
            self.driver.get("http://books.toscrape.com/")
            
            while True:
                print(f"Scraping page {page_number}...")
                books = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article.product_pod")))
                
                # extraire les URLs des livres
                book_urls = [b.find_element(By.CSS_SELECTOR, "h3 a").get_attribute("href") for b in books]
                
                # parcourir les URLs et extraire les informations
                for url in book_urls:
                    self.driver.get(url)
                    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1")))
                    
                    book_data.append({
                        "titre": self.get_text("h1", "Unknown Title"),
                        "prix": self.get_text(".price_color", "Unknown Price"),
                        "image_url": self.get_attr(".item img", "src", "No Image"),
                        "rating": self.get_rating(),
                        "stock": self.get_text(".availability", "Unknown Availability").strip(),
                        "description": self.get_text("#product_description + p", "No description available")
                    })
                    self.driver.back()
                
                # aller à la page suivante
                try:
                    next_button = self.driver.find_element(By.CSS_SELECTOR, "li.next a")
                    next_button.click()
                    page_number += 1
                except:
                    print("No more pages.")
                    break
        # gerer les exceptions
        finally:
            self.driver.quit()
            return pd.DataFrame(book_data)
    
    # recuperer le texte d'un élément
    def get_text(self, selector, default):
        try:
            return self.driver.find_element(By.CSS_SELECTOR, selector).text
        except:
            return default
    
    # recuperer un attribut d'un élément
    def get_attr(self, selector, attr, default):
        try:
            return self.driver.find_element(By.CSS_SELECTOR, selector).get_attribute(attr)
        except:
            return default

    # recuperer la note d'un livre
    def get_rating(self):
        try:
            rating_element = self.driver.find_element(By.CSS_SELECTOR, "p[class*='star-rating']")
            return rating_element.get_attribute("class").split()[-1]
        except:
            return "Unknown Rating"
        