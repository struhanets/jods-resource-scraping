import re

import scrapy
import spacy
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


"""
1. Create a spider and connect scrapy-selenium
2. Create unc for scrapping each vacancies urls
3. Create all the vacancies urls using scrapy-func parse_vacancy with next info:
a. name - vacancy title
c. Qualifications - list of vacancies qualifications & required skills
d. experience - range of experience
"""
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

    def start_requests(self):
        for exp_name, exp_value in self.expirience_levels.items():
            get_link = f"https://jobs.dou.ua/vacancies/?category=Python{exp_value}"

            yield SeleniumRequest(
                url=get_link,
                callback=self.parse,
                wait_until=EC.visibility_of((By.CSS_SELECTOR, ".more-btn>a")),
                script="""
                document.querySelector(".more-btn>a").dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));
                document.querySelector(".more-btn>a").dispatchEvent(new MouseEvent('mouseup', { bubbles: true }));
                """,
                cb_kwargs={"experience": exp_name}
            )

    def parse(self, response, experience):
        vacancies_links = response.css(".l-vacancy > .title>a::attr(href)").getall()
        for link in vacancies_links:
            yield scrapy.Request(link, callback=self.parse_vacancy, cb_kwargs={"experience": experience})

    # def extract_quali_block(self, text):
    #     match = re.search(r"Qualifications | Що очікуємо від тебе | Requirements | Вимоги | Skills", text, re.IGNORECASE)
    #
    #     if match is not None:
    #         return match.group()
    #     return text


    # def get_keywords(self, text):
    #     doc = nlp(text)
    #     keywords = set()
    #     for token in doc:
    #         if token.pos_ in ["PROPN", "NOUN"] and token.is_alpha:
    #             keywords.add(token.text)
    #
    #     return keywords


    def parse_vacancy(self, response, experience):

        # full_text = " ".join(response.css("div.vacancy-section ::text").getall()).strip()
        #
        # requirements = self.extract_quali_block(full_text)
        #
        # skills = self.get_keywords(requirements)

        item_data = {
            "name": response.css(".l-vacancy > h1::text").get(),
            "experience": experience,
            # "skills": skills

        }
        yield item_data
