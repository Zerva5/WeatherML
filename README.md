# WeatherML! 

So far this repo is capable of downloading weather data from every single weather station in Canada and then parsing it into a single dataset (one for Hourly and one for Daily data)! 

Weather.gc.ca has some limitations when it comes to downloading data, StatsCan is much better! Right now you can download 1 year of monthly observations of 1 month of hourly observations. There are (as of Feb 9th) 8795 current and past weather stations in Canada. About 1700 for BC. There are approximately 73,000 months of hourly observations and 41,000 years of daily observations for BC, or about 115,000 individual `.csv` files total. 

(This)[https://drive.google.com/drive/folders/1WJCDEU34c60IfOnG4rv5EPZ4IhhW9vZH] GDrive folder from weather.gc.ca has instructions on downloading climate data using https requests. `fetchData.py` automates this process.

`fetchData.py` **WILL** wreck your internet connection and take awhile. I suggest doing this download at night. Weather.gc.ca doesn't have any 24hr rate limits or anything, I was able to download about 300k csv files from them overnight. You will run into rate limits, I used a `WORKER_COUNT` of 50-150 but YMMV. It also needs to be cleaned up with options so that you don't need to manually go into the file and uncomment lines. But that can happen later.  


# ML Models!

## A bad one
So right now the majority of the work has been fetching and parsing the data in a way that doesn't take 20 years. The model contained in `dailyModel.ipynb` takes in the Latitude, Longitude, Year, Month, and Day to predict the max temp, min temp, and precipitation for the day. It wasn't trained for that long and had *only* 6.6 million daily temp samples. 

## Future Plans
What I'll be working on is a model that takes in n consecutive *Daily* observations and spits out the *Hourly* observations for the middle one. Can also do a recurrence NN. I think this model will be more successful as it will have more information available as input and the sample size for 100% complete *Hourly* observations is 13.27M samples. There are 54M total *Hourly* observations but many of them don't include key stats. I am hoping to also make a model that will predict these missing values. Not sure which I should do first but should be interesting nontheless!

## Final Goal
I'm undecided on my final goal for the project right now. I think it would be intersting to make a predictive model that, given the previous 24hrs of weather across some area, can predict the weather at some given location and time. It would take in the weather information for the previous two days across the country/province and predict the weather at a 
