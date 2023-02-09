from ctypes import ArgumentError
import multiprocessing
import pathlib
import pandas as pd
import numpy as np
import os
import time
from collections import namedtuple
from pandas.core.window.ewm import template_header

# go through all the CSV's and all the rows. Save all rows that have temp info. Go through and save all rows that have wind info
# See how many have both?

## WE want to have 3 pickles by the end:
# Just the temp
# Just the wind
# Both
# Should be no duplication between the 3


def worker_func(shared_list, sharedValues, lock, queue):

    totalFiles = 0
    totalRows = 0
    acceptedRows = 0
    
    while True:
        filename, rootPath, requiredColumns = queue.get()


        try:
            df, totalRows = process_file(filename, rootPath, requiredColumns)

            shared_list.append(df)

            accepted = df.shape[0]

            printNow=False

            with lock:
                sharedValues.totalFiles.value += 1
                sharedValues.totalRows.value += totalRows
                sharedValues.acceptedRows.value += accepted
            
                if(sharedValues.totalFiles.value % 1000 == 0):
                    printNow = True
                    totalFiles = sharedValues.totalFiles.value
                    totalRows = sharedValues.totalRows.value
                    acceptedRows = sharedValues.acceptedRows.value
                

            if printNow:
                print("{} files have been processed. Processed {} rows total, accepted {} ({:.2f}%)".format(totalFiles,totalRows,
                                                                                                        acceptedRows, acceptedRows/totalRows * 100))
        except Exception as e:
            print("Worker exception:", e)


        queue.task_done()

    queue.task_done()

def process_file(filename, rootPath, requiredColumns):
    try:
        tempdf = pd.read_csv(rootPath + "/" + filename)
    except Exception as e:
        print("some error", e)
        return None,0

                     
    try:
        if(len(requiredColumns) != 0):
            temprows = tempdf[tempdf[requiredColumns].notna().all(axis=1)]
        else:
            temprows = tempdf

        totalRows = tempdf.shape[0]
        #shared_list.append(temprows)
             
    except Exception as e:
        print(filename, "- some error")
        print(e)
        return None,0

    return temprows, totalRows
    

def hourly(rootPath, requiredColumns:list, processLimit = 500, maxFiles = 0):
    startTime = time.time()
    
    SharedValues = namedtuple("SharedValues", "totalRows totalFiles acceptedRows")

    directory = os.fsencode(rootPath)

    queue = multiprocessing.JoinableQueue()


    manager = multiprocessing.Manager()
    shared_list = manager.list()
    
    shared_count = manager.Value('i', 0)
    totalRows = manager.Value('i', 0)
    acceptedRows = manager.Value('i', 0)

    sharedValues = SharedValues(totalRows, shared_count, acceptedRows)
    
    lock = manager.Lock()

    workers = [multiprocessing.Process(target=worker_func, args=(shared_list, sharedValues, lock, queue,)) for _ in range(processLimit)]
    for worker in workers:
        worker.start()

    fcount = 0

    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        queue.put((filename, rootPath, requiredColumns))

        fcount += 1
        if fcount == maxFiles:
            break

    queue.join()

    endTime = time.time()

    
    for worker in workers:
        worker.terminate()

    print("Finished reading and selecting from file, took {:.2f} minutes.\nstarting the final concat".format((endTime - startTime) / 60))

    df_temp = pd.concat(shared_list, ignore_index=True)
    endTime = time.time()
    print("Done concat. Total time: {:.2f} minutes".format((endTime - startTime) / 60))

    
    
    return df_temp


def main():
    

    df = hourly("hourly", ['Longitude (x)', 'Latitude (y)', 'Year', 'Month', 'Day', 'Time (LST)', 'Dew Point Temp (°C)','Rel Hum (%)','Wind Dir (10s deg)','Wind Spd (km/h)','Visibility (km)','Stn Press (kPa)','Weather'])

    #df = hourly("hourly", [])

    print(df.shape[0])
    
    df.to_pickle("hourly_complete.pkl")

main()
