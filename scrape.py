import bs4
from bs4 import BeautifulSoup
import csv
import lxml
import requests
import re
from string import digits
import mysql.connector
from mysql.connector import errorcode

# BeautifulSoup encodes email for protection, decode function
def decodeEmail(e):
    de = ""
    k = int(e[:2], 16)

    for i in range(2, len(e)-1, 2):
        de += chr(int(e[i:i+2], 16)^k)

    return de


list_of_companies = []
years = []
loc = []
numbers = []
strength = []
emails = []
websites = []
domain = []
csv_columns = ['CompanyName', 'Locations', 'YearFounded', 'PhoneNumber', 'EmployeeStrength', 'Website', 'Domain', 'Email']
domain_list = ['top-flutter-app-development-companies','top-mobile-app-development-companies-united-kingdom', 'top-mobile-app-development-companies-in-canada', 'top-video-production-companies', 'top-legal-cannabis-video-production-companies', 'top-mean-stack-developer', 'top-mobile-app-development-companies-in-canada', 'top-mobile-app-development-companies-uae', 'top-mobile-app-development-companies','top-mobile-app-development-companies-ukraine','top-ecommerce-development-companies', 'top-joomla-development-companies', 'top-wearable-app-development-companies', 'top-react-native-app-development-companies', 'top-full-stack-developer', 'top-react-js-development-companies', 'top-laravel-development-companies-developers', 'top-php-development-companies', 'top-web-design-companies', 'top-wordpress-development-companies', 'top-shopify-development-companies', 'top-magento-web-development-companies']


for x in domain_list:
    print x
    i = 1
    while(1):
        url = "https://www.itfirms.co/"+str(x)+"/"+str(i)+"/"

        response = requests.get(url)
        soup = BeautifulSoup(response.content,'lxml')
        # domain = soup.title.text

        h3 = soup.find_all('h3')
        if len(h3) == 0:
            break

        tags = soup.findAll("div", class_="additional_detail")
        if len(tags) == 0:
            break
        
        for h in h3:
            s = str(h.text.encode('utf-8'))
            comp = s.replace(':',  '').translate(None, digits).replace('. ', '')
            k = bool(re.search(r'\d', s))
            if k == True:
                list_of_companies.append(comp)
        
        for tag in tags:
            t1 = re.search('>(.*)<',str(tag.find('span', {'class': 'w-detail located-i'}))).group(1)
            t2 = re.search('>(.*)<',str(tag.find('span', {'class': 'w-detail founded-i'}))).group(1)
            t3 = re.search('>(.*)<',str(tag.find('span', {'class': 'w-detail call-i'}))).group(1)
            t4 = re.search('>(.*)<',str(tag.find('span', {'class': 'w-detail employees-i'}))).group(1)
            t5 = re.search('>(.*)<',str(tag.find('span', {'class': 'w-detail email-i'}))).group(1)
            try:
                t5 = decodeEmail(re.search('data-cfemail="(.*)">',t5).group(1))
            except AttributeError:
                t5 = ""
            emails.append(t5)
            years.append(t2.replace('Founded: ',''))
            loc.append(t1.replace('""',''))
            strength.append(t4.replace('\xe2\x80\x93', '-'))
            numbers.append(t3.replace('<a>', '').replace('</a>', '').replace(' ',''))
            domain.append(x)

        dict = {}
        dict_data = []

        h4 = soup.find_all('h4')
        for h in h4:
            websites.append(str(h.text))
    
        i=i+1

for i in range(len(list_of_companies)):
    dict = {}
    dict['CompanyName'] = list_of_companies[i]
    if years[i].isdigit():
        dict['Locations'] = loc[i]
        dict['YearFounded'] = years[i]
    else:
        dict['Locations'] = years[i]
        dict['YearFounded'] = loc[i]
    dict['EmployeeStrength'] = strength[i]
    dict['Website'] = websites[i]
    dict['PhoneNumber'] = numbers[i]
    dict['Domain'] = domain[i]
    dict['Email'] = emails[i]
    dict_data.append(dict)

# print soup.prettify()

csv_file = "Companies.csv"
try:
    with open(csv_file, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in dict_data:
            writer.writerow(data)
except IOError:
    print("I/O error")

config = {
  'user': '<username>',
  'password': '<password>',
  'host': '127.0.0.1',
  'database': '<databasename>',
  'raise_on_warnings': True
}


sql = "INSERT INTO Companies (CompanyName, Locations, YearFounded, PhoneNumber, EmployeeStrength, Website, Domain, Email) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"

# CREATE TABLE `Companies` (
#   `CompanyName` varchar(50) ,
#   `Locations` varchar(50) ,
#   `YearFounded` int,
#   `PhoneNumber` varchar(50),
#   `EmployeeStrength` varchar(50) ,
#   `Website` varchar(50) ,
#   `Domain` varchar(100) ,
#   `Email` varchar(50) 
# )

try:
  cnx = mysql.connector.connect(**config)
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)
else:
    print("Connected to DB")
    mycursor = cnx.cursor()
    mycursor.executemany("""
    INSERT INTO Companies (CompanyName, Locations, YearFounded, PhoneNumber, EmployeeStrength, Website, Domain, Email)
    VALUES (%(CompanyName)s, %(Locations)s, %(YearFounded)s, %(PhoneNumber)s, %(EmployeeStrength)s, %(Website)s, %(Domain)s, %(Email)s)""", dict_data)
    cnx.commit()
    mycursor.close()
    cnx.close()
    print("Inserted Successfully")
