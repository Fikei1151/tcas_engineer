
import pandas as pd

# Load the data
file_path = 'university_location_with_lat_lon_updated.csv'
df = pd.read_csv(file_path)

# Filter the rows with missing latitude or longitude
missing_lat_lon = df[df['latitude'].isnull() | df['longitude'].isnull()]

# Get unique universities with missing latitude or longitude
unique_universities_missing = missing_lat_lon['select_all_university'].unique()

# Get all unique universities
unique_universities_all = df['select_all_university'].unique()

# Print the unique universities with missing latitude or longitude
print("Universities with missing latitude or longitude:")
for university in unique_universities_missing:
    print(university)

# Print the counts
print("\nTotal number of unique universities with missing latitude or longitude:", len(unique_universities_missing))
print("Total number of unique universities:", len(unique_universities_all))
