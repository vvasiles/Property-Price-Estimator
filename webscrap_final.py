from bs4 import BeautifulSoup
from csv import writer
import requests
import random
import math
import time

dataset = [] 
# 40,105,280
page1 = 1
start = '1'


def scrape_page(sp):
    
    itemlist = sp.find_all(class_="card-list__item")
    for x in itemlist:
        link = 'https://www.propertyfinder.qa' + x.find('a', class_="card--clickable", href=True)['href']
        location = x.find(class_="card__location").get_text()
        # time.sleep(random.randint(0,5))

        print("Link:", link)
        page = requests.get(link)

        if page == None:
            print(" Connection issue ")
            return

        dta = []
        soup = BeautifulSoup(page.text, 'html.parser')

        # rent
        dta.append(int(soup.find_all(class_ = "property-price")[0].get_text().strip().split("QAR")[0].strip().replace(',','')))
        missing_facts = []
        test = str(soup.find(class_='property-facts'))    #check for missing facts
        if "Property type" not in test: missing_facts.append(1)
        if "Property size" not in test: missing_facts.append(2)
        if "Bedrooms" not in test: missing_facts.append(3)
        if "Bathrooms" not in test: missing_facts.append(4)


        dummy = BeautifulSoup('<li>dummy</li>', 'html.parser').find('li') #dummy fact object added to result set 

        facts = soup.find_all(class_="property-facts__list")
        for x in missing_facts:
            facts.insert(x, dummy)

        for i in range(0, len(facts)):
            
            fac = facts[i].find(class_="property-facts__content")
            if fac == None: dta.append('')
            else:
                facstr = fac.get_text().replace('\n', '').replace(' ','').replace(',','')
                if "sqft" in facstr:
                    dta.append(int(facstr.split('/')[1].split('sqm')[0]))
                else: dta.append(facstr)

        # Getting Amenities
        allam = []
        amenities = soup.find_all(class_="property-amenities__list")
        if len(amenities) == 0:
            dta.append('')
        elif len(amenities) == 1:
            dta.append(str(amenities[0]).split("</svg>")[1].split("</div>")[0].split("\n")[1].strip())
        else:
            dta.append(str(amenities[0]).split("</svg>")[1].split("</div>")[0].split("\n")[1].strip())
            for i in amenities[1:]:
                pl = str(i).split("</svg>")[1].split("</div>")[0].split("\n")[1].strip()
                allam.append(pl)

        dta.append(','.join(allam))  #ammenities

        dta.append(location.split(',')[-2].strip())  #location - only the area - ThePearl/AlWaab ...

        print(" - Data:", dta)

        if 'WholeBuilding' not in dta[1] and 'BulkRent' not in dta[1] and 'Whole Building' not in dta[1] and 'Bulk Rent' not in dta[1]:
           dataset.append(dta)
        else:
            print("Type of building not interested")
            pass


def main():
    prefix ='https://www.propertyfinder.qa/en/search?c=2&l=9&ob=ba&page='
    suffix = '&rp=m'
    page = requests.get(prefix + start + suffix)
    soup = BeautifulSoup(page.text, 'html.parser')

    listk = int(soup.find(class_="property-header__list-count").get_text().replace(' results', ''))
    all_ads = soup.find_all(class_="card-list__item")
    pagek = math.ceil(listk / len(all_ads))


    print("Total number of pages to be scraped:" + str(pagek)+ '\n')



    for pag in range(page1, pagek):
        print("Page:" + str(pag))
        page = requests.get(prefix + str(pag) + suffix)
        soup = BeautifulSoup(page.text, 'html.parser')
        scrape_page(soup)

        if pag % 5 == 0:
            file_name_nr = "Backup_after_" + str(pag) + "_pages.csv"
            with open(file_name_nr, 'w') as csv_file:
                writer(csv_file).writerow(['Price', 'Type', 'Area(sqm)', 'NoBedrooms', 'NoBathrooms', 'Furnishing', 'Amenities', 'Location'])
                writer(csv_file).writerows(dataset)


        print("Listings collected until", str(pag), ":", str(len(dataset)))

    print("Scraped" + str(pagek+1) + "pages")



main()
with open('final.csv', 'w') as csv_file:
    writer(csv_file).writerow(['Price', 'Type', 'Area(sqm)', 'NoBedrooms', 'NoBathrooms', 'Furnishing', 'Amenities', 'Location'])
    writer(csv_file).writerows(dataset)