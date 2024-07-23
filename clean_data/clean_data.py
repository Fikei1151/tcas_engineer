import pandas as pd

file_path = "data\data.csv"

df = pd.read_csv(file_path)

df['select_faculty'] = df['select_faculty'].str.replace(r'^\d+\.\s*', '', regex=True)
df['course'] = df['course'].str.replace(r'^\d+\.\s*', '', regex=True)
df['sub_course'] = df['sub_course'].str.replace(r'^\d+\.\s*', '', regex=True)

df.to_csv('data/data.csv', index=False)