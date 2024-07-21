import pandas as pd
import geopy
from geopy.geocoders import Nominatim
from time import sleep

# Load the data
university_location = pd.read_csv('university_location_with_lat_lon.csv')

# Initialize geolocator
geolocator = Nominatim(user_agent="university_locator")

# Function to get latitude and longitude
def get_lat_lon(university, province):
    location = geolocator.geocode(f"{university}, {province}, Thailand")
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

# Filter the rows with missing latitude or longitude
missing_lat_lon = university_location[university_location['latitude'].isnull() | university_location['longitude'].isnull()]

# Add latitude and longitude columns for missing rows
for i, row in missing_lat_lon.iterrows():
    print(f"Processing: {row['university']}, {row['province']}")
    lat, lon = get_lat_lon(row['university'], row['province'])
    university_location.at[i, 'latitude'] = lat
    university_location.at[i, 'longitude'] = lon
    # To avoid being blocked by the geocoding service
    sleep(1)

# Save the updated DataFrame
university_location.to_csv('university_location_with_lat_lon_updated.csv', index=False)

university_location.head()
