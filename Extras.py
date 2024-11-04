import pandas as pd
import plotly.express as px
import datetime
import json

week_day_conv = {0:"Mon", 1:"Tue", 2:"Wed", 3:"Thu", 4:"Fri", 5:"Sat", 6:"Sun"}
car_conv = {
    "CHEVROLET": ["CHEVROLET", "CHEVR", "CHEV", "CHEVY", "CHEVEROLET", "CHEVEOLET", "CHVROLET", "CHEROLET", "CHEVROELT", "CHEVROET", "`CHEVROLET", "CHEVY TRAILBLAZ", "CHEVROLET VAN", "CHEVROLET TAXI", "CHEVROLET SEDAN", "CHEROLET", "CHEVROLER"],
    "LEXUS": ["LEXUS", "LLEXUS", "1LEXUS", "LEXU"],
    "NISSAN": ["NISSAN", "NISSA", "NIISAAN", "NISAN", "NISSSAN", "NISSSN", "NISSI"],
    "ACURA": ["ACURA", "`ACURA", "ACUUR"],
    "VOLKSWAGEN": ["VOLKSWAGEN", "VOLKSWAGON", "VOLKWAGEN", "VOLKS", "VOLKSWAGEN SW", "VOLKSWAGEN CONV", "VOLKSAWAGEN", "VOL KSWAGEN", "VW", "VOLKS WAGEN"],
    "TOYOTA": ["TOYOTA", "TOYOYA", "TOYOT", "TOYOTO", "`TOYOTA", "TOYOTA SW", "TOYOTA CONV", "TOYOTA SCION", "TOYOTA TAXI", "TTOYOTA", "TOYOTA (SILVER)", "TOYOTA (BLUE)"],
    "ALFA ROMEO": ["ALFA ROMEO", "ALFA", "ALPINA"],
    "AUDI": ["AUDI", "AUDU", "AUDI SW", "AUDI CONV", "AUDI   SW"],
    "BMW": ["BMW", "BMW SW", "BMW CONV", "BMWU"],
    "BUICK": ["BUICK", "BUICK SW"],
    "CADILLAC": ["CADILLAC", "CADIL", "CADILLAC CONV", "CADI"],
    "CHRYSLER": ["CHRYSLER", "CGRYSLER", "CHRYLSER", "CHRSYLER", "CHRYSLER CONV", "CHRYS"],
    "DODGE": ["DODGE", "DODGER", "DODGE RAM", "DODGE TOW TRK"],
    "MERCEDES": ["MERCEDES", "MERC", "MERCEDES S/W", "MERCDES", "MERCEDEDS", "MERCEDS", "MERCEDEZ", "MRECEDES", "`MERCEDES", "MERCEDES SW", "MERZ"],
    "HONDA": ["HONDA", "`HONDA", "HOND", "HONDA SW", "HONDA ACCORD", "HOINDA", "HONDA MC"],
    "MITSUBISHI": ["MITSUBISHI", "MITSUBISH", "MITSUBSIHI", "MITSUBSHI", "MITSUBISHUI", "MITUSUBISHI", "MITISUBISHI", "MITSHUBISHI", "MITS"],
    "HYUNDAI": ["HYUNDAI", "HYUNADI", "HYNUDAI", "HYNDAI", "HYUNDAL", "HYUND", "HYUNDA", "HYUNDA1", "HYUNDAI SW"],
    "VOLVO": ["VOLVO", "VOLVO SW", "VOLVO   SW", "VOLVO CONV"],
    "JEEP": ["JEEP", "JEEP ( WHITE)", "JEEP0"],
    "INFINITI": ["INFINITI", "INFINITE", "INFIN", "INFINTY", "INFIINITI", "INFINITTI", "INTINITI", "INFINIT"],
    "FORD": ["FORD", "FORF", "FORD SW", "FORD CONV", "FORDTAXI", "FORD CROWN VICT", "FORD TAXI", "FORD U-HAUL", "FORD  SW", "FORD  TAXI", "FORD UHAUL"],
    "GMC": ["GMC"],
    "MAZDA": ["MAZDA", "MAZAD", "MAZADA", "MAZDA CONV", "MADZA", "MAZDA 2"],
    "KIA": ["KIA", "KIA SW", "KAI", "KIS"],
    "SUBARU": ["SUBARU", "SUBURA", "SUBRU", "SUBAR", "SUBARU S/W", "SUBURAU"],
    "SCION": ["SCION", "SCIO", "SION", "SCION  TAXI"],
    "JAGUAR": ["JAGUAR", "JAGUA", "JAG"],
    "FIAT": ["FIAT", "FAIT"],
    "MERCURY": ["MERCURY", "MERCUCY", "MERCURY  SW", "MECURY", "MERCURY SW", "MERCURY VAN"],
    "MINI": ["MINI", "MINI COOPER", "MINI-COOPER", "MINI - COOPER", "MINI COPPER", "MINI- COOPER", "MINI COOPERCON", "MNI COOPER"],
    "PONTIAC": ["PONTIAC", "PONTI", "PONT"],
    "VOLKSWAGON": ["VOLKSWAGON"],
    "SMART": ["SMART", "SMART CAR"],
    "PORSCHE": ["PORSCHE", "PORS", "PORCH", "PORSHE"],
    "ALFA": ["ALFA"],
    "SAAB": ["SAAB", "SABB", "SSAB", "SAAB SW", "SAAB CONV"],
    "HUMMER": ["HUMMER"],
    "TESLA": ["TESLA", "TELSA"],
    "FERRARI": ["FERRARI"],
    "LAND ROVER": ["LAND ROVER", "LAND", "LAND ROBER", "LANDROVER", "LNDR", "RANGE ROVER", "RANGROVER", "RANGE"],
    "HARLEY DAVIDSON": ["HARLEY DAVIDSON", "HARLE"],
    "BENTLEY": ["BENTLEY", "BENTL"],
    "ISUZU": ["ISUZU", "ISUZI", "IZUZU", "ISUZU PU"],
    "OLDSMOBILE": ["OLDSMOBILE", "OLDSM", "OLDS", "OLDSMOMBILE"],
    "PLYMOUTH": ["PLYMOUTH", "PLYMO"],
    "LINCOLN": ["LINCOLN", "LINCO", "LINC", "LIN"],
    "MASERATI": ["MASER"],
    "INTERNATIONAL": ["INTER"],
    "FREIGHTLINER": ["FREIG"],
    "KENWORTH": ["KENWO", "KENW"],
    "TRIUMPH": ["TRIUM"],
    "DAEWOO": ["DAEWOO", "DAEWO"],
    "FISKER": ["FISKE"],
    "AERO": ["AERO"],
    "FUSO": ["FUSO"],
    "GEO": ["GEO"],
    "VICTORY": ["VICTORY"],
    "HINO": ["HINO"],
    "YAMAHA": ["YAMAH"]
}

# Import ticket and towing data
towing_data = pd.read_csv("Towing_csv.csv")
ticket_data = pd.read_csv("Ticketing_csv.csv")

# Filter only necessary columns
towing_data = towing_data[['VehicleMake','TowedDateTime']]
ticket_data = ticket_data[['Make','ViolDate']]

# Convert string to datetime
towing_data["TowedDateTime"] = pd.to_datetime(towing_data["TowedDateTime"])
ticket_data["ViolDate"] = pd.to_datetime(ticket_data["ViolDate"])

# Get weekday from datetime
towing_data["Day"] = towing_data["TowedDateTime"].apply(lambda x: week_day_conv.get(datetime.datetime.weekday(x)))
ticket_data["Day"] = ticket_data["ViolDate"].apply(lambda x: week_day_conv.get(datetime.datetime.weekday(x)))

# Get month from datetime
towing_data["Month"] = towing_data["TowedDateTime"].apply(lambda x: (x.strftime("%b")))
ticket_data["Month"] = ticket_data["ViolDate"].apply(lambda x: (x.strftime("%b")))

# Get hour from datetime
towing_data["Hour"] = towing_data["TowedDateTime"].apply(lambda x: int((x.strftime("%H"))))
ticket_data["Hour"] = ticket_data["ViolDate"].apply(lambda x: int((x.strftime("%H"))))

# Function to find actual car brand
def get_car_conv(car_entry):
    car_entry = car_entry.upper().strip()
    # Loop through the car_conv dictionary
    for correct_brand, variations in car_conv.items():
        # Check if the car_entry matches any of the variations
        if car_entry in variations:
            return correct_brand
    # If no match found, return the original name (or you could return "Unknown")
    return "Unknown"

# Applying the function to the 'Car Brand' column of the DataFrame
towing_data["Car"] = towing_data['VehicleMake'].apply(lambda x: get_car_conv(str(x)))
ticket_data["Car"] = ticket_data['Make'].apply(lambda x: get_car_conv(str(x)))

# Append both dataframes
towing_data["Data"] = "Towings"
ticket_data["Data"] = "Tickets"
all_data = pd.concat([towing_data, ticket_data])


### Day of the week Graph

# Get total count for each day
day_counts = all_data.groupby(['Day', 'Data']).size().reset_index(name='Count')

# Sort dataframe by day
sorted_weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
day_counts['Day'] = pd.Categorical(day_counts['Day'], sorted_weekdays)
day_counts = day_counts.sort_values("Day")

# Convert count to % of total (easier for graphing with two very different scales)
day_counts['Percent'] = round(100* day_counts['Count']/ day_counts.groupby('Data')['Count'].transform('sum'),2)

fig = px.bar(day_counts, x='Day', y='Percent', color='Data', 
             color_discrete_map={"Tickets": "#2f4b7c", "Towings": "#ffa600"},
             title='Tickets and Towings by Weekday',
             custom_data=['Count'],
             barmode='group') 
# Remove zooming ability
fig.layout.xaxis.fixedrange = True
fig.layout.yaxis.fixedrange = True

fig.update_layout(dragmode=False)

fig.update_layout(yaxis_title=None)
fig.update_layout(xaxis_title=None)
fig.update_layout(title='By Day')

# Remove legend
fig.update_layout(showlegend=False)

# Transparent background
fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)',})

#Adjust margins for viewing
fig.update_layout(
    margin=dict(l=20, r=20, t=25, b=20)
)

# Adjust hover font and background color
fig.update_layout(hoverlabel=dict(bgcolor="white",font_color="black"))

# Update y-axis to display %
fig.update_layout(yaxis_ticksuffix = '%')

# Set hover template for "Tickets" with the color of the bar in the first line
fig.update_traces(hovertemplate=
                  "<b style='color:#2f4b7c'>%{x}</b><br>" +  # First line in the color of the trace
                  "Percent: %{y:,.0}%<br>" +
                  "Total Count: %{customdata[0]}" +
                  "<extra></extra>",
                  selector=dict(name='Tickets'))

# Set hover template for "Towings" with the color of the bar in the first line
fig.update_traces(hovertemplate=
                  "<b style='color:#ffa600'>%{x}</b><br>" +  # First line in the color of the trace
                  "Percent: %{y:,.0}%<br>" +
                  "Total Count: %{customdata[0]}" +
                  "<extra></extra>",
                  selector=dict(name='Towings'))

graph_json = fig.to_json()

# Open the file in write mode ('w')
with open('C:/Users/smwat/BaltParkWeb/maps/templates/day_of_week.json', 'w') as outfile:
    # Parse the JSON string and write it to the file
    json.dump(json.loads(graph_json), outfile)


### Month Graph

# Get total count for each month
month_counts = all_data.groupby(['Month', 'Data']).size().reset_index(name='Count')

# Sort dataframe by month
sorted_months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
month_counts['Month'] = pd.Categorical(month_counts['Month'], sorted_months)
month_counts = month_counts.sort_values("Month")

# Convert count to % of total (easier for graphing with two very different scales)
month_counts['Percent'] = round(100* month_counts['Count']/ month_counts.groupby('Data')['Count'].transform('sum'),2)

fig = px.bar(month_counts, x='Month', y='Percent', color='Data', 
             color_discrete_map={"Tickets": "#2f4b7c", "Towings": "#ffa600"},
             title='Tickets and Towings by Month',
             custom_data=['Count'],
             barmode='group') 
# Remove zooming ability
fig.layout.xaxis.fixedrange = True
fig.layout.yaxis.fixedrange = True

fig.update_layout(dragmode=False)

fig.update_layout(yaxis_title=None)
fig.update_layout(xaxis_title=None)
fig.update_layout(title="By Month")

# Remove legend
fig.update_layout(showlegend=False)

# Transparent background
fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)',})

#Adjust margins for viewing
fig.update_layout(
    margin=dict(l=20, r=20, t=25, b=20)
)

# Adjust hover font and background color
fig.update_layout(hoverlabel=dict(bgcolor="white",font_color="black"))

# Update y-axis to display %
fig.update_layout(yaxis_ticksuffix = '%')

# Set hover template for "Tickets" with the color of the bar in the first line
fig.update_traces(hovertemplate=
                  "<b style='color:#2f4b7c'>%{x}</b><br>" +  # First line in the color of the trace
                  "Percent: %{y:,.0}%<br>" +
                  "Total Count: %{customdata[0]}" +
                  "<extra></extra>",
                  selector=dict(name='Tickets'))

# Set hover template for "Towings" with the color of the bar in the first line
fig.update_traces(hovertemplate=
                  "<b style='color:#ffa600'>%{x}</b><br>" +  # First line in the color of the trace
                  "Percent: %{y:,.0}%<br>" +
                  "Total Count: %{customdata[0]}" +
                  "<extra></extra>",
                  selector=dict(name='Towings'))

graph_json = fig.to_json()

# Open the file in write mode ('w')
with open('C:/Users/smwat/BaltParkWeb/maps/templates/month.json', 'w') as outfile:
    # Parse the JSON string and write it to the file
    json.dump(json.loads(graph_json), outfile)


### Hour Graph

# Get total count for each hour
hour_counts = all_data.groupby(['Hour', 'Data']).size().reset_index(name='Count')

# Sort dataframe by hour
hour_counts = hour_counts.sort_values("Hour")

# Convert count to % of total (easier for graphing with two very different scales)
hour_counts['Percent'] = round(100* hour_counts['Count']/ hour_counts.groupby('Data')['Count'].transform('sum'),2)

time_dict = {
    1: "1AM", 2: "2AM", 3: "3AM", 4: "4AM", 5: "5AM", 6: "6AM", 7: "7AM", 8: "8AM", 9: "9AM", 10: "10AM", 11: "11AM", 12: "12PM",
    13: "1PM", 14: "2PM", 15: "3PM", 16: "4PM", 17: "5PM", 18: "6PM", 19: "7PM", 20: "8PM", 21: "9PM", 22: "10PM", 23: "11PM", 0: "12AM"
}

hour_counts["Time"] = hour_counts["Hour"].apply(lambda x: time_dict.get((x)))

fig = px.scatter(hour_counts, x='Time', y='Percent', color='Data', 
             color_discrete_map={"Tickets": "#2f4b7c", "Towings": "#ffa600"},
             title='Tickets and Towings by Hour',
             custom_data=['Count'],
             ) 
# Remove zooming ability
fig.layout.xaxis.fixedrange = True
fig.layout.yaxis.fixedrange = True

fig.update_layout(dragmode=False)

fig.update_layout(yaxis_title=None)
fig.update_layout(xaxis_title=None)
fig.update_layout(title='By Hour')

# Remove legend
fig.update_layout(showlegend=False)

# Transparent background
fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)',})

#Adjust margins for viewing
fig.update_layout(
    margin=dict(l=20, r=20, t=25, b=20)
)

# Adjust hover font and background color
fig.update_layout(hoverlabel=dict(bgcolor="white",font_color="black"))

# Update y-axis to display %
fig.update_layout(yaxis_ticksuffix = '%')

#Add graph lines and smoothing
fig.update_traces(mode='lines', line_shape='spline')

# Set hover template for "Tickets" with the color of the bar in the first line
fig.update_traces(hovertemplate=
                  "<b style='color:#2f4b7c'>%{x}</b><br>" +  # First line in the color of the trace
                  "Percent: %{y:,.0}%<br>" +
                  "Total Count: %{customdata[0]}" +
                  "<extra></extra>",
                  selector=dict(name='Tickets'))

# Set hover template for "Towings" with the color of the bar in the first line
fig.update_traces(hovertemplate=
                  "<b style='color:#ffa600'>%{x}</b><br>" +  # First line in the color of the trace
                  "Percent: %{y:,.0}%<br>" +
                  "Total Count: %{customdata[0]}" +
                  "<extra></extra>",
                  selector=dict(name='Towings'))

graph_json = fig.to_json()

# Open the file in write mode ('w')
with open('C:/Users/smwat/BaltParkWeb/maps/templates/hour.json', 'w') as outfile:
    # Parse the JSON string and write it to the file
    json.dump(json.loads(graph_json), outfile)


### Car Graph

# Get total count for each hour
car_counts = all_data.groupby(['Car', 'Data']).size().reset_index(name='Count')

# Sort dataframe by hour
car_counts = car_counts.sort_values(by="Count", ascending=False)

top_list = list(car_counts['Car'][~(car_counts['Car']=="Unknown")].unique()[0:15])
print(top_list, type(top_list))

car_counts_top = car_counts[car_counts['Car'].isin(top_list)]

car_counts_top['Count'] = car_counts_top.apply(
    lambda row: -row['Count'] if row['Data'] == 'Towings' else row['Count'],
    axis=1
)

# Convert count to % of total (easier for graphing with two very different scales)
car_counts_top['Percent'] = round(100* car_counts_top['Count']/ car_counts_top.groupby('Data')['Count'].transform('sum'),2)
print(car_counts_top)

car_counts_top['Percent'] = car_counts_top.apply(
    lambda row: -row['Percent'] if row['Data'] == 'Towings' else row['Percent'],
    axis=1
)

car_counts_top['AbsolutePercent'] = car_counts_top['Percent'].abs()
car_counts_top['AbsoluteCount'] = car_counts_top['Count'].abs()

# Create the horizontal bar chart with separate positive and negative bars
fig = px.bar(car_counts_top, y='Car', x='Percent', color='Data',  # Swap 'x' and 'y' for horizontal
             title='Tickets and Towings by Car',
             labels={'Car': 'Car', 'Percent': 'Percent', 'Count': 'Total Count', 'Data': 'Data'},
             orientation='h',  # Horizontal bar chart
             color_discrete_map={"Tickets": "#2f4b7c", "Towings": "#ffa600"},
             barmode='relative',   # Bars on either side of axis
             custom_data=['AbsoluteCount', 'AbsolutePercent']
             ) 

# Remove legend
fig.update_layout(showlegend=False)

#Adjust margins for viewing
fig.update_layout(
    margin=dict(l=20, r=20, t=25, b=20)
)

# Remove zooming ability
fig.layout.xaxis.fixedrange = True
fig.layout.yaxis.fixedrange = True

fig.update_layout(dragmode=False)

fig.update_layout(yaxis_title=None)
fig.update_layout(xaxis_title=None)
fig.update_layout(title='By Car')

# Adjust hover templates
fig.update_traces(hovertemplate=
                  "<b style='color:#2f4b7c'>%{y}</b><br>" +
                  "Tickets Percent: %{x}%<br>" +
                  "Total Count: %{customdata[0]}" +
                  "<extra></extra>",
                  selector=dict(name='Tickets'))

fig.update_traces(hovertemplate=
                  "<b style='color:#ffa600'>%{y}</b><br>" +
                  "Towings Percent: %{customdata[1]}%<br>" +
                  "Total Count: %{customdata[0]}" +
                  "<extra></extra>",
                  selector=dict(name='Towings'))

# Adjust x-axis to center the y-axis
max_abs_count = car_counts_top['Percent'].abs().max()  # Get the max absolute count value for scaling

fig.update_layout(
    xaxis=dict(
        range=[-20, 20],  # Set the range to fit -20% to 20%
        tickvals=[-20, -15, -10, -5, 0, 5, 10, 15, 20],  # Custom tick positions
        ticktext=["20%", "15%", "10%", "5%", "0%", "5%", "10%", "15%", "20%"],  # Custom labels
        zeroline=True,  # Add a line at x=0 (center)
        zerolinecolor='black',  # Make the center line black
        zerolinewidth=2,  # Width of the center line
        fixedrange=True  # Prevent zooming
    ),
    yaxis=dict(
        title='',  # Optional: Remove the y-axis title to avoid overlap
        autorange="reversed",  # Reverse the y-axis to keep car names in the correct order
    )
)

# Transparent background
fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)',})

# Adjust hover font and background color
fig.update_layout(hoverlabel=dict(bgcolor="white",font_color="black"))



graph_json = fig.to_json()

# Open the file in write mode ('w')
with open('C:/Users/smwat/BaltParkWeb/maps/templates/car.json', 'w') as outfile:
    # Parse the JSON string and write it to the file
    json.dump(json.loads(graph_json), outfile)



