import bs4
from bs4 import BeautifulSoup
import csv
import lxml
import requests
import re
from string import digits


# BeautifulSoup encodes email for protection, decode function
def decodeEmail(e):
    de = ""
    k = int(e[:2], 16)

    for i in range(2, len(e)-1, 2):
        de += chr(int(e[i:i+2], 16)^k)

    return de




list_of_companies = []
loc = []
numbers = []
strength = []
emails = []
websites = []
domain = []
dict_data = []
csv_columns = ['CompanyName', 'Locations', 'PhoneNumber', 'EmployeeStrength', 'Website', 'Domain', 'Email']
domain_list = ['content-marketing', 'email-marketing', 'marketing-analytics-big-data', 'amazon-marketing', 'ecommerce-seo-marketing', 'inbound-marketing', 'software-development', 'offshore-software-developers', 'outsourcing-companies', 'ar-vr', 'cybersecurity-risk-management', 'aws-solution-architects', 'wearable-technology-companies', 'iot-companies', 'salesforce-developer', 'sap-consulting-companies', 'data-entry', 'information-technology']

for x in domain_list:
    print "*-----"+x+"-----*"
    url = "https://www.designrush.com/agency/"+x
    response = requests.get(url)
    soup = BeautifulSoup(response.content,'lxml')
    page = soup.findAll("li", class_="page-item")

    maxPage = []
    for p in page:
        if p.a is not None:
            if p.a.text.isdigit():
                maxPage.append(int(p.a.text.encode('utf-8')))

    maxPageVal = max(maxPage)


    print maxPageVal
    i=0
    while(1):
        
        if i == 0:
            url = "https://www.designrush.com/agency/"+x
        elif i <= maxPageVal:
            url = "https://www.designrush.com/agency/"+x+"/?page="+str(i)
        else:
            break
            
        print url
        response = requests.get(url)
        soup = BeautifulSoup(response.content,'lxml')
    
        domain = soup.title.text.split('|')[0]

        tags = soup.findAll("div", class_="agency-list-item-info")


        for tag in tags:
            img = tag.find('img', alt=True)
            list_of_companies.append(img['alt'])
            web = tag.find_all('a', href=True)
            websites.append(web[0]['href'].split('?', 1)[0].encode('utf-8'))
        
            meta = tag.find("ul", attrs={"class": "agency-list-item-info-meta"})
            k = meta.find_all("li")
            loc.append(k[0].text.strip().encode('utf-8'))
            strength.append(k[1].text.strip().encode('utf-8'))

        info = soup.findAll("div", class_="agency-list-contact-info")
        for inf in info:
            phnNo = inf.find("a",  attrs={"class": "agency-list-contact-box--link"})
            mail = inf.find('span', {'class': '__cf_email__'})
            decodedMail = decodeEmail(re.search('data-cfemail="(.*)">',str(mail)).group(1))
            emails.append(decodedMail)
            numbers.append(phnNo['href'][4:])
        
        i = i+1

for i in range(len(list_of_companies)):
    dict = {}
    dict['CompanyName'] = list_of_companies[i].encode('utf-8')
    dict['Locations'] = loc[i].encode('utf-8')
    dict['EmployeeStrength'] = strength[i].encode('utf-8')
    dict['Website'] = websites[i].encode('utf-8')
    dict['PhoneNumber'] = numbers[i]
    dict['Domain'] = domain.encode('utf-8')
    dict['Email'] = emails[i].encode('utf-8')
    dict_data.append(dict)


csv_file = "DesignRush.csv"
try:
    with open(csv_file, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in dict_data:
            writer.writerow(data)
except IOError:
    print("I/O error")
