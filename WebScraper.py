"""
project_final.py: závěrečný projekt
author: Jaroslav Machovec
email: jaroslavmachovec1@gmail.com
discord: nemam
"""

# Importy
import requests
from bs4 import BeautifulSoup
import argparse

# Funkce pro generování absolutní URL z relativní
def generuj_absolutni_url(hlavni_url, relativni_url):
    if '/' in hlavni_url:
        return hlavni_url[:hlavni_url.rfind('/')] + "/" + relativni_url
    return hlavni_url

# Funkce pro získání názvů politických stran z dané URL
def ziskat_nazvy_stran(url_strany):
    odpoved = requests.get(url_strany)  # Odeslání HTTP GET požadavku
    if odpoved.status_code == 200:  # Kontrola úspěšnosti požadavku
        soup = BeautifulSoup(odpoved.content, 'html.parser')  # Parsování HTML obsahu
        radky = soup.find_all('tr')  # Vyhledání všech řádků tabulky
        nazvy_stran = []
        for radek in radky:
            bunky = radek.find_all("td")  # Vyhledání všech buněk v řádku
            if len(bunky) == 5:  # Pokud řádek obsahuje 5 buněk
                nazev_strany = bunky[1].get_text().strip()  # Získání názvu strany z druhé buňky
                if nazev_strany not in nazvy_stran:
                    nazvy_stran.append(nazev_strany)  # Přidání názvu strany do seznamu
        return nazvy_stran
    else:
        print("Nepodařilo se stáhnout data")
        return []

# Funkce pro zpracování hlavních dat z dané URL
def zpracovat_data(url_hlavni, vystupni_soubor, url_strany):
    odpoved = requests.get(url_hlavni)  # Odeslání HTTP GET požadavku

    if odpoved.status_code == 200:  # Kontrola úspěšnosti požadavku
        soup = BeautifulSoup(odpoved.content, 'html.parser')  # Parsování HTML obsahu
        radky = soup.find_all('tr')  # Vyhledání všech řádků tabulky
        cislo_radku = 0
        with open(vystupni_soubor, 'w', encoding='cp1250') as f:  # Otevření souboru pro zápis
            # Zápis záhlaví CSV souboru
            f.write("Kod oblasti;Nazev oblasti;Registrovani volici;Obalky;Platne hlasy;")
            seznam_stran = ziskat_nazvy_stran(url_strany)  # Získání seznamu názvů stran
            f.write(";".join(seznam_stran))
            f.write("\n")
            for radek in radky:
                bunky = radek.find_all("td")  # Vyhledání všech buněk v řádku

                if len(bunky) >= 2:  # Pokud řádek obsahuje alespoň 2 buňky
                    cislo_radku += 1
                    prvni_bunka = bunky.pop(0)
                    druha_bunka = bunky.pop(0)
                    odkazy = prvni_bunka.find_all("a")  # Vyhledání všech odkazů v první buňce
                    if odkazy:
                        prvni_odkaz = odkazy.pop(0)
                        relativni_url = prvni_odkaz.get('href')  # Získání relativní URL z odkazu
                        druha_url = generuj_absolutni_url(url_hlavni, relativni_url)  # Generování absolutní URL

                        data_radku = prvni_bunka.get_text().strip() + ";" + druha_bunka.get_text().strip()
                        seznam_stran = zpracovat_podrobnosti(druha_url, f, data_radku, cislo_radku, seznam_stran)  # Zpracování podrobností
            if cislo_radku == 1 and seznam_stran:
                f.write(";".join(seznam_stran))
                f.write("\n")
    else:
        print("Nepodařilo se stáhnout data")

# Funkce pro zpracování detailních dat z dané URL
def zpracovat_podrobnosti(druha_url, vystupni_soubor, data_radku, cislo_radku, seznam_stran):
    odpoved = requests.get(druha_url)  # Odeslání HTTP GET požadavku

    if odpoved.status_code == 200:  # Kontrola úspěšnosti požadavku
        soup = BeautifulSoup(odpoved.content, 'html.parser')  # Parsování HTML obsahu
        radky = soup.find_all('tr')  # Vyhledání všech řádků tabulky

        pokracovani_radku = ""
        seznam_hlasu = []
        for radek in radky:
            bunky = radek.find_all("td")  # Vyhledání všech buněk v řádku

            if len(bunky) == 9:  # Pokud řádek obsahuje 9 buněk
                prvni_bunka = bunky.pop(3)
                druha_bunka = bunky.pop(3)
                platne_hlasy_bunka = bunky.pop(5)
                pokracovani_radku = prvni_bunka.get_text().strip() + ";" + druha_bunka.get_text().strip() + ";" + platne_hlasy_bunka.get_text().strip()
            if len(bunky) == 5:  # Pokud řádek obsahuje 5 buněk
                nazev_strany = bunky.pop(1)
                hlasy_strany = bunky.pop(1)
                if cislo_radku == 1:
                    seznam_stran.append(nazev_strany.get_text().strip())  # Přidání názvu strany do seznamu
                seznam_hlasu.append(hlasy_strany.get_text().strip())  # Přidání hlasů strany do seznamu

        # Zápis dat do souboru
        vystupni_soubor.write(data_radku + ";" + pokracovani_radku + ";" + ";".join(seznam_hlasu))
        vystupni_soubor.write("\n")
        return seznam_stran
    else:
        print("Nepodařilo se stáhnout data")
        return seznam_stran

# Hlavní funkce skriptu
def hlavni(hlavni_url, vystupni_soubor, url_strany):
    zpracovat_data(hlavni_url, vystupni_soubor, url_strany)

if __name__ == '__main__':
    # Nastavení argumentů příkazového řádu
    parser = argparse.ArgumentParser(description='Skript pro web scraping')
    parser.add_argument('hlavni_url', type=str, help='URL stránky pro stažení')
    parser.add_argument('vystupni_soubor', type=str, help='Výstupní soubor')
    parser.add_argument('url_strany', type=str, help='URL pro získání názvů stran')
    args = parser.parse_args()
    hlavni(args.hlavni_url, args.vystupni_soubor, args.url_strany)
