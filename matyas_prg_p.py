"""
Autor: Matyáš Kovanda
e-mail: matyaskovanda@gmail.com
Popis: Stáhne výsledky voleb z dané obce a uloží je do CSV souboru.
"""
import sys
import csv
import requests
from bs4 import BeautifulSoup
def stahni_html(url):
    odpoved = requests.get(url)
    odpoved.encoding = 'utf-8'
    if odpoved.status_code != 200:
        print(f"Chyba při stahování dat z: {url}")
        sys.exit(1)
    return BeautifulSoup(odpoved.text, 'html.parser')
def ziskej_odkazy(soup, base_url):
    odkazy = []
    tabulka = soup.find('table')
    radky = tabulka.find_all('tr')[2:]
    for radek in radky:
        bunky = radek.find_all('td')
        kod = bunky[0].text.strip()
        nazev = bunky[1].text.strip()
        odkaz = base_url + bunky[0].find('a')['href']
        odkazy.append((kod, nazev, odkaz))
    return odkazy
def zpracuj_vysledky(soup):
    registrovani = soup.find('td', headers='sa2').text.strip().replace('\xa0', '').replace(' ', '')
    obalky = soup.find('td', headers='sa3').text.strip().replace('\xa0', '').replace(' ', '')
    platne = soup.find('td', headers='sa6').text.strip().replace('\xa0', '').replace(' ', '')
    strany = soup.find_all('td', class_='overflow_name')
    hlasy = soup.find_all('td', headers=['t1sb3', 't2sb3'])
    vysledky = {}
    for strana, hlas in zip(strany, hlasy):
        jmeno = strana.text.strip()
        pocet = hlas.text.strip().replace('\xa0', '').replace(' ', '')
        vysledky[jmeno] = pocet
    return registrovani, obalky, platne, vysledky
def hlavni():
    if len(sys.argv) != 3:
        print("Použití: python skript.py <URL> <vystupni_soubor.csv>")
        sys.exit(1)
    vstup_url = sys.argv[1]
    vystup_soubor = sys.argv[2]
    zaklad_url = "https://volby.cz/pls/ps2017nss/"
    soup = stahni_html(vstup_url)
    obce = ziskej_odkazy(soup, zaklad_url)
    _, _, prvni_odkaz = obce[0]
    prvni_soup = stahni_html(prvni_odkaz)
    _, _, _, priklad_vysledky = zpracuj_vysledky(prvni_soup)
    strany = list(priklad_vysledky.keys())
    with open(vystup_soubor, mode='w', newline='', encoding='utf-8') as soubor:
        writer = csv.writer(soubor)
        hlavicka = ['kód obce', 'název obce', 'registrovaní', 'obálky', 'platné hlasy'] + strany
        writer.writerow(hlavicka)
        for kod, nazev, odkaz in obce:
            obec_soup = stahni_html(odkaz)
            registrovani, obalky, platne, vysledky = zpracuj_vysledky(obec_soup)
            radek = [kod, nazev, registrovani, obalky, platne] + [vysledky.get(s, '0') for s in strany]
            writer.writerow(radek)
    print(f"Data byla uložena do souboru: {vystup_soubor}")
if __name__ == "__main__":
    hlavni()