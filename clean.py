import pandas as pd

# Load the CSV file
file_path = 'all_tcas.csv'
df = pd.read_csv(file_path)

# Filter out rows where 'select_faculty' does not contain 'วิศวกรรมศาสตร์'
filtered_df = df[df['select_faculty'].str.contains('วิศวกรรมศาสตร์')]

# Drop columns that contain 'url' or 'href'
filtered_df = filtered_df.drop(columns=[col for col in filtered_df.columns if 'url' in col or 'href' in col])

# Save the filtered dataframe to a new CSV file
filtered_file_path = 'filtered_all_tcas_no_url_href.csv'
filtered_df.to_csv(filtered_file_path, index=False)
