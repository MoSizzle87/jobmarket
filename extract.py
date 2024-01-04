import httpx
from selectolax.parser import HTMLParser

url = 'https://www.welcometothejungle.com/fr/companies/mp-data/jobs/data-engineer-transport_boulogne-billancourt?q=6b9bc2cfac1437f82bba5384be22f6cc&o=9132eb47-99ff-44f2-809b-f0819ee9671d'
headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/120.0.0.0 Safari/537.36"}

resp = httpx.get(url, headers=headers)
html = HTMLParser(resp.text)

print(html.css_first("title").text())

