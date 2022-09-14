"""
projekt_3.py: třetí projekt do Engeto Online Python Akademie
author: Miroslav Zelený
email: m.zeleny@volny.cz
discord: Mirek Z.
"""

import sys

url = sys.argv[1]
nazev_souboru = sys.argv[2]

import requests
import csv
import unicodedata
from pprint import pprint
from bs4 import BeautifulSoup

# url = "https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103"
# nazev_souboru="vysledky_Prostejov.csv"

print(f"Stahuji data z webu {url} a ukládám do souboru {nazev_souboru}...")

def main():
    soup=zpracuj_odpoved_serveru(url)
    list_obci = seznam_obci(soup)
    list_kodu_obci=kody_obci(soup)
    list_linku_obci = linky_obci(soup)
    pocet_obci = len(list_obci)
    stazene_stranky_obci=stahni_obce(pocet_obci,list_linku_obci)
    volici=pocty_volicu(stazene_stranky_obci,pocet_obci)
    pocet_obalek=obalky(stazene_stranky_obci,pocet_obci)
    valid_hlasy=platne_hlasy(stazene_stranky_obci,pocet_obci)
    seznam_stran=strany(stazene_stranky_obci)
    vsechny_hlasy=hlasy(stazene_stranky_obci,pocet_obci)
    radky=radky_csv(list_kodu_obci,list_obci,volici,pocet_obalek,valid_hlasy,vsechny_hlasy,seznam_stran)
    zapis_do_csv(radky,seznam_stran,list_obci)

def zpracuj_odpoved_serveru(url):
    odpoved_serveru = requests.get(url)
    html_doc = odpoved_serveru.text
    return BeautifulSoup(html_doc, 'html.parser')

def seznam_obci(soup):
    obce = zpracuj_odpoved_serveru(url).find_all('td',{"class":"overflow_name"})
    list_obci=[]
    for result in obce:
        list_obci.append(result.text)
    return list_obci

def kody_obci(soup):
    kod_obci = zpracuj_odpoved_serveru(url).find_all('td', {"class": "cislo"})
    list_kodu_obci=[]
    for result in kod_obci:
        list_kodu_obci.append(result.text)
    return list_kodu_obci

def linky_obci(soup):
    linky_obci = zpracuj_odpoved_serveru(url).find_all('td', {"class": "cislo"})
    list_linku_obci = []
    for http in linky_obci:
        a = http.find("a")
        href = a.get("href")
        list_linku_obci.append("https://volby.cz/pls/ps2017nss/"+href)
    return list_linku_obci

def stahni_obce(pocet_obci,list_linku_obci):
    stazene_stranky_obci=[]
    for i in range(pocet_obci):
        link=list_linku_obci[i]
        stazene_stranky_obci.append(zpracuj_odpoved_serveru(link))
    return stazene_stranky_obci

def vymaz_mezery(string):
    return "".join(string.split())

def pocty_volicu(stazene_stranky_obci,pocet_obci):
    pocty_volicu=[]
    for i in range(pocet_obci):
        pocty_volicu.append(stazene_stranky_obci[i].find('td', {"headers":"sa2"}).text)
        pocty_volicu[i]=unicodedata.normalize("NFKD", pocty_volicu[i])
        pocty_volicu[i]=vymaz_mezery(pocty_volicu[i])
        pocty_volicu[i] = int(pocty_volicu[i])
    return pocty_volicu

def obalky(stazene_stranky_obci, pocet_obci):
    obalky=[]
    i = 0
    for i in range(pocet_obci):
        obalky.append(stazene_stranky_obci[i].find('td', {"headers":"sa3"}).text)
        obalky[i] = unicodedata.normalize("NFKD", obalky[i])
        obalky[i] = vymaz_mezery(obalky[i])
    return obalky

def platne_hlasy(stazene_stranky_obci,pocet_obci):
    platne_hlasy = []
    i = 0
    for i in range(pocet_obci):
        platne_hlasy.append(stazene_stranky_obci[i].find('td', {"headers": "sa6"}).text)
        platne_hlasy[i] = unicodedata.normalize("NFKD", platne_hlasy[i])
        platne_hlasy[i] = vymaz_mezery(platne_hlasy[i])
        platne_hlasy[i] = platne_hlasy[i]
    return platne_hlasy

def strany(stazene_stranky_obci):
    strany = []
    strany_filtr=[]

    strany=stazene_stranky_obci[0].find_all('td', {"class":"overflow_name"})

    for result in strany:
        strany_filtr.append(result.text)
    for j in range(len(strany)):
        strany[j]=strany_filtr[j]
    strany_filtr.clear()
    # print("strany", strany)
    return strany

def hlasy(stazene_stranky_obci,pocet_obci):
    hlasy_pom = []
    hlasy = []
    hlasy_filtr = []

    for i in range(pocet_obci):
        hlasy_pom.append(stazene_stranky_obci[i].find_all('td', {"headers": "t1sa2 t1sb3"}))
        hlasy_pom.append(stazene_stranky_obci[i].find_all('td', {"headers": "t2sa2 t2sb3"}))
        for result in hlasy_pom[1]:
            hlasy_pom[0].append(result)
        # del hlasy_pom[1]
        del hlasy_pom[0][-1]
        hlasy.append(hlasy_pom[0])
        hlasy_pom.clear()

        for result in hlasy[i]:
            result = result.text
            result = str(result)
            result = unicodedata.normalize("NFKD", result)
            result = vymaz_mezery(result)
            hlasy_filtr.append(result)

        for k in range(len(hlasy[0])):
            hlasy[i][k] = hlasy_filtr[k]
        hlasy_filtr.clear()
    return hlasy

def radky_csv(list_kodu_obci,list_obci,volici,pocet_obalek,valid_hlasy,vsechny_hlasy,seznam_stran):
    codes=list_kodu_obci
    location=list_obci
    registered=volici
    envelopes=pocet_obalek
    valid=valid_hlasy
    hlasy=vsechny_hlasy
    radky=[]
    pomocne_radky = []
    for i in range(len(location)):
        radky.append([])

    for i in range(len(location)):
        pomocne_radky.append(codes[i])
        pomocne_radky.append(location[i])
        pomocne_radky.append(registered[i])
        pomocne_radky.append(envelopes[i])
        pomocne_radky.append(valid[i])

    for j in range(len(location)):
        for i in range(5):
            radky[j].append(pomocne_radky[i])
        del pomocne_radky[0:5]


    for i in range(len(location)):
        for j in range(len(seznam_stran)):
            radky[i].append(hlasy[i][j])
    return radky

def zapis_do_csv(radky,seznam_stran,list_obci):
    strany=seznam_stran
    location = list_obci
    header=["code","location","registered","envelopes","valid"]
    for i in range(len(strany)):
        header.append(strany[i])

    with open(nazev_souboru, mode="w", newline="", encoding='utf-8') as zapis_csv:
        zapis = csv.writer(zapis_csv, delimiter=",")
        zapis.writerow(header)
        for radek in range(len(location)):
            zapis.writerow(radky[radek])

if __name__ == '__main__':
    main()



