### Dou_Vacancies Scraping
In this project, we performed web scraping to collect job postings data 
related to Python development roles. The extracted information includes 
the job title, required skills, and the experience level for each position. 


## Features
# Product Scraping: 
The scraper collects the following data for each product:
- Position Name
- Experience
- Skills

# Categories Scraped:
The scraper targets only one category:
- Python
from source:
- https://jobs.dou.ua/

# Technical Requirements:
- python 3.11+
- Scrapy
- Selenium
- json
- matplotlib
- pandas

## Installation

Follow these steps to set up and run the project locally:

- Clone the repository to your local machine:
```bash
git clone https://github.com/struhanets/jods-resource-scraping.git
cd jods-resource-scraping
```
- Create a virtual environment for Python dependencies:
```bash
python -m venv venv
```
- Activate the virtual environment:
```bash
venv\Scripts\activate #for Windows
source venv/bin/activate #for macOS/Linux
```
- Install the required dependencies:
```bash
pip install -r requirements.txt
```
- start parsing proces in terminal
```bash
scrapy crawl products
```
For analysing data
- open vacancies_analyse.ipynb file, and run all of cells
