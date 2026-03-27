import requests
import json
import pandas as pd
import os
from dotenv import load_dotenv

# Retreiving data for all countries with the needed fields - name, capital, flags, flag, population, continents
restcountries_url = 'https://restcountries.com/v3.1/all?fields=name,capital,flag,flags,population,continents'
# Note 1:
# REST Countries API endpoint with explicit versioning (v3.1).
# Using a fixed version ensures stability. However, external APIs 
# are subject to deprecation policies. If fields are modified or removed 
# in future versions, this ETL pipeline will require schema migration. For example, 'demonym' field is available only in v2
# Ref: https://gitlab.com/restcountries/restcountries/-/blob/master/FIELDS.md
# Note 2:
# Some fields for example  'name' and 'name > official/common' specified in Fields Description table as two separate lines
# so from the first sight it might be confusing, because firstly it looks like 2 separate fields 
# and secondly 'name > official/common' naming (would it be a separate field) can cause syntax errors,
# however, while researching the data in jupyter notebook, it becomes clear that this field is a nested one
# in the 'name' field. 

response = requests.get(restcountries_url)
if response.status_code == 200:
    data = json.loads(response.text)
else:
    print(f"API Error: {response.status_code} - {response.text}")

#Converting json data into a dataframe
df = pd.DataFrame(data)

#Getting rid of 'list' structure in the 'capital' column
exploded_df = df.explode("capital",ignore_index = True)

#Getting rid of 'list' structure in the 'continents' column
exploded_df2 = exploded_df.explode("continents",ignore_index = True)

#As a first step of normalization, normalizing the 'flags' data, keeping only the needed columns with description and flag's png url
normalize_flags = pd.json_normalize(exploded_df2['flags'])
normalize_flags = normalize_flags.drop('svg', axis=1)

#As a second step of normalization, normalizing the 'name' data, keeping only the needed columns - common name and official name
normalize_name = pd.json_normalize(exploded_df2['name'])
normalize_name = normalize_name[['common','official']]

#Joining 3 datasets - the first one where we exploded the 'capital', the second one where we normalized flags, and the third one where we normalized countries names
df_flat = pd.concat([exploded_df2.drop(['flags', 'name', 'flag'], axis=1), normalize_flags, normalize_name], axis=1)
df_flat = df_flat.rename(columns={'png':'flag_png', 'alt':'flag_desc', 'common':'country_name', 'official':'country_official_name'})

#Setting up the columns order and data types, sorting the dataset by the 'country_name' column
columns_order = ['country_name', 'country_official_name', 'capital','continents', 'flag_desc', 'flag_png', 'population']
df_flat = df_flat.astype({
    'country_name': 'string',
    'country_official_name': 'string',
    'capital': 'string',
    'continents': 'string',
    'flag_desc': 'string',
    'flag_png': 'string'
})

#Handling Nulls
df_flat = df_flat.fillna('no data')
df_final = df_flat[columns_order].sort_values(by='country_name')


#For saving data into the database
#getting credentials from .env file
load_dotenv()
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_PORT = os.getenv('DB_PORT') #I am using port 5433 as I have Postgres itself set up locally and this caused an error

#Creating Engine
from sqlalchemy import create_engine
database_url = f'postgresql://{DB_USER}:{DB_PASSWORD}@localhost:{DB_PORT}/countries_db'
engine = create_engine(database_url)

#Saving data into the database
def save_to_db(df_final, table_name='countries'):
    try:
        df_final.to_sql(table_name, con=engine, if_exists='replace', index=False)
        print('Data successfully saved')
    except Exception as e:
        print(f"error: {e}")
save_to_db(df_final)

