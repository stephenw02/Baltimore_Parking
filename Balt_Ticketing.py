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
import tracemalloc

tracemalloc.start()

warnings.filterwarnings("ignore")


### Import any new data from source and load into database
# Set the DJANGO_SETTINGS_MODULE to point to your settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'baltparkweb.settings')
django.setup()

from maps.models import ProcessedDataLog, TicketingRecord  # Import the model for storing last objectId

#TicketingRecord.objects.all().delete()
#ProcessedDataLog.objects.filter(dataset_name="TicketingDataset").delete()

# Base URL for the API
base_url = "https://services1.arcgis.com/UWYHeuuJISiGmgXx/arcgis/rest/services/Finance_Parking_Fines/FeatureServer/0/query"

# Get the latest processed objectId from the database
def get_last_object_id():
    log = ProcessedDataLog.objects.filter(dataset_name="TicketingDataset").first()
    if log:
        print(f"Last processed object ID: {log.last_object_id}")
        return log.last_object_id
    else:
        print("No processed data log found, starting from scratch.")
        return None

# Fetch new data by querying from the latest objectId
def fetch_new_data(url, last_object_id, batch_size=1000):
    print("last object ID: ", last_object_id)
    
    # If last_object_id exists, query only for new records
    where_clause = f"ESRI_OID > {last_object_id}" if last_object_id else "ESRI_OID > 0"
    print(f"Fetching new data with where_clause: {where_clause}")
    
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
    print("Items to process: ", data['objectIds'])
    
    if data['objectIds'] != []:
        object_ids = data['objectIds']
        object_ids.sort()
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
                if row.ViolDate == None:
                    print("No Date Entered")
                elif datetime.fromtimestamp(int(row.ViolDate)/1000) > datetime(2021, 1, 1, 0, 1):
                    TicketingRecord.objects.create(
                        Citation=row.Citation,
                        Tag=row.Tag,
                        ExpMM=row.ExpMM,
                        ExpYY=row.ExpYY,
                        State=row.State,
                        Make=row.Make,
                        Address=row.Address,
                        ViolCode=row.ViolCode,
                        Description=row.Description,
                        ViolFine=row.ViolFine,
                        ViolDate=row.ViolDate,
                        Balance=row.Balance,
                        PenaltyDate=row.PenaltyDate,
                        OpenFine=row.OpenFine,
                        OpenPenalty=row.OpenPenalty,
                        NoticeDate=row.NoticeDate,
                        InvestigationStatus=row.InvestigationStatus,
                        TrialStatus=row.TrialStatus,
                        GeneralStatus=row.GeneralStatus,
                        GroupID=row.GroupID,
                        ImportDate=row.ImportDate,
                        Neighborhood=row.Neighborhood,
                        PoliceDistrict=row.PoliceDistrict,
                        CouncilDistrict=row.CouncilDistrict,
                        Location=row.Location,
                        HashedRecord=row.HashedRecord,
                        NeedsSync=row.NeedsSync,
                        isDeleted=row.isDeleted,
                        ESRI_OID=row.ESRI_OID
                    )
                else:
                    print("Date before 2021. Not saving to database")

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
        log, created = ProcessedDataLog.objects.get_or_create(dataset_name="TicketingDataset")
        log.last_object_id = max_object_id
        log.save()

        print(f"Updated last processed object ID to: {max_object_id}")

        # Pause between batches to avoid overloading the server
        sleep(2)
    
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
records = TicketingRecord.objects.all().values()

# Convert the queryset to a list of dictionaries
records_list = list(records)

# Convert the list of dictionaries to a Pandas DataFrame
df = pd.DataFrame(records_list)




### Clean Data
# Convert datetime string to datatime type
df["ViolDate"] = pd.to_datetime(df["ViolDate"], unit='ms', errors='coerce')

# List of relevant descriptions
desc_list = ['No Stop/Park Street Cleaning','No Stopping/Standing Not Tow-Away Zone','All Other Stopping or Parking Violations','All Other Parking Meter Violations','Passenger Loading Zone','No Stopping/Standing Tow Away Zone','Residential Parking Permit Only','Blocking Garage or Driveway','No Stop/Stand/Park Cruising','Res. Park Permit 2nd Offense','Res. Park Permit 4th Offense','Res. Park Permit 3rd Offense','Parking or Parking Meter Tow-Away zone','No Stopping/Parking Stadium Event – 33rd','No Stopping or No Parking Pimlico Event','No Stopping//Parking Stadium Event Camden']

# Filter out nulls, date outside of scope, and descriptions outside of scope
df2 = df[ (df["Description"].isin(desc_list)) & (df["ViolDate"]>"1/1/2024 0:00:01 AM") & (df["Address"].notnull()) ]
df2 = df2[~df2.Address.str.startswith('0')]

# Remove address prefixes and and city and state
df2['AddressTrim'] = df2['Address'].str.replace(r'^(E/S|O/S|O/UB|O/D|U/B|O/)\s*', '', regex=True)
df2['AddressFull'] = df2['AddressTrim'].astype(str) + ', Baltimore, MD'

# Load the dictionary from the JSON file
with open('address_data.json', 'r') as json_file:
    add_geo_dict = json.load(json_file)

def add_directionality(input):
    input_parts = input.split(" ")
    
    # Check if the first part is a number (street number)
    if input_parts[0].isdigit():
        # If the second part is already a direction, return as-is
        if input_parts[1].upper() in ["N", "S", "E", "W"]:
            return input
    # If the input starts with a direction (like "N Charles St"), return as-is
    elif input_parts[0].upper() in ["N", "S", "E", "W"]:
        return input

    # Monument St: 50% E / 50% W for Street Numbers <=600, 100% E for Street Numbers > 600
    if "MONUMENT ST" in input.upper():
        if len(input_parts) > 1 and input_parts[0].isdigit():
            street_number = int(input_parts[0])
            if street_number <= 600:
                direction = "E" if street_number % 2 == 0 else "W"
            else:
                direction = "E"
            input_parts.insert(1, direction)
        else:
            direction = "E" if hash(input) % 2 == 0 else "W"
            input_parts.insert(0, direction)

    # Castle St: 50% N / 50% S for all Street Numbers
    elif "CASTLE ST" in input.upper():
        direction = "N" if hash(input) % 2 == 0 else "S"
        if len(input_parts) > 1 and input_parts[0].isdigit():
            input_parts.insert(1, direction)
        else:
            input_parts.insert(0, direction)

    # Central Ave: 25% N / 75% S for all Street Numbers
    elif "CENTRAL AVE" in input.upper():
        direction = "N" if hash(input) % 4 == 0 else "S"
        if len(input_parts) > 1 and input_parts[0].isdigit():
            input_parts.insert(1, direction)
        else:
            input_parts.insert(0, direction)

    # Exeter St: 100% S for all Street Numbers
    elif "EXETER ST" in input.upper():
        if len(input_parts) > 1 and input_parts[0].isdigit():
            input_parts.insert(1, "S")
        else:
            input_parts.insert(0, "S")

    # Calvert St: 100% S for Street Numbers <=300, 100% N for Street Numbers > 300
    elif "CALVERT ST" in input.upper():
        if len(input_parts) > 1 and input_parts[0].isdigit():
            street_number = int(input_parts[0])
            direction = "S" if street_number <= 300 else "N"
            input_parts.insert(1, direction)
        else:
            input_parts.insert(0, "S")

    # Chase St: 50% W / 50% E for all Street Numbers > 1, 100% E for Street Numbers <=1
    elif "CHASE ST" in input.upper():
        if len(input_parts) > 1 and input_parts[0].isdigit():
            street_number = int(input_parts[0])
            if street_number > 1:
                direction = "W" if hash(input) % 2 == 0 else "E"
            else:
                direction = "E"
            input_parts.insert(1, direction)
        else:
            direction = "W" if hash(input) % 2 == 0 else "E"
            input_parts.insert(0, direction)

    # Fayette St: 50% W / 50% E for Street Numbers <=2700, 100% E for Street Numbers > 2700
    elif "FAYETTE ST" in input.upper():
        if len(input_parts) > 1 and input_parts[0].isdigit():
            street_number = int(input_parts[0])
            if street_number <= 2700:
                direction = "W" if hash(input) % 2 == 0 else "E"
            else:
                direction = "E"
            input_parts.insert(1, direction)
        else:
            direction = "W" if hash(input) % 2 == 0 else "E"
            input_parts.insert(0, direction)

    # Read St: 50% E / 50% W for all Street Numbers
    elif "READ ST" in input.upper():
        direction = "E" if hash(input) % 2 == 0 else "W"
        if len(input_parts) > 1 and input_parts[0].isdigit():
            input_parts.insert(1, direction)
        else:
            input_parts.insert(0, direction)

    # Eutaw St: 50% N / 50% S for Street Numbers <=300, 100% N for Street Numbers > 300
    elif "EUTAW ST" in input.upper():
        if len(input_parts) > 1 and input_parts[0].isdigit():
            street_number = int(input_parts[0])
            direction = "N" if street_number > 300 else "S"
            input_parts.insert(1, direction)
        else:
            direction = "N" if hash(input) % 2 == 0 else "S"
            input_parts.insert(0, direction)

    # Green St: 50% N / 50% S for all Street Numbers
    elif "GREEN ST" in input.upper():
        direction = "N" if hash(input) % 2 == 0 else "S"
        if len(input_parts) > 1 and input_parts[0].isdigit():
            input_parts.insert(1, direction)
        else:
            input_parts.insert(0, direction)

    # Lexington St: 100% E for all Street Numbers
    elif "LEXINGTON ST" in input.upper():
        if len(input_parts) > 1 and input_parts[0].isdigit():
            input_parts.insert(1, "E")
        else:
            input_parts.insert(0, "E")

    # Barre St: 50% E / 50% W for Street Numbers <=200, 100% W for Street Numbers > 200
    elif "BARRE ST" in input.upper():
        if len(input_parts) > 1 and input_parts[0].isdigit():
            street_number = int(input_parts[0])
            direction = "W" if street_number > 200 else ("E" if hash(input) % 2 == 0 else "W")
            input_parts.insert(1, direction)
        else:
            direction = "E" if hash(input) % 2 == 0 else "W"
            input_parts.insert(0, direction)

    # Paca St: 50% N / 50% S for all Street Numbers
    elif "PACA ST" in input.upper():
        direction = "N" if hash(input) % 2 == 0 else "S"
        if len(input_parts) > 1 and input_parts[0].isdigit():
            input_parts.insert(1, direction)
        else:
            input_parts.insert(0, direction)

    # Lanvale St: 50% E / 50% W for all Street Numbers
    elif "LANVALE ST" in input.upper():
        direction = "E" if hash(input) % 2 == 0 else "W"
        if len(input_parts) > 1 and input_parts[0].isdigit():
            input_parts.insert(1, direction)
        else:
            input_parts.insert(0, direction)

    # Cross St: 80% E / 20% W for Street Numbers <=700, 100% W for Street Numbers > 700
    elif "CROSS ST" in input.upper():
        if len(input_parts) > 1 and input_parts[0].isdigit():
            street_number = int(input_parts[0])
            if street_number > 700:
                direction = "W"
            else:
                direction = "E" if hash(input) % 5 != 0 else "W"
            input_parts.insert(1, direction)
        else:
            direction = "E" if hash(input) % 5 != 0 else "W"
            input_parts.insert(0, direction)

    # Washington St: 75% N / 25% S for Street Numbers <=800, 100% N for Street Numbers > 800
    elif "WASHINGTON ST" in input.upper():
        if len(input_parts) > 1 and input_parts[0].isdigit():
            street_number = int(input_parts[0])
            if street_number > 800:
                direction = "N"
            else:
                direction = "N" if hash(input) % 4 != 0 else "S"
            input_parts.insert(1, direction)
        else:
            direction = "N" if hash(input) % 4 != 0 else "S"
            input_parts.insert(0, direction)

    # Pleasant St: 50% E / 50% W for all Street Numbers
    elif "PLEASANT ST" in input.upper():
        direction = "E" if hash(input) % 2 == 0 else "W"
        if len(input_parts) > 1 and input_parts[0].isdigit():
            input_parts.insert(1, direction)
        else:
            input_parts.insert(0, direction)

    # Lafayette Ave: 50% E / 50% W for Street Numbers <=500, 100% W for Street Numbers > 500
    elif "LAFAYETTE AVE" in input.upper():
        if len(input_parts) > 1 and input_parts[0].isdigit():
            street_number = int(input_parts[0])
            if street_number > 500:
                direction = "W"
            else:
                direction = "E" if hash(input) % 2 == 0 else "W"
            input_parts.insert(1, direction)
        else:
            direction = "E" if hash(input) % 2 == 0 else "W"
            input_parts.insert(0, direction)

    elif "BROADWAY" in input.upper():
        direction = "N" if hash(input) % 2 == 0 else "S"
        if len(input_parts) > 1 and input_parts[0].isdigit():
            input_parts.insert(1, direction)
        else:
            input_parts.insert(0, direction)

    elif "LIBERTY ST" in input.upper():
        if len(input_parts) > 1 and input_parts[0].isdigit():
            input_parts.insert(1, "N")
        else:
            input_parts.insert(0, "N")

    elif "MADISON ST" in input.upper():
        direction = "E" if hash(input) % 2 == 0 else "W"
        if len(input_parts) > 1 and input_parts[0].isdigit():
            input_parts.insert(1, direction)
        else:
            input_parts.insert(0, direction)

    elif "CHARLES ST" in input.upper() and not any(char in input.upper() for char in ["N CHARLES ST", "S CHARLES ST"]):
        # Check if the first part is a street number and adjust based on the value
        if input_parts[0].isdigit():  # Check if the first part is the street number
            street_number = int(input_parts[0])
            if street_number >= 2000:
                input_parts.insert(1, "N")  # Add 'N' for numbers >= 2000
            else:
                input_parts.insert(1, "S")  # Add 'S' for numbers < 2000

    return " ".join(input_parts)

def get_GeoCoords(input, x):
    # Apply directionality function
    input2 = add_directionality(input)
    # Check if address is already in dictionary of known coords
    if input2 in add_geo_dict.keys():
        #print(x, " - ", input2, " : " , add_geo_dict[input2])
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
        
# Apply geocoordinate function
df2["AddressCoords"] = df2.apply(lambda x: get_GeoCoords(x['AddressFull'], x.name), axis=1)

# Save the dictionary as a JSON file
with open('address_data.json', 'w') as json_file:
    json.dump(add_geo_dict, json_file)



# Filter out nan values
df3 = df2[ (df2['AddressCoords'] != "") ]

df3["AddressCoords"] = df3["AddressCoords"].astype(str)

# Format coordinates now that they're strings
df3["AddressCoords"] = df3.apply(lambda x: x["AddressCoords"].replace("[","").replace("]","").split(","), axis=1)

# Format coordinates as shapely points and round to save space
df3["CM"] = df3.apply(lambda x: (Point( round(float(x["AddressCoords"][0]),6), round(float(x["AddressCoords"][1]),6) )), axis=1)

# Export for Extras
df3.to_csv("Ticketing_csv.csv")

### Plot Map Creation
# Drop unnecessary columns
df4= df3[['CM','Description']]

# Create a new column with the tuple of coordinates
df4['Coordinates'] = df4['CM'].apply(lambda p: (p.x, p.y))

# Group by 'Description' and 'Coordinates', and count occurrences
df5 = df4.groupby(['Description', 'Coordinates']).size().reset_index(name='Count')

# Drop the 'Coordinates' column and re-add the 'CM' column as Points
df5['CM'] = df5['Coordinates'].apply(lambda coord: Point(coord))
df5 = df5.drop(columns='Coordinates')

# Drop duplicates
df5 = df5.drop_duplicates()

# Load data as geopandas dataframe
gdf_cits = geopandas.GeoDataFrame(df5, geometry='CM', crs="EPSG:4326")
ticket_plotmap = gdf_cits.explore(location=(39.2904,-76.6122), width='100%', height='100%', zoom_start=15, tiles="CartoDB positron", color="red", marker_kwds=dict(radius=2))
ticket_plotmap.save('maps/templates/ticket_plotmap.html')



### Heat Map Creation
# Create list of coordinates
coords_list =  df3.apply(lambda x: (x["AddressCoords"][1], x["AddressCoords"][0]), axis=1)

# Get count of coordinate occurances
coords_counter = Counter(coords_list)

# Create a list of coordinates with intensity (count of occurrences)
heatmap_data = [[coord[0], coord[1], count/max(coords_counter.values())] for coord, count in coords_counter.items()]

m = folium.Map(location=(39.2904,-76.6122), width='100%', height='100%', zoom_start=15, tiles="CartoDB positron")
plugins.HeatMap(heatmap_data, radius=17, blur=23, min_opacity=0.5).add_to(m)
m.save('maps/templates/ticket_heatmap.html')



### Road Map Creation
# Load Geospacial data (has all streets within city)
gdf = geopandas.read_file('Balt_shp/tl_2023_24510_roads.shp')
gdf2 = gdf
roads = gdf2.to_crs(epsg=32618)

#Assign variable
ticket_data = df3

# Get count of of towings per address
address_counter = Counter(ticket_data['Address'])
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
#print(distributed_counts)

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
m.save('C:/Users/smwat/BaltParkWeb/maps/templates/ticket_roadmap.html')

print(tracemalloc.get_traced_memory())
tracemalloc.stop()