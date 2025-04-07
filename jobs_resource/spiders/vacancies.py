import time

import scrapy
import spacy
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from scrapy.selector import Selector
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


nlp = spacy.load("en_core_web_sm")

TECH_STACK = {
    "Python", "Django", "Flask", "FastAPI", "PostgreSQL", "MongoDB", "MySQL",
    "Git", "Docker", "Kubernetes", "AWS", "GCP", "Azure", "Redis", "Celery",
    "RabbitMQ", "DRF", "GraphQL", "REST", "CI/CD", "Linux", "PyTorch", "Pandas",
    "NumPy", "React", "JavaScript", "HTML", "CSS", "SQL", "API", "asyncio", "OOP",
}

class VacanciesSpider(scrapy.Spider):
    name = "vacancies"
    allowed_domains = ["jobs.dou.ua"]
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

    def extract_skills_from_text(self, text: str, tech_stack: set) -> list:
        found_skills = []
        lowered_text = text.lower()
        for tech in tech_stack:
            if tech.lower() in lowered_text:
                found_skills.append(tech)
        return found_skills



    def parse_vacancy(self, response, experience):

        text_blocks = response.css(".vacancy-section").xpath(".//text()").getall()
        full_text = " ".join(text_blocks).strip()

        skills = self.extract_skills_from_text(full_text, TECH_STACK)

        item_data = {
            "name": response.css(".l-vacancy > h1::text").get(),
            "experience": experience,
            "skills": skills

        }
        yield item_data

    def closed(self, reason):
        self.driver.close()
