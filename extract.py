import httpx
from selectolax.parser import HTMLParser

# penser a utiliser une approche asynchrone pour plus de rapidité

url = 'https://www.welcometothejungle.com/fr/companies/sicara/jobs/lead-data-engineer-cdi-sicara-paris_paris'
headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/120.0.0.0 Safari/537.36"}

resp = httpx.get(url, headers=headers)
html = HTMLParser(resp.text)

# Ciblage de ma balise contenant toutes les données de base de l'offre
contract_elements = html.css_first('.sc-bXCLTC.jlqIpd.sc-fbKhjd.kfysmu.sc-1wwpb2t-5.hexbEF')
# Extraction des données contenues dans la balise
job_title = contract_elements.css_first('.sc-empnci.cYPTxs.wui-text').text()
contract_type = contract_elements.css_first('[name="contract"]').parent.text()
salary = contract_elements.css_first('[name="salary"]').parent.text().replace("Salaire : ", "")
company = contract_elements.css_first('.sc-empnci.hmOCpj.wui-text').text()
location = contract_elements.css_first('[name="location"]').parent.text()
remote = contract_elements.css_first('[name="remote"]').parent.text()
experience = contract_elements.css_first('[name="suitcase"]').parent.text().replace("Expérience : ", "")
education_level = contract_elements.css_first('[name="education_level"]').parent.text().replace("Éducation : ", "")
publication_date = contract_elements.css_first('time').attributes['datetime'][0:10]

# Ciblage de ma balise contenant toutes les données de l'entreprise
company_elements = html.css_first('.sc-bXCLTC.dBpdut')
sector = company_elements.css_first('[alt="Tag"]').parent.text()
company_size = company_elements.css_first('[alt="Department"]').parent.text().replace(" collaborateurs", "")
creation_date = company_elements.css_first('[alt="Date"]').parent.text().replace("Créée en ", "")
address = ", ".join(company_elements.css_first('.sc-ezreuY.iObOsq.sc-boZgaH.fVBQVn.sc-4e9f7k-2.kAeJOl').text().split(", ")[:2])
average_age_of_employees = company_elements.css_first('[alt="Birthday"]').parent.text().replace("Âge moyen : ", "")
turnover = company_elements.css_first('[alt="EuroCurrency"]').parent.text().replace("Chiffre d'affaires : ", "")
proporion_female = company_elements.css_first('[alt="Female"]').parent.text()
proporion_male = company_elements.css_first('[alt="Male"]').parent.text()

