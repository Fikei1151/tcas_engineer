import pandas as pd

# Load the CSV file
file_path = 'all_tcas.csv'
data = pd.read_csv(file_path)

# Filter the dataframe to keep only rows where 'select_faculty' contains the word 'วิศว'
filtered_data = data[data['select_faculty'].str.contains('วิศว', na=False)]

# Drop the specified columns
filtered_data = filtered_data.drop(columns=['web-scraper-order', 'web-scraper-start-url','select_all_university-href','course-href','sub_course-href','select_faculty-href'])

# Save the filtered data to a new CSV file
filtered_file_path = 'filtered_all_tcas.csv'
filtered_data.to_csv(filtered_file_path, index=False)

print(f"Filtered file saved to: {filtered_file_path}")
