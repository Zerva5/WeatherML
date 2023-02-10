from ctypes import ArgumentError
import pandas as pd
import urllib.request

import os
import multiprocessing

def days_in_month(month):
    if month in [1, 3, 5, 7, 8, 10, 12]:
        return 31
    elif month in [4, 6, 9, 11]:
        return 30
    elif month == 2:
        return 28
    return -1

province_list = ['BRITISH COLUMBIA', 'YUKON TERRITORY', 'NORTHWEST TERRITORIES', 'NUNAVUT',
                 'ALBERTA', 'SASKATCHEWAN', 'MANITOBA', 'ONTARIO', 'QUEBEC', 'NEW BRUNSWICK'
                 'NOVA SCOTIA', 'PRINCE EDWARD ISLAND', 'NEWFOUNDLAND']
urlBase = "https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID={stationId}&Year={year}&Month={month}&Day=14&timeframe={tf}&submit=Download+Data" 



def getStations(path:str, province:str = "ALL"):
    # make sure valid province
    if province not in province_list and province != "ALL":
        raise ArgumentError("Bad province argument " + province + ", must be one of: " + str(province_list))
    
    df = pd.read_csv(path)

    # Select province
    if province != "ALL":
        df = df[df['Province'] == province]

    # Get hourly stations, trim unneeded columns
    hourlyStations = df[df['HLY First Year'].notna()]
    hourlyStations = hourlyStations[['Name', 'Province', 'Station ID', 'LatitudeDEC', 'LongitudeDEC', 'Elevation', 'HLY First Year', 'HLY Last Year']]
    hourlyStations.rename(columns = {'HLY First Year':'First Year', 'HLY Last Year':'Last Year'}, inplace=True)

    # get daily stations, trim uneeded cols
    dailyStations = df[df['DLY First Year'].notna()]
    dailyStations = dailyStations[['Name', 'Province', 'Station ID', 'LatitudeDEC', 'LongitudeDEC', 'Elevation', 'DLY First Year', 'DLY Last Year']]
    dailyStations.rename(columns = {'DLY First Year':'First Year', 'DLY Last Year':'Last Year'}, inplace=True) #


    
    return hourlyStations, dailyStations




def download_url(queue):
    while True:
        url, outname = queue.get()

        #async with semaphore:
        try:
            urllib.request.urlretrieve(url, filename=outname)
        except TimeoutError as err:
            print("Timeout error!")
        except Exception as err:
            print("some other error:", err)
        
        queue.task_done()

    queue.task_done()

def addToQueue(data, prefix: str, queue, fileFormat: str, timeframe: str):
    tfList = {"H":1, "D":2}

    if(timeframe != "H" and timeframe != "D"):
        raise ArgumentError("Timeframe must be H or D!")
    
    if(fileFormat not in ["csv"]):
        raise ArgumentError("Bad fileformat argument!")

    
    # Timeframes: 1 is hourly, 2 is daily
    
    count = 0
    for rowIndex in range(data.shape[0]):
        row = data.iloc[[rowIndex]]

        stationID = int(row['Station ID'].item())
        startYear = int(row['First Year'].item())
        endYear = int(row['Last Year'].item())

        for y in range(startYear, endYear + 1):
            url = urlBase.format(stationId=stationID, year=y, tf=tfList[timeframe], ftype=fileFormat)
            filename = prefix + "/{Id}_y{year}.{ftype}".format(Id=stationID, year=y, ftype=fileFormat)
            if not os.path.exists(filename):
                queue.put((url, filename))
                count += 1
    return count

def main():
    WORKER_COUNT = 80
    
    queue = multiprocessing.JoinableQueue()
    workers = [multiprocessing.Process(target=download_url, args=(queue,)) for _ in range(WORKER_COUNT)]
    for worker in workers:
        worker.start()

    fileCount = 0
    dailyCount = 0
    hourlyCount = 0
    hourly, daily = getStations("Station Inventory EN.csv", "BRITISH COLUMBIA")

    # hourlyCount = addToQueue(hourly, "hourly", queue, "csv", "H")
    # dailyCount = addToQueue(daily, "daily", queue, "csv", "D")



    # for rowIndex in range(daily.shape[0]):
    #     row = daily.iloc[[rowIndex]]

    #     stationID = int(row['Station ID'].item())
    #     startYear = int(row['First Year'].item())
    #     endYear = int(row['Last Year'].item())

    #     for y in range(startYear, endYear + 1):
    #         url = urlBase.format(stationId=stationID, year=y, tf=2, month=1)
    #         filename = "daily/{id}_y{year}.csv".format(id=stationID, year=y)
    #         if not os.path.exists(filename):
    #             queue.put((url, filename))
    #             dailyCount += 1

    # print(hourly.shape)
    # print(daily.shape)
    for rowIndex in range(hourly.shape[0]):
        row = hourly.iloc[[rowIndex]]

        stationID = int(row['Station ID'].item())
        startYear = int(row['First Year'].item())
        endYear = int(row['Last Year'].item())

        for y in range(startYear, endYear + 1):
            for m in range(1,12 + 1):

                url = urlBase.format(stationId=stationID, year=y, tf=1, month=m)
                filename = "hourly/{id}_y{year}_m{month}.csv".format(id=stationID, year=y, month=m)
                if not os.path.exists(filename):
                    queue.put((url, filename))
                    hourlyCount += 1


    print("Starting download of", hourlyCount + dailyCount, "files. Daily:", dailyCount, ", Hourly:", hourlyCount)
    #print("starting...")
    queue.join()
    for worker in workers:
        worker.terminate()
    #print(fileCount)            # 
                
  

main()
