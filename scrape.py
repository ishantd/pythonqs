from requests import get
from bs4 import BeautifulSoup
import re
import itertools
import sqlite3
import json

# url = 'https://www.sanfoundry.com/1000-python-questions-answers/'
url = 'https://www.sanfoundry.com/artificial-intelligence-questions-answers/'
response = get(url)
main_soup = BeautifulSoup(response.text, 'html.parser')
links = main_soup.select('td a')
hrefs = []


def clean_text(string):
    if isinstance(string, list):
        for i in range(len(string)):
            escapes = ''.join([chr(char) for char in range(1, 32)])
            translator = str.maketrans('', '', escapes)
            string[i] = string[i].translate(translator)
        final = string
    else:
        escapes = ''.join([chr(char) for char in range(1, 32)])
        translator = str.maketrans('', '', escapes)
        final = string.translate(translator)
    return final

def check_question(qs):
    qs = qs.replace(" ", "")
    qs = ''.join([i for i in qs if not i.isdigit()])
    if len(qs) > 10:
        return True
    else:
        return False

created = 0
nc = 0

for x in links:
    hrefs.append(x.get('href'))

def get_data_from_page(page):
    global nc
    global created
    page_string = str(page)
    # print(page_string)
    all_p = page.find_all('p')
    all_options = []
    for p in all_p:
        para = str(p)
        options = re.findall(r'\d+[.](.*?)<\/div>', para, re.MULTILINE|re.DOTALL)
        all_options.append(options)
    all_options = (list(itertools.chain.from_iterable(all_options)))
    all_options = list(dict.fromkeys(all_options))
    print(len(all_options))
    data = []
    # try:
    for x in all_options:
        question = re.findall(r'^(.*?)<br\/>', x)
        if question:
            question = question[0] #Data Point
            if check_question(question):
                question = clean_text(question)
                options = re.findall(r'[a-d]\)(.*?)<br\/>', x) #Data Point
                options = clean_text(options)
                options = json.dumps(options)
                answer = re.findall(r'Answer:(.*?)<br\/>', x)  #Data Point
                if answer:
                    answer = answer[0].replace(" ", "")
                else:
                    answer = "NOT AVAILABLE"
                    print("ANSER IN NA")
                e = re.findall(r'Explanation:(.*?)$', x)
                if e:  #Data Point
                    e = e[0][1:]
                else:
                    e = "NOT AVAILABLE"
                    print("EPXLAINFA IN NA")
                    # nc = nc + 1
                point = {
                    'question' : question,
                    'options': options,
                    'answer': answer,
                    'explanation': e,
                }
                data.append(point)
                created = created + 1
            else:
                print("NOT A VALID QUESTION")
                continue
        else:
            nc = nc + 1
            continue
    return data

def get_page_from_url(link):
    response = get(link)
    print(link)
    page = BeautifulSoup(response.text, 'html.parser')
    data = get_data_from_page(page)
    return data

pages_data = []
for i in range(len(hrefs)):
    pages_data.append(get_page_from_url(hrefs[i]))
    print("PAGES LEFT =====> ", len(hrefs) - i)

pages_data = list(itertools.chain.from_iterable(pages_data))
print(type(pages_data[0]))


conn = sqlite3.connect('aidata.db')
cursor = conn.cursor()

#Doping EMPLOYEE table if already exists.
cursor.execute("DROP TABLE IF EXISTS QUESTIONS")

#Creating table as per requirement
sql ='''CREATE TABLE QUESTIONS(
   id integer primary key autoincrement,
   Q CHAR(500) NOT NULL,
   OPTIONS TEXT,
   ANSWER CHAR(1),
   EXPLANATION CHAR(1000)
)'''
cursor.execute(sql)
print("Table created successfully........")

for x in pages_data:
    cursor.execute('''INSERT INTO QUESTIONS(
   Q, OPTIONS, ANSWER, EXPLANATION) VALUES 
   (?, ?, ?, ?)''', (x['question'], x['options'], x['answer'], x['explanation']))

conn.commit()
print("Records inserted........")

# Closing the connection
conn.close()

print("TOTAL CRWATE", created)
print("DEL", nc)
