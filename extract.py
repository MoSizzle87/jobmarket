import httpx
from selectolax.parser import HTMLParser

# penser a utiliser une approche asynchrone pour plus de rapidité

url = 'https://www.welcometothejungle.com/fr/companies/sicara/jobs/lead-data-engineer-cdi-sicara-paris_paris'
headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/120.0.0.0 Safari/537.36"}

resp = httpx.get(url, headers=headers)
html = HTMLParser(resp.text)


def get_info(html, selector, str1="", str2="", str3="", str4=""):
    """
    Fonction pour extraire les informations voulues et revoyer None si l'information n'est pas présente dans la page
    :param html: HTML contenant les informations
    :param selector: HTML contenant les informations de variables
    :param str1: Valeur à supprimer
    :param str2: chaine vide pour suppression str1
    :param str3: Valeur à supprimer
    :param str4: chaine vide pour suppression str3
    :return: Texte contenant les informations
    """
    try:
        return html.css_first(selector).parent.text().replace(str1, str2).replace(str3, str4)
    except AttributeError:
        return None


def get_info_no_parent(html, selector, str1="", str2="", str3="", str4=""):
    """
    Fonction pour extraire les informations voulues lorsque nous avons utilisé la balise la plus proche et revoyer
    None si l'information n'est pas présente dans la page
    :param html: HTML contenant les informations
    :param selector: HTML contenant les informations de variables
    :param str1: Valeur à supprimer
    :param str2: chaine vide pour suppression str1
    :param str3: Valeur à supprimer
    :param str4: chaine vide pour suppression str3
    :return: Texte contenant les informations
    """
    try:
        return html.css_first(selector).text().replace(str1, str2).replace(str3, str4)
    except AttributeError:
        return None


# Ciblage de ma balise contenant toutes les données de base de l'offre
contract_elements = html.css_first('.sc-bXCLTC.jlqIpd.sc-fbKhjd.kfysmu.sc-1wwpb2t-5.hexbEF')
# Extraction des données contenues dans la balise
job_title = get_info_no_parent(contract_elements, '.sc-empnci.cYPTxs.wui-text')
contract_type = get_info(contract_elements, '[name="contract"]')
salary = get_info(contract_elements, '[name="salary"]', "Salaire : ")
company = get_info_no_parent(contract_elements, '.sc-empnci.hmOCpj.wui-text')
location = get_info(contract_elements, '[name="location"]')
remote = get_info(contract_elements, '[name="remote"]')
experience = get_info(contract_elements, '[name="suitcase"]', str1="Expérience : ")
education_level = get_info(contract_elements, '[name="education_level"]', str1="Éducation : ")
# pour publication_date l'information figure directement dans la balise j'utilise .attributes
publication_date = contract_elements.css_first('time').attributes['datetime'][0:10]

# Ciblage de ma balise contenant toutes les données de l'entreprise
company_elements = html.css_first('.sc-bXCLTC.dBpdut')
# Extraction des données contenues dans la balise
sector = get_info(company_elements, '[alt="Tag"]')
company_size = get_info(company_elements, '[alt="Department"]', " collaborateurs")
creation_date = get_info(company_elements, '[alt="Date"]', "Créée en ")
address = ", ".join(get_info_no_parent(company_elements, '.sc-ezreuY.iObOsq.sc-boZgaH.fVBQVn.sc-4e9f7k-2.kAeJOl').split(", ")[:2])
average_age_of_employees = get_info(company_elements, '[alt="Birthday"]', str1="Âge moyen : ", str3=" ans")
turnover_in_millions = get_info(company_elements, '[alt="EuroCurrency"]', str1="Chiffre d'affaires : ", str3="M€")
proportion_female = get_info(company_elements, '[alt="Female"]', str1="%")
proportion_male = get_info(company_elements, '[alt="Male"]', str1="%")

wttj_db = {
    'job_title': job_title, 'contract_type': contract_type, 'salary': salary, 'company': company, 'location': location,
    'remote': remote, 'experience': experience, 'education_level': education_level,
    'publication_date': publication_date, 'sector': sector, 'company_size': company_size,
    'creation_date': creation_date, 'address': address, 'average_age_of_employees': average_age_of_employees,
    'turnover_in_millions': turnover_in_millions, 'proportion_female': proportion_female,
    'proportion_male': proportion_male
}

print(wttj_db)
