import pandas as pd
import os
import datetime
import numpy as np

os.chdir("set working directory")

#Fetch new summary data
summary_new = pd.read_csv('https://raw.githubusercontent.com/nychealth/coronavirus-data/master/summary.csv', error_bad_lines=False)
#transpose and rename column
summary_new = summary_new.T
summary_new = summary_new.reset_index()
summary_new.columns = summary_new.iloc[0]
summary_new = summary_new.drop(summary_new.index[0])
summary_new = summary_new.rename(columns={'Hospitalized*:':'Total hospitalized*:'})
#pull the date to append to the other excel data files
date = summary_new['As of:'].iloc[0]
try:
    summary_new['date'] = pd.to_datetime(summary_new['As of:'])
    date = summary_new['As of:'].iloc[0]
    summary_new = summary_new.drop(columns=['As of:'])
except:
    df_date = summary_new['As of:'].iloc[0].split()
    # get text month
    month = df_date[0]
    # convert text month to number:
    m = {
        'jan': 1,
        'feb': 2,
        'mar': 3,
        'apr': 4,
        'may': 5,
        'jun': 6,
        'jul': 7,
        'aug': 8,
        'sep': 9,
        'oct': 10,
        'nov': 11,
        'dec': 12
    }
    s = month.strip()[:3].lower()
    try:
        month_numb = int(m[s])
    except:
        raise ValueError('Not a month')
    # get day, remove coma
    day = int(df_date[1].replace(',', ''))
    # build date:
    summary_new['date'] = datetime.datetime(2020, int(month_numb), int(day))
    summary_new = summary_new.drop(columns=['As of:'])
    date = datetime.datetime(2020, int(month_numb), int(day))
print(summary_new)
print()
#load existing summary data
summary = pd.read_excel('NYC_COVID_19_data.xlsx', sheet_name='summary')
#append new summary
summary = summary.append(summary_new,sort=True)

#fetch new boro data
boro_new = pd.read_csv('https://raw.githubusercontent.com/nychealth/coronavirus-data/master/boro.csv', error_bad_lines=False)
#create column with the date as values
boro_new['date'] = date
try:
    boro_new['date'] = pd.to_datetime(boro_new['date'])
except:
    pass
print(boro_new)
print()
#load existing boro data
boro = pd.read_excel('NYC_COVID_19_data.xlsx', sheet_name='boro')
#append new boro data to old
boro = boro.append(boro_new,sort=True)

#fetch bew by age data
by_age_new = pd.read_csv('https://raw.githubusercontent.com/nychealth/coronavirus-data/master/by-age.csv', error_bad_lines=False)
#create column with the date as values
by_age_new['date'] = date
try:
    by_age_new['date'] = pd.to_datetime(by_age_new['date'])
except:
    pass
print(by_age_new)
print()
#load existing data
by_age = pd.read_excel('NYC_COVID_19_data.xlsx', sheet_name='by age')
#append new to old
by_age = by_age.append(by_age_new,sort=True)

#fetch new sex data
by_sex_new = pd.read_csv('https://raw.githubusercontent.com/nychealth/coronavirus-data/master/by-sex.csv', error_bad_lines=False)
#create column with the date as values
by_sex_new['date'] = date
try:
    by_sex_new['date'] = pd.to_datetime(by_sex_new['date'])
except:
    pass
print(by_sex_new)
print()
#load existing data
by_sex = pd.read_excel('NYC_COVID_19_data.xlsx', sheet_name='by sex')
#append new to old
by_sex = by_sex.append(by_sex_new,sort=True)

#fetch new by zip code data
tests_by_zcta_new = pd.read_csv('https://raw.githubusercontent.com/nychealth/coronavirus-data/master/tests-by-zcta.csv', error_bad_lines=False)
#create column with the date as values
tests_by_zcta_new['date'] = date
try:
    tests_by_zcta_new['date'] = pd.to_datetime(tests_by_zcta_new['date'])
except:
    pass
#load existing data
tests_by_zcta = pd.read_excel('NYC_COVID_19_data.xlsx', sheet_name='by zcta')
#appned new to old
tests_by_zcta = tests_by_zcta.append(tests_by_zcta_new,sort=True)
print(tests_by_zcta.head())
print()

#load population data and join to zipcode
df_pop = pd.read_excel(r'/Users/annastish/PycharmProjects/tadhg_proj/zipcodepop.xlsx')
zipcode_join = pd.DataFrame(tests_by_zcta)
zipcode_join = zipcode_join.set_index('MODZCTA').join(df_pop.set_index('Zip Code'))
zipcode_join = zipcode_join.reset_index().rename(columns={'index':'MODZCTA'})
zipcode_join['pos%pop'] = (zipcode_join['Positive']/zipcode_join['Population'])*100
zipcode_join['per 100'] = (zipcode_join['Positive']*100)/zipcode_join['Population']
print(zipcode_join.head())
print()

#reshape zip code data for scatter plot graph
df = pd.DataFrame(tests_by_zcta)
df = df.replace('nan', np.NaN)
df = df.dropna()
df['zipcode'] = df['MODZCTA'].astype(int)
df['date'] = df['date'].dt.date
zips = df['zipcode'].unique()
zip_scatter = pd.DataFrame()
for i in zips:
    try:
        df_zip= df.loc[df['zipcode'].isin([i])]
        df_zip_piv = df_zip.pivot(index='zipcode', columns='date', values='Positive')
        zip_scatter = zip_scatter.append(df_zip_piv)
    except:
        print(i)
#create date parameters
max_Date = df['date'].max()
day = datetime.timedelta(1)
max_Date_1 = max_Date - day*3
max_Date_2 = max_Date_1 - day
zip_scatter['max - max_t1'] = zip_scatter[max_Date] - zip_scatter[max_Date_1]
zip_scatter['max_t1 - max_t2'] = zip_scatter[max_Date_1] - zip_scatter[max_Date_2]
print(zip_scatter.head())
print()

#fetch new case_hope_death data
case_hosp_death_new = pd.read_csv('https://raw.githubusercontent.com/nychealth/coronavirus-data/master/case-hosp-death.csv', error_bad_lines=False)
#create column with the date as values
case_hosp_death_new['date_recorded'] = date
#load existing data
case_hosp_death = pd.read_excel('NYC_COVID_19_data.xlsx', sheet_name='case_hosp_death')
#appned new to old
case_hosp_death = case_hosp_death.append(case_hosp_death_new,sort=True)
print(case_hosp_death)
print()

# Create a Pandas Excel writer using XlsxWriter as the engine.
writer = pd.ExcelWriter('NYC_COVID_19_data.xlsx', engine='xlsxwriter')
# Convert the dataframea to an XlsxWriter Excel object.
summary.to_excel(writer, sheet_name='summary',index=False)
case_hosp_death.to_excel(writer, sheet_name='case_hosp_death', index=False)
boro.to_excel(writer, sheet_name='boro',index=False)
by_age.to_excel(writer, sheet_name='by age',index=False)
by_sex.to_excel(writer, sheet_name='by sex',index=False)
tests_by_zcta.to_excel(writer, sheet_name='by zcta',index=False)
zipcode_join.to_excel(writer, sheet_name='by zcta - pop',index=False)
zip_scatter.to_excel(writer, sheet_name='zip scatter')
#save
writer.save()
print('new data appended and saved')