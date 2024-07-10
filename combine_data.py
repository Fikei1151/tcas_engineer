import pandas as pd

data1 = pd.read_csv('filtered_all_tcas.csv')
data2 = pd.read_csv('university_location.csv')

data2.drop('id', inplace=True, axis=1) 
data2.drop('year', inplace=True, axis=1) 

output = pd.merge(data1, data2,  
                   on='university',  
                   how='inner') 

file_path = 'combine_data.csv'
output.to_csv(file_path, index=False)