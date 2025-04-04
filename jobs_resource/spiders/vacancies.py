import re
import time

import scrapy
import spacy
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from scrapy.selector import Selector
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


nlp = spacy.load("en_core_web_sm")

class VacanciesSpider(scrapy.Spider):
    name = "vacancies"
    allowed_domains = ["jobs.dou.ua"]
    # url = "https://jobs.dou.ua/vacancies/?category=Python"
    expirience_levels = {
        "trainee": "&exp=0-1",
        "junior": "&exp=1-3",
        "middle": "&exp=3-5",
        "senior": "&exp=5plus"
    }

    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless=new")
        self.driver = webdriver.Chrome(options=chrome_options)


    def start_requests(self):
        for exp_name, exp_value in self.expirience_levels.items():
            get_link = f"https://jobs.dou.ua/vacancies/?category=Python{exp_value}"
            self.driver.get(get_link)

            while True:
                try:
                    WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, ".more-btn>a"))
                    )
                    self.driver.execute_script("""
                        const btn = document.querySelector(".more-btn>a");
                        if (btn) {
                            btn.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));
                            btn.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }));
                        }
                    """)
                    time.sleep(2)
                except:
                    break
            page_source = self.driver.page_source
            response = Selector(text=page_source)

            yield from self.parse(response, exp_name)


    def parse(self, response, experience):
        vacancies_links = response.css(".l-vacancy > .title>a::attr(href)").getall()
        for link in vacancies_links:
            yield scrapy.Request(link, callback=self.parse_vacancy, cb_kwargs={"experience": experience})

    def extract_quali_block(self, text):
        match = re.search(r"Qualifications | Що очікуємо від тебе | Requirements | Вимоги | Skills", text, re.IGNORECASE)

        if match is not None:
            return match.group()
        return text


    def get_keywords(self, text):
        doc = nlp(text)
        keywords = set()
        for token in doc:
            if token.pos_ in ["PROPN", "NOUN"] and token.is_alpha:
                keywords.add(token.text)

        return keywords


    def parse_vacancy(self, response, experience):

        full_text = " ".join(response.css("div.vacancy-section ::text").getall()).strip()

        requirements = self.extract_quali_block(full_text)

        skills = self.get_keywords(requirements)

        item_data = {
            "name": response.css(".l-vacancy > h1::text").get(),
            "experience": experience,
            # "skills": skills

        }
        yield item_data

    def closed(self, reason):
        self.driver.close()
