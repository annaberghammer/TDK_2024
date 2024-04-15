# -*- coding: utf-8 -*-
"""
Created on Sat Sep 30 10:56:14 2023

@author: Anna
"""

import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
import requests
import re
from textblob import TextBlob
from deep_translator import GoogleTranslator

### Download ChromeDriver automatically
#MISSING______________________________________________________________________________________________________________________

delay = 30

###---------------------------------------------------------------------------
### Open Profession.hu

url = 'https://www.profession.hu/cegek'

service = webdriver.ChromeService()
driver = webdriver.Chrome(service = service)
driver.get(url)

### Accept cookie's

try:
    WebDriverWait(driver, delay).until(
        EC.presence_of_element_located((By.ID, 'elfogad')))
    
except:
    pass

WebDriverWait(driver, delay).until(
    EC.any_of(
        EC.presence_of_element_located((By.ID, 'elfogad')),
        EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/div/div[1]/div[2]/select'))))

time.sleep(1)

try:
    driver.find_element('id', 'elfogad').click()
except:
    pass

WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/div/div[1]/div[2]/select')))
                                     
time.sleep(1)

### Order the list by number of reviews

drpOrder = Select(driver.find_element('xpath', '//*[@id="main"]/div/div[1]/div[2]/select'))

drpOrder.select_by_visible_text('Értékelés száma szerint csökkenő')

time.sleep(5)

###---------------------------------------------------------------------------
### Get all the companies links where number of reviews reach target

data = pd.DataFrame(columns = ['name', 'link', 'number_of_reviews'])

target_number_of_reviews = 10
review_count = 1000

while review_count >= target_number_of_reviews:       
    
    html = driver.page_source    
    soup = BeautifulSoup(html, 'html.parser')
        
    links = soup.find_all('div', attrs = {'class' : 'company-data'})
    
    for link in links:
        review_str = link.find('a').getText()
        review = int(review_str.split(' ')[0])
        
        if (review >= 0):
            href = link.find(href = True)['href']
            
            temp = pd.DataFrame([{'link': href, 'number_of_reviews': review}])
            
            data = pd.concat([data, temp], ignore_index = True)
    
    time.sleep(5)
    
    driver.find_element('xpath', '//*[@id="main"]/div/div[7]/div[2]/ul/li[2]/a/i').click()
    
    time.sleep(5)
    
    review_count_str = driver.find_element('xpath', '/html/body/div[1]/main/div/div[5]/div[1]/div[2]/div[2]/a[1]').text
    review_count = int(review_count_str.split(' ')[0])

### Get main part of the links
data['link'] = data['link'].str.rsplit('/ertekelesek', expand = True)[0]

### Transfer number of reviews into numerical column

data.number_of_reviews = data.number_of_reviews.astype(int)    

### Drop rows, where number of review is less than the target

data = data[data.number_of_reviews >= target_number_of_reviews]

driver.close()

### Number of companies

n = data.shape[0]

###---------------------------------------------------------------------------
### Get data for the companies
### Go through all of the companies in a loop

### Get the Reviews for the companies

data_company = pd.DataFrame(columns = ['name', 'description_short', 'description_long', 'score', 'address', 'employees', 'start_date', 'recommendation', 'reviewer_attributes', 'company_feature', 'company_review_by_category'])

for c in range(n):

    url = data['link'][c] + '/ertekelesek'
    
    company_html = requests.get(url = url).text
    company_soup = BeautifulSoup(company_html, 'html.parser')
    
    ### Company name
    name = company_soup.find('div', attrs = {'id': 'end-page-company-name'}).find('b').text.strip()
    
    data['name'][c] = name
    
    ### Company description
    description = company_soup.find('div', attrs = {'class': 'header-datas-description'}).text.strip()
    
    try:    
        description_short, description_long = description.split('●')
        description_short = description_short.strip()
        description_long = description_long.strip()
    except:
        description_short = description
        description_long = ''
    
    ### Company score
    score = company_soup.find('div', attrs = {'class' : 'header-datas-rate'}).text
    score = float(score.replace(',', '.'))
    
    ### Company address
    address = company_soup.find('div', attrs = {'class' : 'header-datas-company-datas'}).find_all('div')[0].text.strip()
    address = address.replace('\n', ' ')
    address = re.sub("\s\s+", " ", address)
    
    ### Company number of employees
    employees = company_soup.find('div', attrs = {'class' : 'header-datas-company-datas'}).find_all('div')[1].text.strip()
    employees = employees.split(' ')[0]
    
    ### Company start date
    try:
        start_date = company_soup.find('div', attrs = {'class' : 'header-datas-company-datas'}).find_all('div')[2].text.strip()
        start_date = int(start_date.split(' ')[0])
    except:
        start_date = ''
    
    ### Recommendation percentage
    recommendation = company_soup.find('text', attrs = {'class' : 'percentage'}).text
    recommendation = float(recommendation[:-1])
    
    ### Reviewers data
    reviewer_soup = company_soup.find('div', attrs = {'class' : 'evalutions-data-modal-content-datas'})
    
    reviewew_category_number = len(reviewer_soup.find_all('div', attrs = {'class' : 'rating-list-text'}))
    
    reviewer_attributes = pd.DataFrame(columns = ['category', 'percentage'])
    
    for i in range(reviewew_category_number):
        temp_category = reviewer_soup.find_all('div', attrs = {'class' : 'rating-list-text'})[i].text.strip()
        temp_category_percentage = float(reviewer_soup.find_all('div', attrs = {'class' : 'rating-list-after'})[i].text.strip()[:-1])
        
        temp = pd.DataFrame([{'category': temp_category, 'percentage': temp_category_percentage}])
        
        reviewer_attributes = pd.concat([reviewer_attributes, temp], ignore_index = True)
    
    ### Company's features
    company_feature_soup = company_soup.find('div', attrs = {'class' : 'rating-list-block-column-2 typical-of-the-workplace-data'})
    
    company_feature_number = len(company_feature_soup.find_all('div', attrs = {'class' : 'rating-list-text'}))
    
    company_feature = pd.DataFrame(columns = ['feature', 'score'])
    
    for i in range(company_feature_number):
        temp_feature = company_feature_soup.find_all('div', attrs = {'class' : 'rating-list-text'})[i].text.strip()
        temp_feature_score = float(company_feature_soup.find_all('div', attrs = {'class' : 'rating-list-after underline-dotted'})[i].text.strip()[:-1])
        
        temp = pd.DataFrame([{'feature': temp_feature, 'score': temp_feature_score}])
        
        company_feature = pd.concat([company_feature, temp], ignore_index = True)
    
    ### Company's review score by category
    company_review_soup = company_soup.find('div', attrs = {'class' : 'rating-list-block last-hide-separator'})
    
    company_review_number = len(company_review_soup.find_all('div', attrs = {'class' : 'rating-list-text'}))
    
    company_review_by_category = pd.DataFrame(columns = ['category', 'score'])
    
    for i in range(company_review_number):
        temp_category = company_review_soup.find_all('div', attrs = {'class' : 'rating-list-text'})[i].text.strip()
        temp_category_score = float(company_review_soup.find_all('div', attrs = {'class' : 'rating-list-after'})[i].text.strip().replace(',', '.'))
        
        temp = pd.DataFrame([{'category': temp_category, 'score': temp_category_score}])
        
        company_review_by_category = pd.concat([company_review_by_category, temp], ignore_index = True)

    ### Combine data
    temp = pd.DataFrame([{'name' : name, 'description_short' : description_short, 'description_long' : description_long, 'score' : score, 'address' : address, 'employees' : employees, 'start_date' : start_date, 'recommendation' : recommendation, 'reviewer_attributes' : reviewer_attributes, 'company_feature' : company_feature, 'company_review_by_category' : company_review_by_category}])
    
    data_company = pd.concat([data_company, temp], ignore_index = True)

###---------------------------------------------------------------------------
### Get the Text reviews for the companies

data_reviewer = pd.DataFrame(columns = ['company_name', 'score', 'text', 'status', 'number_of_years', 'position', 'hours', 'county', 'positives', 'negatives', 'recommend'])

for c in range(n):
    
    url = data['link'][c] + '/velemenyek'
    
    company_name = data['name'][c]
    
    driver = webdriver.Chrome(service = service)
    driver.get(url)
    
    ###Accept cookie's
    
    WebDriverWait(driver, delay).until(
        EC.any_of(
            EC.presence_of_element_located((By.ID, 'elfogad')),
            EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/div/div[1]/div[2]/select'))))
    
    try:
        driver.find_element('id', 'elfogad').click()
    except:
        pass
    
    WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, '//*[@id="end-page-new-evaluation"]')))
                                         
    time.sleep(1)
    
    last_page = 0
    
    while(last_page == 0):
        
        WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, '//*[@id="end-page-new-evaluation"]')))
        
        time.sleep(2)
        
        company_html = driver.page_source
        
        time.sleep(1)
        
        company_soup = BeautifulSoup(company_html, 'html.parser')
        
        review_cards_html = company_soup.find_all('div', attrs = {'class' : 'card feedback-item'})
        
        for i in range(len(review_cards_html)):
            score_category_number = len(review_cards_html[i].find_all('div', attrs = {'class' : 'rating-list-after'}))
        
            reviewer_category_score = pd.DataFrame(columns = ['category', 'score'])
        
            for j in range(score_category_number):
                
                if (j == 0):
                    temp_category = 'Összesített'
                else:
                    temp_category = review_cards_html[i].find_all('div', attrs = {'class' : 'rating-list-text'})[j - 1].text.strip()
                    
                temp_category_score = float(review_cards_html[i].find_all('div', attrs = {'class' : 'rating-list-after'})[j].text.strip().replace(',', '.'))
                
                temp = pd.DataFrame([{'category': temp_category, 'score': temp_category_score}])
                
                reviewer_category_score = pd.concat([reviewer_category_score, temp], ignore_index = True)
             
            text = review_cards_html[i].find('div', attrs = {'class' : 'feedback-item_title'}).text.strip()
            
            employee_data = review_cards_html[i].find('div', attrs = {'class' : 'feedback-item_breadcrumb'}).text.strip().split('•')
            
            if (len(employee_data) == 5):
                
                status = employee_data[0].strip()
                number_of_years = employee_data[1].strip()
                position = employee_data[2].strip()
                hours = employee_data[3].strip()
                county = employee_data[4].strip()
            
            elif(len(employee_data) == 4):
                
                status = employee_data[0].strip()
                number_of_years = employee_data[1].strip()
                hours = employee_data[2].strip()
                county = employee_data[3].strip()
                position = ''
                
            else:
                
                status = ''
                number_of_years = ''
                hours = ''
                county = ''
                position = ''
            
            positives = review_cards_html[i].find_all('div', attrs = {'class' : 'truncate-overflow'})[0].text.strip()
            
            negatives = review_cards_html[i].find_all('div', attrs = {'class' : 'truncate-overflow'})[1].text.strip()
            
            if(review_cards_html[i].find_all('div', attrs = {'class' : 'feedback-item_tag tag-extra m-0 mt-3'}) == []):
                recommend = 'Nem ajánlaná ismerőseinek'
            else:
                recommend = 'Ajánlaná ismerőseinek'
                
            temp = pd.DataFrame([{'company_name': company_name, 'score' : reviewer_category_score, 'text' : text, 'status' : status, 'number_of_years' : number_of_years, 'position' : position, 'hours' : hours, 'county' : county, 'positives' : positives, 'negatives' : negatives, 'recommend' : recommend}])
            
            data_reviewer = pd.concat([data_reviewer, temp], ignore_index = True)
            
        try:
            driver.find_element(By.XPATH, '//*[@id="main"]/div[2]/div[3]/div[12]/div[1]/ul/li[2]/div').click()
            
        except:
            last_page = 1
    
    driver.close() 

###---------------------------------------------------------------------------
### Create database where every data is in a seperate column

### Data Reviewer

data_reviewer_temp = pd.DataFrame()

for i in range(data_reviewer.shape[0]):
    
    temp = pd.DataFrame(data_reviewer['score'][i].T)
    temp.columns = temp.iloc[0]
    temp = temp[1:]
    
    data_reviewer_temp = pd.concat([data_reviewer_temp, temp], ignore_index = True)

data_reviewer_temp = data_reviewer_temp.astype(int)

data_reviewer = pd.merge(data_reviewer, data_reviewer_temp, left_index = True, right_index = True)

del data_reviewer['score']

### Data Company

### Reviewer attributes

data_company_temp = pd.DataFrame()

for i in range(data_company.shape[0]):
    
    temp = pd.DataFrame(data_company['reviewer_attributes'][i].T)
    temp.columns = temp.iloc[0]
    temp = temp[1:]
    
    data_company_temp = pd.concat([data_company_temp, temp], ignore_index = True)

data_company_temp = data_company_temp.astype(float)

data_company = pd.merge(data_company, data_company_temp, left_index = True, right_index = True)

del data_company['reviewer_attributes']

### Company feature

data_company_temp = pd.DataFrame()

for i in range(data_company.shape[0]):
    
    temp = pd.DataFrame(data_company['company_feature'][i].T)
    temp.columns = temp.iloc[0]
    temp = temp[1:]
    
    data_company_temp = pd.concat([data_company_temp, temp], ignore_index = True)

data_company_temp = data_company_temp.astype(float)

data_company = pd.merge(data_company, data_company_temp, left_index = True, right_index = True)

del data_company['company_feature']

### Company review by category

data_company_temp = pd.DataFrame()

for i in range(data_company.shape[0]):
    
    temp = pd.DataFrame(data_company['company_review_by_category'][i].T)
    temp.columns = temp.iloc[0]
    temp = temp[1:]
    
    data_company_temp = pd.concat([data_company_temp, temp], ignore_index = True)

data_company_temp = data_company_temp.astype(float)

data_company = pd.merge(data_company, data_company_temp, left_index = True, right_index = True)

del data_company['company_review_by_category']

### Translate reviews to english

data_reviewer['text_english'] = ''

for i in range(len(data_reviewer)):
    to_translate = data_reviewer['text'][i]
    data_reviewer['text_english'][i] = GoogleTranslator(source='auto', target='en').translate(to_translate)
    
data_reviewer['positives_english'] = ''

for i in range(len(data_reviewer)):
    to_translate = data_reviewer['positives'][i]
    data_reviewer['positives_english'][i] = GoogleTranslator(source='auto', target='en').translate(to_translate)   
    
data_reviewer['negatives_english'] = ''

for i in range(len(data_reviewer)):
    to_translate = data_reviewer['negatives'][i]
    data_reviewer['negatives_english'][i] = GoogleTranslator(source='auto', target='en').translate(to_translate)

###---------------------------------------------------------------------------
### Sentimental analysis for review

data_reviewer['text_polarity'] = ''

for i in range(len(data_reviewer)):
    blob = TextBlob(data_reviewer['text_english'][i])
    blob.ngrams(n = 2)
    polarity = blob.sentiment.polarity
    data_reviewer['text_polarity'][i] = polarity
    
data_reviewer['text_polarity'] = data_reviewer['text_polarity'].astype(float)

### Change the words that are often mistaken to other polarity
data_reviewer['text_english_2'] = data_reviewer['text_english']

for i in range(len(data_reviewer)):
    data_reviewer['text_english_2'][i] = data_reviewer['text_english_2'][i].replace('problematic', 'bad')
    data_reviewer['text_english_2'][i] = data_reviewer['text_english_2'][i].replace('Problematic', 'bad')
    data_reviewer['text_english_2'][i] = data_reviewer['text_english_2'][i].replace('Problematic', 'bad')  

data_reviewer['text_polarity_2'] = ''

for i in range(len(data_reviewer)):
    blob = TextBlob(data_reviewer['text_english_2'][i])
    blob.ngrams(n = 2)
    polarity = blob.sentiment.polarity
    data_reviewer['text_polarity_2'][i] = polarity
    
data_reviewer['text_polarity_2'] = data_reviewer['text_polarity_2'].astype(float)             

### Calculate the length of the positive and negative reviews

for i in range(len(data_reviewer)):
    try:
        data_reviewer['positives_len'][i] = len(data_reviewer['positives_english'][i])
    except:
        data_reviewer['positives_len'][i] = 0
    try:
        data_reviewer['negatives_len'][i] = len(data_reviewer['negatives_english'][i])
    except:
        data_reviewer['negatives_len'][i] = 0
    
###---------------------------------------------------------------------------
### Merge company data

data_company_result = data.merge(data_company, how = 'inner', on = 'name')

###
### Data cleaning steps

data_company_result['recommendation_2'] = data_company_result['recommendation'] /25 + 1
data_company_result['Biztosítják a munkaeszközöket'] = data_company_result['Biztosítják a munkaeszközöket'] /25 + 1
data_company_result['Vállalják a betanítást'] = data_company_result['Vállalják a betanítást'] /25 + 1
data_company_result['Stresszes'] = data_company_result['Stresszes'] /25 + 1
data_company_result['Jó célért dolgozni'] = data_company_result['Jó célért dolgozni'] /25 + 1
data_company_result['Rugalmas'] = data_company_result['Rugalmas'] /25 + 1
data_company_result['Családbarát hely'] = data_company_result['Családbarát hely'] /25 + 1
data_company_result['Szakmai kihívásokkal teli'] = data_company_result['Szakmai kihívásokkal teli'] /25 + 1
data_company_result['Monoton'] = data_company_result['Monoton'] /25 + 1
data_company_result['Környezettudatos hely'] = data_company_result['Környezettudatos hely'] /25 + 1
data_company_result['Támogatják a képzéseket'] = data_company_result['Támogatják a képzéseket'] /25 + 1
data_company_result['Nagy felelősséget igénylő'] = data_company_result['Nagy felelősséget igénylő'] /25 + 1
data_company_result['Fizikailag megterhelő'] = data_company_result['Fizikailag megterhelő'] /25 + 1
data_company_result['Összetartó csapat'] = data_company_result['Összetartó csapat'] /25 + 1
data_company_result['Változatos, izgalmas'] = data_company_result['Változatos, izgalmas'] /25 + 1

data_company_result['Stresszes'] = 6-data_company_result['Stresszes']
data_company_result['Monoton'] = 6-data_company_result['Monoton']
data_company_result['Fizikailag megterhelő'] = 6-data_company_result['Fizikailag megterhelő']

data_reviewer_agg = data_reviewer.groupby('company_name').agg({'text_polarity': 'mean', 'text_polarity_2': 'mean', 'positives_len': 'mean', 'negatives_len': 'mean'})

data_reviewer_agg['positive/negative ratio'] = data_reviewer_agg['positives_len'] / data_reviewer_agg['negatives_len']

data_clean = data_company_result.merge(data_reviewer_agg, how = 'left', left_on = 'name', right_on = 'company_name')

###---------------------------------------------------------------------------
### Remove unnecessarly columns

### Rename columns
data_clean = data_clean.rename(columns = {'name' : 'Company name',
                       'number_of_reviews' : 'Number of reviews',
                       'description_short' : 'Short description',
                       'score' : 'Overall score', 
                       'employees' : 'Number of employees',
                       'recommendation' : 'Recommendation', 
                       'Szakmunkás' : 'Skilled workers',
                       'Középfokú' : 'Secondary education',
                       'Felsőfokú' : 'Higher education',
                       '28 évnél fiatalabb' : 'Under 28 years',
                       '28-40 év közötti' : 'Between 28 and 40 years',
                       '40 évnél idősebb' : 'Older than 40 years',
                       '1 évnél kevesebb' : 'Less than 1 year', 
                       '1-3 év' : 'Between 1 and 3 years', 
                       '3 évnél több' : 'More than 3 years',
                       'Biztosítják a munkaeszközöket' : 'Provide the working tools', 
                       'Vállalják a betanítást' : 'Provide training in the beginning', 
                       'Stresszes' : 'Stressful',
                       'Jó célért dolgozni' : 'Work for good cause', 
                       'Rugalmas' : 'Flexible', 
                       'Családbarát hely' : 'Family friendly place',
                       'Szakmai kihívásokkal teli' : 'Professionally challenging', 
                       'Monoton' : 'Monotonous', 
                       'Környezettudatos hely' : 'Environmentally friendly place',
                       'Támogatják a képzéseket' : 'Supporting trainings', 
                       'Nagy felelősséget igénylő' : 'High responsibility',
                       'Fizikailag megterhelő' : 'Physically demanding', 
                       'Összetartó csapat' : 'Cohesive team', 
                       'Változatos, izgalmas' : 'Varied, exciting',
                       'Bérezés és juttatások' : 'Salary and benefits', 
                       'Munkaidő és munkarend' : 'Hours and working hours', 
                       'Főnökök' : 'Bosses',
                       'Fejlődési, előrelépési lehetőség' : 'Opportunities for development and advancement', 
                       'Munka és magánélet egyensúlya' : 'Work-life balance',
                       'Kollégák és céges hangulat' : 'Colleagues and company atmosphere', 
                       'Megközelíthetőség' : 'Contact', 
                       'Munkakörnyezet' : 'Working environment',
                       'text_polarity_2' : 'General review polarity', 
                       'positive/negative ratio' : 'Positive/Negative characters’ ratio '})
            
data_final = data_clean.drop(['link', 'description_long', 'address', 'start_date', 'text_polarity', 'recommendation_2', 'positives_len', 'negatives_len'], axis = 1)
           
###---------------------------------------------------------------------------
### Write data to Excel
writer = pd.ExcelWriter('data_all.xlsx')

data_clean.to_excel(writer, sheet_name = 'Company data', index = False)

writer.close()

writer = pd.ExcelWriter('data.xlsx')

data_final.to_excel(writer, sheet_name = 'Company data', index = False)

writer.close()
