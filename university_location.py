import pandas as pd
import geopy
from geopy.geocoders import Nominatim
from time import sleep

# Load the data
university_location = pd.read_csv('data/tcas.csv')
university_location['course'] = university_location['course'].str.replace(r'^\d+\.\s*', '', regex=True)

# Initialize geolocator
geolocator = Nominatim(user_agent="university_locator")

# Function to get latitude and longitude
def get_lat_lon(university):
    location = geolocator.geocode(f"{university}, Thailand")
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

# Add latitude and longitude columns if they don't exist
if 'latitude' not in university_location.columns:
    university_location['latitude'] = None
if 'longitude' not in university_location.columns:
    university_location['longitude'] = None

# Filter the rows with missing latitude or longitude
missing_lat_lon = university_location[university_location['latitude'].isnull() | university_location['longitude'].isnull()]

# Add latitude and longitude columns for missing rows
for i, row in missing_lat_lon.iterrows():
    print(f"Processing: {row['select_all_university']}")
    lat, lon = get_lat_lon(row['select_all_university'])
    university_location.at[i, 'latitude'] = lat
    university_location.at[i, 'longitude'] = lon
    # To avoid being blocked by the geocoding service
    sleep(1)

# Save the updated DataFrame
university_location.to_csv('data/data.csv', index=False)

# Display the updated DataFrame
university_location.head()
