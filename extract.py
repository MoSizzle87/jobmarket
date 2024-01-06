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
contract_type = html.css_first('div[variant="default"][w="fit-content"].sc-fKWMtX.dWzFoC').text()
salary = html.css_first('[name="salary"]').parent.text().replace("Salaire : ", "")
company = html.css_first('.sc-empnci.hmOCpj.wui-text').text()
city = html.css_first('.sc-1eoldvz-0.bZJPQK').text()
remote = html.css_first('.sc-edKZPI.iPYksh.wui-icon-font + span').text()
experience = html.css_first('[name="suitcase"]').parent.text().replace("Expérience : ", "")
education_level = html.css_first('[name="education_level"]').parent.text().replace("Éducation : ", "")

print(job_title, contract_type, salary, company, city, remote, experience, education_level, sep='\n')

