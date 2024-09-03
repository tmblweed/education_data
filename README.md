# education_data

Script can be run as python3 file/to/loc/enrollment_details.py --year 2021 

 The goal of the script is to fetch results from an API with options to retry and wait, filter data by year and state. Then the results are persisted to a local folder, which are then loaded again into a data frame for additional cleaning and querying

 Ideally, in a production envrionemnt, we would do something like the following
 1) Data ingestion (either on a host with a cron job or airflow schedule or via AWS lambda triggered on a schedule) on a batched schedule, since this is not event data
 2) At the code level, get the mappings for states (fips) and other slices of data and persist them via the API, in a time stamped way to get the latest data. Also, extend the querying to be generic in a way where can construct query for a few different dimensions
 3) Store data in parquet in S3 (date partitioned with subfolders) or another cloud based storage
 4) Query data either through an orchestration platform like Airflow of via another lambda style function
 5) Persist data to a database, on top of which there's a way for teams to query via a data visualitoin layer

               state  enrollment
            Illinois     71078.0
             Florida     58900.0
             Georgia     46841.0
            Colorado     30891.0
                Iowa     22680.0
             Alabama     21946.0
             Indiana     20832.0
             Arizona     16629.0
            Arkansas     15704.0
         Connecticut     13579.0
District of Columbia     11212.0
              Kansas      8104.0
               Idaho      3504.0
              Alaska      2924.0
            Delaware      2040.0
              Hawaii      1578.0



Notes:
 Used chatgpt to format/add logging and reorganize  code, and jupyter notebook to test manually. did not write any test cases keeping in mind the time


**Misc code to validate for the API**
*surprised about lack of data for CA and others - did not get to dig in as to why that is

  
  from urllib.request import urlopen
  from json import loads
  url = "https://educationdata.urban.org/api/v1/schools/ccd/enrollment/2021/grade-pk/"
  response = urlopen(url)
  data = loads(response.read())
  filtered_data = [entry for entry in data['results'] if entry['fips'] == 6]
  filtered_data

the following API returned a different set of results

from urllib.request import urlopen
from json import loads
 url = "https://educationdata.urban.org/api/v1/schools/ccd/enrollment/summaries?var=enrollment&stat=sum&by=state_location"
 response = urlopen(url)
 data = loads(response.read())
 df = pd.DataFrame(data['results'])
 filtered_df = df[df['year'] == 2021].sort_values(by='enrollment', ascending=False)
 filtered_df

  2021	CA	5874948
  2021	TX	5428609
  2021	FL	2832739
  2021	NY	2526204
  2021	IL	1867412
  2021	GA	1740875
  2021	OH	1682397
  2021	PA	1671899
  2021	NC	1526495
  2021	MI	1397111
  2021	NJ	1339937
  2021	VA	1244624
