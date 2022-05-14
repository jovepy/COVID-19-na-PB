# -*- coding: utf-8 -*-
"""
Created on Sat Feb 12 18:19:09 2022

@author: ohmkas
"""

import requests
from selenium import webdriver  # pip install selenium
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager  # pip install webdriver_manager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import unittest
from selenium import webdriver
import time
from datetime import date, timedelta
import pandas as pd
import numpy as np
import os
from bs4 import BeautifulSoup
import shutil
from os import listdir 

def navegar_chrome():
    global driver
    chrome_options =webdriver.ChromeOptions()
    prefs = {"download.default_directory": "G:\Meu Drive\Labimec\BOLETIM COVID 2.0\Downloads"}
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options)
    driver.set_window_position(0,0)
    driver.set_window_size(1600, 800)
    return(driver)

driver = navegar_chrome()

#inicio governo
driver.get('https://superset.plataformatarget.com.br/superset/dashboard/72/')
time.sleep(20)
page_content = driver.page_source
site_back = BeautifulSoup(page_content, 'html.parser')

qnt_enf = str(site_back.find_all('div')).split('73px;">',2)[-1].split('</')[0]
qnt_uti = str(site_back.find_all('div')).split('73px;">',3)[-1].split('</')[0]

ocup_enf = int(site_back.find_all('svg')[1].g.text.split("%",2)[0])/100
ocup_uti = int(site_back.find_all('svg')[2].g.text.split("%",2)[0])/100

down = driver.find_element(by=By.XPATH, value='//*[@id="slice_630-controls"]')   
down.click()
down = driver.find_element(by=By.XPATH, value='//*[@id="GRID_ID-pane-0"]/div/div/div[4]/div/div/div[1]/div[1]/div/div[1]/div[1]/div/div/ul/li[3]/a')   
down.click()
time.sleep(10)


for arquivo in os.listdir('G:/Meu Drive/Labimec/BOLETIM COVID 2.0/Downloads'):
    arquivo
    if arquivo[-4:] == '.csv':
        shutil.move(r'G:/Meu Drive/Labimec/BOLETIM COVID 2.0/Downloads/{}'.format(arquivo),r'G:/Meu Drive/Labimec/BOLETIM COVID 2.0/Leitos_por_Hosp/{}.csv'.format(date.today().strftime('%Y-%m-%d')))
        
    else:
        pass



driver.get('https://paraiba.pb.gov.br/diretas/saude/coronavirus')
time.sleep(10)
page_content = driver.page_source
site_back = BeautifulSoup(page_content, 'html.parser')
df_aux = pd.DataFrame(site_back.find_all('p'))[:5]
df_aux.index = df_aux.index%2
df_aux = df_aux.loc[0]
df_aux = df_aux.astype(str)
df_aux[0] = df_aux[0].str.split('>',expand=True)[1].str.split('\n',expand=True)[1].str.replace(' ','')
df_aux.index = ['confirmados','recuperados','obitos']
df_aux = df_aux.T
for coluna in df_aux:
    df_aux[coluna] = df_aux[coluna].str.replace('.','')
df_aux.index = [date.today().strftime('%Y-%m-%d')]
df_aux.index.name = 'data'
df_aux['qnt_enf'] = int(qnt_enf)
df_aux['qnt_uti'] = int(qnt_uti)
df_aux['ocup_enf'] = ocup_enf
df_aux['ocup_uti'] = ocup_uti

#fim governo

#inicio worldmeters
driver.get('https://www.worldometers.info/coronavirus/')
time.sleep(15)
page_content = driver.page_source
site_back = BeautifulSoup(page_content, 'html.parser')
tabela = pd.read_html(page_content)[0]
brasil = tabela.loc[tabela['Country,Other'] == 'Brazil'][['ActiveCases','Serious,Critical']]
mundo = tabela.loc[tabela['Country,Other'] == 'World'][['ActiveCases','Serious,Critical']]
df_aux['brativos'] = int(brasil['ActiveCases'].iloc[0])
df_aux['brgraves'] = int(brasil['Serious,Critical'].iloc[0])
df_aux['mdativos'] = int(mundo['ActiveCases'].iloc[0])
df_aux['mdgraves'] = int(mundo['Serious,Critical'].iloc[0])
#fim worldmeters

driver.quit()
#uniao 

#leitos por hospital
leitos_por_hospital = pd.DataFrame()  
 
for arquivo in listdir('G:/Meu Drive/Labimec/COVID19/leitos_disp'): 
  data_do_dia = [] 
  if arquivo[-4:] == '.csv': 
    aux = pd.read_csv('G:/Meu Drive/Labimec/COVID19/leitos_disp/'+arquivo) 
    for i in list(range(len(aux))): 
      data_do_dia.append((arquivo[:-4])) 
    aux.index = data_do_dia 
    aux.columns = ['Unidade hospitalar', 'qnt_enf_unid_hosp','qnt_uti_unid_hosp'] 
    leitos_por_hospital = pd.concat([leitos_por_hospital,aux]) 

for arquivo in listdir('G:/Meu Drive/Labimec/BOLETIM COVID 2.0/Leitos_por_Hosp'): 
  data_do_dia = [] 
  if arquivo[-4:] == '.csv': 
    aux = pd.read_csv('G:/Meu Drive/Labimec/BOLETIM COVID 2.0/Leitos_por_Hosp/'+arquivo) 
    for i in list(range(len(aux))): 
      data_do_dia.append((arquivo[:-4])) 
    aux.index = data_do_dia 
    aux.columns = ['Unidade hospitalar', 'qnt_enf_unid_hosp','qnt_uti_unid_hosp'] 
    leitos_por_hospital = pd.concat([leitos_por_hospital,aux]) 
    
leitos_por_hospital.index = pd.to_datetime(leitos_por_hospital.index) 
leitos_por_hospital.index.name = 'data' 
leitos_por_hospital.to_excel('G:/Meu Drive/Labimec/BOLETIM COVID 2.0/Base_Permanente/dasboard_leitos_covid.xlsx')


df_aux = df_aux.reset_index()
base_permanente = pd.read_excel('G:/Meu Drive/Labimec/BOLETIM COVID 2.0/Base_Permanente/base_covid.xlsx')
df_aux = df_aux[base_permanente.columns]
base_permanente = pd.concat([base_permanente,df_aux],axis=0)

base_permanente['data'] = pd.to_datetime(base_permanente['data'])

base_permanente.to_excel('G:/Meu Drive/Labimec/BOLETIM COVID 2.0/Base_Permanente/base_covid.xlsx',index=False)



#criação dos indicadores
base_permanente = base_permanente.set_index('data')
for coluna in base_permanente.columns:
    if 'ocup' in coluna:
        base_permanente[coluna] = base_permanente[coluna].astype(float)
    else:
        base_permanente[coluna] = base_permanente[coluna].astype(int)

base_permanente['ativos'] = base_permanente['confirmados']-base_permanente['obitos']- base_permanente['recuperados']

base_permanente['hospitalizados_uti'] = (base_permanente['qnt_uti']*base_permanente['ocup_uti']).astype(int)
base_permanente['hospitalizados_enf'] = (base_permanente['qnt_enf']*base_permanente['ocup_enf']).astype(int)
base_permanente['total_hospitalizados'] = (base_permanente['hospitalizados_uti']+base_permanente['hospitalizados_enf']).astype(int)
base_permanente['taxa_graves_hosp'] = (base_permanente['hospitalizados_uti']/base_permanente['total_hospitalizados'])
base_permanente['taxa_graves_ativos_PB'] = base_permanente['hospitalizados_uti']/base_permanente['ativos']
base_permanente['taxa_graves_ativos_BR'] = base_permanente['brgraves']/base_permanente['brativos']
base_permanente['taxa_graves_ativos_MD'] = base_permanente['mdgraves']/base_permanente['mdativos']

base_permanente.to_excel('G:/Meu Drive/Labimec/BOLETIM COVID 2.0/Base_Permanente/dasboard_covid.xlsx')
 
#fim da construcao da Base permanente e indicadores

