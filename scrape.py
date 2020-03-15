import requests
from bs4 import BeautifulSoup
import json
from requests_html import HTMLSession
import re
from firebase import firebase

firebase = firebase.FirebaseApplication(
    'https://ns-ng-challenge-app.firebaseio.com/', 
    None
)

session = HTMLSession()

data = []
remove = [",", "Kitas", "Bet", "kuris", "miestas", "\u20ac"]

def removeUnnessery(var):
    edited_string = var.split()
    final_list = [word for word in edited_string if word not in remove]
    var = ' '.join(final_list)
    return var

for num in range(1, 3):
    page = str(num)
    url = "https://www.cvbankas.lt/?page="+page
    print(url)
    responce = session.get(url)
    if responce is not None:
        soup = BeautifulSoup(responce.content, 'html.parser')
        results = soup.find('div', id='job_ad_list')

        job_elems = results.find_all('article', class_='list_article list_article_rememberable jobadlist_list_article_rememberable jobadlist_article_vip')
        for job_elem in job_elems:
            title_elem = job_elem.find('h3', class_='list_h3')
            company_elem = job_elem.find('span', class_='dib mt5')
            salary_elem = job_elem.find('span', class_='salary_amount')
            location_elem = job_elem.find('span', class_='list_city')

            address = job_elem.find('a', class_="list_a can_visited list_a_has_logo", href=True)
            job_url = address['href']
            request_address = requests.get(address['href'])
            soup2 = BeautifulSoup(request_address.text, 'html.parser')
            job_address = soup2.find('a', class_='partners_company_info_additional_info_location_url')

            em = soup2.find('div', id="jobad_content")
            email = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.", em.text, re.I)

            if None in (title_elem, company_elem, salary_elem, location_elem, job_address, job_url, email):
                continue
            title = title_elem.text.strip()
            company = company_elem.text.strip()
            salary = salary_elem.get_text()
            location = location_elem.text.strip()
            city_location = job_address.get_text()
            removeUnnessery(salary)

            data.append(
                {
                    "title": title, 
                    "company": company, 
                    "salary": salary, 
                    "location": location, 
                    "address": city_location,
                    "email": email,
                    "url": job_url
                }
            )
               
for job in data:
    result = firebase.post('/jobs', job)
    print(result)

with open("job-list.json", "w", encoding='utf-8') as write_file:
    json.dump(data, write_file, ensure_ascii=False, indent=4)
