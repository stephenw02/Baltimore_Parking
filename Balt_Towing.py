import pandas as pd
import geopandas
from shapely.geometry import Point
from time import sleep
import json
from folium import plugins
import folium
from collections import Counter
import django
import os
import math
import requests
import numpy as np
from datetime import datetime
import re
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import warnings

warnings.filterwarnings("ignore")

### Import any new data from source and load into database
# Set the DJANGO_SETTINGS_MODULE to point to your settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'baltparkweb.settings')
django.setup()

from maps.models import ProcessedDataLog, TowingRecord  # Import the model for storing last objectId

#TowingRecord.objects.all().delete()
#ProcessedDataLog.objects.filter(dataset_name="TowingDataset").delete()

# Base URL for the API
base_url = "https://opendata.baltimorecity.gov/egis/rest/services/NonSpatialTables/Towing/FeatureServer/0/query"

# Get the latest processed objectId from the database
def get_last_object_id():
    # Retrieve the latest objectId from the database for the dataset
    log = ProcessedDataLog.objects.filter(dataset_name="TowingDataset").first()
    if log:
        print(f"Last processed object ID: {log.last_object_id}")
        return log.last_object_id
    else:
        print("No processed data log found, starting from scratch.")
        return None

# Fetch new data by querying from the latest objectId
def fetch_new_data(url, last_object_id, batch_size=2000):
    print("last object ID: ", last_object_id)
    
    # If last_object_id exists, query only for new records
    where_clause = f"1=1"
    #where_clause = f"ESRI_OID > {last_object_id}" if last_object_id else "ESRI_OID > 0"
    print(f"Fetching new data with where_clause: {where_clause}")
    
    # Get all object IDs greater than the last_object_id
    query_url = f"{url}?where={where_clause}&returnIdsOnly=true&f=json"
    try:
        response = requests.get(query_url)
    except Exception as e:
        print("Error: ", e)
        return None, None

    if response.status_code != 200:
        print(f"Error fetching object IDs: {response.status_code}")
        return None, None

    data = response.json()
    
    try:
        print("Items to process: ", data['objectIds'])
    except:
        print("error retreiving data")
        return None, None # Error fetching results

    if data['objectIds'] != []:
        object_ids = data['objectIds']
        object_ids.sort()
        object_ids = object_ids[last_object_id::]
    else:
        print("No new records found.")
        return None, None  # No new data to process
    
    total_batches = math.ceil(len(object_ids) / batch_size)
    
    max_object_id = last_object_id  # Initialize with the last object ID from the previous run

    for i in range(total_batches):
        id_subset = object_ids[i*batch_size:(i+1)*batch_size]
        id_string = ','.join(map(str, id_subset))
        
        payload = {
            'objectIds': id_string,
            'outFields': '*',
            'outSR': '4326',
            'f': 'json'
        }
        response = requests.post(url, data=payload)
        data = response.json()

        features = data.get('features', [])
        
        if features:
            df = pd.json_normalize(features)
            df.columns = df.columns.str.replace('attributes.', '', regex=False)
            df = df.replace({np.nan: None})
            
            # Insert the DataFrame rows into your database for this batch
            for row in df.itertuples():
                try:
                    if row.TowedDateTime == None:
                        print("No Date Entered")
                    elif datetime.fromtimestamp(int(row.TowedDateTime)/1000) > datetime(2021, 1, 1, 0, 1):
                            TowingRecord.objects.create(
                                PropertyNumber=row.PropertyNumber,
                                TowedDateTime=row.TowedDateTime,
                                PickupType=row.PickupType,
                                VehicleType=row.VehicleType,
                                VehicleYear=row.VehicleYear,
                                VehicleMake=row.VehicleMake,
                                VehicleModel=row.VehicleModel,
                                VehicleColor=row.VehicleColor,
                                TagNumber=row.TagNumber,
                                TagState=row.TagState,
                                TowCompany=row.TowCompany,
                                TowCharge=row.TowCharge,
                                TowedFromLocation=row.TowedFromLocation,
                                HowTowed=row.HowTowed,
                                SlingUsed=row.SlingUsed,
                                DollyUsed=row.DollyUsed,
                                rollBackUsed=row.rollBackUsed,
                                pinPulled=row.pinPulled,
                                pinReplaced=row.pinReplaced,
                                WheelLift=row.WheelLift,
                                Stinger=row.Stinger,
                                ReceivingDateTime=row.ReceivingDateTime,
                                StorageYard=row.StorageYard,
                                StorageLocation=row.StorageLocation,
                                StorageTelephone=row.StorageTelephone,
                                TitleRenounciation=row.TitleRenounciation,
                                TRDateTime=row.TRDateTime,
                                PersonalPropRemoved=row.PersonalPropRemoved,
                                PersonalPropLeftInVehicle=row.PersonalPropLeftInVehicle,
                                HoldType=row.HoldType,
                                HoldDateTime=row.HoldDateTime,
                                HoldReleasedDateTime=row.HoldReleasedDateTime,
                                HoldReleasedNotifyDate=row.HoldReleasedNotifyDate,
                                RemovedFromYardDate=row.RemovedFromYardDate,
                                StolenVehicleFlag=row.StolenVehicleFlag,
                                Status=row.Status,
                                ReleaseDateTime=row.ReleaseDateTime,
                                ReleaseType=row.ReleaseType,
                                TotalPaid=row.TotalPaid,
                                ESRI_OID=row.ESRI_OID
                            )
                    else:
                        print("Date before 2021. Not saving to database")
                except:
                    print("error with timestamp")

            print(f"Processed and saved batch {i+1}/{total_batches} with {len(df)} records.")
            
            # Clear the DataFrame to free up memory
            del df
        
            # Update the max_object_id if the current batch contains higher values
            current_max_id = max(id_subset)
            if max_object_id == None:
                max_object_id = current_max_id
            elif current_max_id > max_object_id:
                max_object_id = current_max_id
            
            # Update the last processed object ID in the database after each batch
            log, created = ProcessedDataLog.objects.get_or_create(dataset_name="TowingDataset")
            log.last_object_id = max_object_id
            log.save()

            print(f"Updated last processed object ID to: {max_object_id}")

        else:
            print("No Features Found")

        # Pause between batches to avoid overloading the server
        sleep(5)
    
    return max_object_id

# Process and save the new data
def process_and_save_data():
    # Step 1: Get the latest objectId from the database
    last_object_id = get_last_object_id()
    
    # Step 2: Fetch new data from the API starting from the last objectId
    fetch_new_data(base_url, last_object_id)

# Run the process
process_and_save_data()


### Load dataset
# Query all records from the model
records = TowingRecord.objects.all().values()

# Convert the queryset to a list of dictionaries
records_list = list(records)

# Convert the list of dictionaries to a Pandas DataFrame
df = pd.DataFrame(records_list)



### Clean Data
# Convert datetime string to datatime type
df["TowedDateTime"] = pd.to_datetime(df["TowedDateTime"], unit='ms', errors='coerce')

desc_list = ['Impound (Illegal Parking)', 'Parking Violation', 'street cleaning', 'Street cleaning']

# Filter out null values, dates before 2024, and non relevant towing causes (accidents, abandoments, etc.)
df2 = df[ (df['TowedFromLocation'].notnull()) & (df["TowedDateTime"]>"1/1/2024 0:00:01 AM") & (df["TowedDateTime"]!=pd.NaT) & (df["PickupType"].isin(desc_list)) ]
df2 = df2[~df2.TowedFromLocation.str.startswith('0')]

# Clean addresses and add city + state
df2['AddressTrim'] = df2['TowedFromLocation'].str.replace(r'^(E/S|O/S|O/UB|O/D|U/B|O/|UNIT)\s*', '', regex=True)
df2['TowedFromAddressFull'] = df2['AddressTrim'].astype(str) + ', Baltimore, MD'

# Load the dictionary from the JSON file
with open('address_data.json', 'r') as json_file:
    add_geo_dict = json.load(json_file)

# Get geocoordinates from address function
def get_GeoCoords(input, x):

    input2 = input

    # Check if address is already in dictionary of known coords
    if input2 in add_geo_dict.keys():
        return add_geo_dict[input2]
    else:
        sleep(4)
        try:
            # Geocode address to get coordinates
            resp = geopandas.tools.geocode(input2, provider='nominatim', user_agent="donut123")
            coord = [resp.geometry.iloc[0].x, resp.geometry.iloc[0].y]
            print(x, " - ", input2, " : ", coord)
            add_geo_dict[input2] = coord
            return coord
        except:
            add_geo_dict[input2] = ""
            print(x, " - ", input2, " : " , "Failed")
            return ""
        
# Apply geocoord function
df2["TowedFromCoord"] = df2.apply(lambda x: get_GeoCoords(x['TowedFromAddressFull'], x.name), axis=1)

# Save the dictionary as a JSON file
with open('address_data.json', 'w') as json_file:
    json.dump(add_geo_dict, json_file)

df3 = df2

# Export for Extras
df3.to_csv("Towing_csv.csv")


# Remove blank coordinate rows
df4 = df3[ (df3['TowedFromCoord'] != "") ]

df4["TowedFromCoord"] = df4["TowedFromCoord"].astype(str)

def clean_coord_str(row):
    try:
        lat, lon = row.replace("[","").replace("]","").split(",")
        return [lat,lon]
    except:
        print("error cleaning row: ", row)


# Clean coordinate string
df4["TowedFromCoord"] = df4.apply(lambda x: clean_coord_str(x["TowedFromCoord"]), axis=1)

def create_geo_point(row):
    try:
        point = Point( round(float(row[0]),6), round(float(row[1]),6) )
        return point
    except:
        print("error with row: ", row)


# Convert coordinates to Shapely Point
df4["CM"] = df4.apply(lambda x: create_geo_point(x["TowedFromCoord"]), axis=1)


### Heat Map Creation
# Get list of coordinates
coords_list =  df4.apply(lambda x: (x["TowedFromCoord"][1], x["TowedFromCoord"][0]), axis=1)

# Get count of coordinate occurances
coords_counter = Counter(coords_list)

# Create a list of coordinates with intensity (count of occurrences)
heatmap_data = [[coord[0], coord[1], count/max(coords_counter.values())] for coord, count in coords_counter.items()]

# Generate and save Heatmap
m = folium.Map(location=(39.2904,-76.6122), width='100%', height='100%', zoom_start=15, tiles="CartoDB positron")
plugins.HeatMap(heatmap_data, radius=17, blur=23, min_opacity=0.5).add_to(m)
m.save('maps/templates/towing_heatmap.html')


### Plot Map Creation
# Drop unnecessary columns
df5= df4[['CM','PickupType']]

# Create a new column with the tuple of coordinates
df5['Coordinates'] = df5['CM'].apply(lambda p: (p.x, p.y))

# Group by 'Description' and 'Coordinates', and count occurrences
df6 = df5.groupby(['PickupType', 'Coordinates']).size().reset_index(name='Count')

# Drop the 'Coordinates' column and re-add the 'CM' column as Points
df6['CM'] = df6['Coordinates'].apply(lambda coord: Point(coord))
df6 = df6.drop(columns='Coordinates')

# Drop duplicates
df6 = df6.drop_duplicates()

# Convert to geopandas dataframe
gdf_tows = gdf_cits = geopandas.GeoDataFrame(df6, geometry='CM', crs="EPSG:4326")

# Generate and save plotmap
balt_plot_tow = gdf_tows.explore(location=(39.2904,-76.6122), width='100%', height='100%', zoom_start=15, tiles="CartoDB positron", color="red", marker_kwds=dict(radius=2))
balt_plot_tow.save('maps/templates/towing_plotmap.html')


### Road Map Creation
# Load Geospacial data (has all streets within city)
gdf = geopandas.read_file('Balt_shp/tl_2023_24510_roads.shp')
gdf2 = gdf
roads = gdf2.to_crs(epsg=32618)

#Assign Variable
towing_data = df4

# Get count of of towings per address
address_counter = Counter(towing_data['TowedFromLocation'])
address_counter_df = pd.DataFrame.from_dict(address_counter, orient='index').reset_index()
address_counter_df.columns = ['index', 'Count']

# Standardize to uppercase
address_counter_df['Address'] = address_counter_df['index'].str.upper()
roads['FULLNAME'] = roads['FULLNAME'].str.upper()

# Handle directional prefixes (U/B, O/S, E/S, etc.)
def clean_prefixes(address):
    address = re.sub(r'^(E\/S|O\/S|O\/UB|O\/D|U\/B|O\/|E\/SK|UNIT|W\/A)\s*', '', address) 
    return address

# Handle street number prefixes
def clean_st_num(address):
    address = re.sub(r'^\d*\s', '', address)
    return address

# Stardardize address suffixes (Saint is data speciic)
def clean_street_names(address):
    if address is not None:
        address = re.sub(r'\bSTREET\b', 'ST', address, flags=re.IGNORECASE)
        address = re.sub(r'\bAVENUE\b', 'AVE', address, flags=re.IGNORECASE)
        address = re.sub(r'\bSAINT\b', 'ST', address, flags=re.IGNORECASE)
    return address

# Street namers need to get more creative (Duplicate street names that are the same as streets with N/S/E/W aren't typically what is meant when data manually entered. N/S/E/W streets are typically in / closer to downtown and more likely to be what the data is refering to)
def change_duplicate_st_names(address):
    if address is not None:
        if address == "CALVERT ST":
            address = "CALVERT ST 2"
        elif address == "LINWOOD AVE":
            address = "LINWOOD AVE 2"
        elif address == "CENTRAL AVE":
            address = "CENTRAL AVE 2"
        elif address == "ELLAMONT ST":
            address = "ELLAMONT ST 2"
        elif address == "GAY ST":
            address = "GAY ST 2"
        elif address == "HAMBURG ST":
            address = "HAMBURG ST 2"
        elif address == "HAMILTON ST":
            address = "HAMILTON ST 2"
        elif address == "HIGHLAND AVE":
            address = "HIGHLAND AVE 2"
        elif address == "KENWOOD ST":
            address = "KENWOOD ST 2"
        elif address == "OLIVER ST":
            address = "OLIVER ST 2"
        elif address == "PACA ST":
            address = "PACA ST 2"
        elif address == "PATTERSON PARK AVE":
            address = "PATTERSON PARK AVE 2"
        elif address == "PLEASANT ST":
            address = "PLEASANT ST 2"
        elif address == "PRATT ST":
            address = "PRATT ST 2"
        elif address == "ROSEDALE ST":
            address = "ROSEDALE ST 2"
    return address

# Apply cleaning functions
address_counter_df['CleanAddress'] = address_counter_df['Address'].apply(clean_prefixes)
address_counter_df['CleanAddress'] = address_counter_df['CleanAddress'].apply(clean_st_num)
address_counter_df['CleanAddress'] = address_counter_df['CleanAddress'].apply(clean_street_names)

# Temporarily remove directionality (N, S, E, W) from both street names and addresses for matching
def remove_directionality(street_name):
    # Remove directionality (N, S, E, W) only if it appears as a prefix or suffix
    if street_name is not None:
        street_name = re.sub(r'^\b(N|S|E|W)\b\s+', '', street_name)  # Remove direction at start (e.g., "N Charles St")
        street_name = re.sub(r'\s+\b(N|S|E|W)\b$', '', street_name)  # Remove direction at end (e.g., "Charles St N")
        return street_name.strip()
    else:
        return street_name
    
# Apply additional cleaning functions
address_counter_df['StreetWithoutDir'] = address_counter_df['CleanAddress'].apply(remove_directionality)
roads['FULLNAME'] = roads['FULLNAME'].apply(change_duplicate_st_names)
roads['FULLNAME'] = roads['FULLNAME'].apply(clean_street_names)
roads['StreetWithoutDir'] = roads['FULLNAME'].apply(remove_directionality)

# Merge exact matches first
exact_matches_df = pd.merge(address_counter_df, roads, left_on='CleanAddress', right_on='FULLNAME', how='inner')
exact_matches_df = exact_matches_df.groupby(['FULLNAME','LINEARID'])['Count'].sum().reset_index()
exact_matches_df = exact_matches_df.drop("LINEARID", axis=1).drop_duplicates()

# Handle non-directional entries and distribute them
non_directional_df = address_counter_df[~address_counter_df['CleanAddress'].isin(roads['FULLNAME'])]

# Find matching streets for non-directional entries
def distribute_counts(street, count):
    # Find all streets that match the non-directional version
    roads2 = roads.drop(["geometry","LINEARID","RTTYP","MTFCC"], axis=1).drop_duplicates()
    possible_matches = roads2[roads2['StreetWithoutDir'] == street]

    # If matches are found, distribute the count equally
    if not possible_matches.empty:
        distributed_count = count / len(possible_matches)
        possible_matches['DistributedCount'] = round(float(distributed_count),0)
        return possible_matches[['FULLNAME', 'DistributedCount']]
    return pd.DataFrame()  # No match

# Apply distribution for non-directional entries
distributed_counts = pd.concat(
    [distribute_counts(row['StreetWithoutDir'], row['Count']) for _, row in non_directional_df.iterrows()]
)

# Standarize column names
exact_matches_df = exact_matches_df[['FULLNAME', 'Count']]
distributed_counts.columns = ['FULLNAME', 'Count']

# Combine both dataframes
final_df = pd.concat([exact_matches_df, distributed_counts])
final_df.rename(columns={'FULLNAME': 'Street Name'}, inplace=True)

# Group by street name and sum counts
final_counts_df = final_df.groupby('Street Name')['Count'].sum().reset_index()

#Standardize road dataframe to match final df
roads.rename(columns={'FULLNAME': 'Street Name'}, inplace=True)

# Merge final street counts back with the original StreetNames.csv on the Street Name column
result_df = pd.merge(roads, final_counts_df, on='Street Name', how='left')

# Fill missing counts with 0 (in case there were streets with no matches) and normalize on a 0-1 scale
result_df['Count'] = result_df['Count'].fillna(0)
result_df['Normalized'] = result_df['Count'] / max(result_df['Count'])

# Convert normalized count value to colormap hex
def convert_to_hex(val):
    if val == 0:
        #return mcolors.to_hex(cm.get_cmap('jet')(val))
        return "#ffffff00"
    else:
        return mcolors.to_hex(cm.get_cmap('gist_heat_r')(val))
    
# Apply colormapping
result_df["Color"] = result_df['Normalized'].apply(lambda x: convert_to_hex(x))

# Remove STATE HWYs and US HWYs (Often duplicates and not needed for this view)
result_df = result_df[~result_df['Street Name'].str.contains('STATE HWY', na=False)]
result_df = result_df[~result_df['Street Name'].str.contains('US HWY', na=False)]

m = folium.Map(location=(39.2904,-76.6122), width='100%', height='100%', zoom_start=15, tiles="CartoDB positron")
popup = folium.GeoJsonPopup(
    fields=["Street Name", "Count"],
    localize=True,
    labels=True)
folium.GeoJson(result_df, style_function= lambda x: {'color': x['properties']['Color']},popup=popup).add_to(m)
m.save('C:/Users/smwat/BaltParkWeb/maps/templates/towing_roadmap.html')