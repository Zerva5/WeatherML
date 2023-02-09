import pandas as pd

# JUST FOR TEMP AND PRECIP DATA

# cleaning temperature data
df = pd.read_pickle("temperature_rows.pkl")

# Get columns that are flags. We want to avoid these
flagCols = df.columns[df.columns.str.contains("Flag")][0:8]
#print(flagCols)

# Accept rows that don't have any flags relating to temperature set, flags usually mean bad news.
df_accepted = df[df[flagCols].notna().any(axis=1) == False]
df_rejected = df[df[flagCols].notna().any(axis=1) == True]

# hourlyStations = hourlyStations[['Name', 'Province', 'Station ID', 'LatitudeDEC', 'LongitudeDEC', 'Elevation', 'HLY First Year', 'HLY Last Year']]
#     hourlyStations.rename(columns = {'HLY First Year':'First Year', 'HLY Last Year':'Last Year'}, inplace=True)

df_accepted = df_accepted[['Longitude (x)', 'Latitude (y)', 'Year', 'Month', 'Day', 'Max Temp (°C)','Min Temp (°C)','Mean Temp (°C)','Heat Deg Days (°C)','Cool Deg Days (°C)','Total Rain (mm)','Total Snow (cm)','Total Precip (mm)']]

df_accepted.rename(columns={'Longitude (x)':'Longitude', 'Latitude (y)':'Latitude', 'Max Temp (°C)':'Max Temp','Min Temp (°C)':'Min Temp','Mean Temp (°C)':'Mean Temp','Heat Deg Days (°C)':'Heat Deg Days','Cool Deg Days (°C)':'Cool Deg Days','Total Rain (mm)':'Total Rain','Total Snow (cm)':'Total Snow','Total Precip (mm)':'Total Precip'}, inplace = True)


df.to_pickle("temp_data.pkl")
