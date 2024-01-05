import httpx
from selectolax.parser import HTMLParser

url = ('https://www.welcometothejungle.com/fr/companies/mp-data/jobs/data-engineer-transport_boulogne-billancourt?q'
       '=6b9bc2cfac1437f82bba5384be22f6cc&o=9132eb47-99ff-44f2-809b-f0819ee9671d')
headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/120.0.0.0 Safari/537.36"}

resp = httpx.get(url, headers=headers)
html = HTMLParser(resp.text)

# Utilisation d'un selecteur CSS sur les classes pour retrouver les éléments voulus
job_title = html.css_first('.sc-empnci.cYPTxs.wui-text').text()
contract_type = html.css_first('div[variant="default"][w="fit-content"].sc-fKWMtX.dWzFoC').text()
company = html.css_first('.sc-empnci.hmOCpj.wui-text').text()
city = html.css_first('.sc-1eoldvz-0.bZJPQK').text()
salary_element = html.css_first('.sc-bXCLTC.kJcLKT').text()
try:
    salary = int(salary_element)
except ValueError:
    salary = None


print(job_title, contract_type, company, city, salary)

