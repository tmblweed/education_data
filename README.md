# Education Data

## Running the Script

The script can be run as follows:

```bash python3 path/to/enrollment_details.py --year 2021
Goal of the Script

The goal of the script is to fetch results from an API with options to retry and wait, filter data by year and state, and then persist the results to a local folder. These results are subsequently loaded into a DataFrame for additional cleaning and querying.

Ideal Production Environment Workflow

In a production environment, the following steps would ideally be implemented:
Data Ingestion:
 Use a host with a cron job, Airflow schedule, or AWS Lambda triggered on a schedule to perform data ingestion on a batched schedule, as this is not event-driven data.
State and Data Mapping:
 At the code level, obtain mappings for states (FIPS codes) and other data slices, and persist them via the API in a timestamped manner to ensure the latest data is retrieved. Extend the querying capability to be generic, allowing for the construction of queries across multiple dimensions.
Data Storage:
 Store the data in Parquet format in S3 (date-partitioned with subfolders) or another cloud-based storage solution.
Data Querying:
 Query the data through an orchestration platform like Airflow or via another Lambda function.
Data Persistence and Visualization:
 Persist the data to a database, on top of which teams can query it via a data visualization layer.

Additional, the code would have test cases for each method, and a way to do data validations for the data that's returned from the API and some sort of a quality checks (For e.g, why is there no CA data)

State                Enrollment
--------------------------------
Illinois             71,078.0
Florida              58,900.0
Georgia              46,841.0
Colorado             30,891.0
Iowa                 22,680.0
Alabama              21,946.0
Indiana              20,832.0
Arizona              16,629.0
Arkansas             15,704.0
Connecticut          13,579.0
District of Columbia 11,212.0
Kansas                8,104.0
Idaho                 3,504.0
Alaska                2,924.0
Delaware              2,040.0
Hawaii                1,578.0
Notes

Used ChatGPT to format, add logging, and reorganize the code. Tested manually using Jupyter Notebook. Did not write any test cases, considering the time constraints.


Used the following miscellaneous Code to Validate the API. I was surprised by the lack of data for California and other states—did not have the time to investigate why this was the case.

The following code returned 0 results -

from urllib.request import urlopen
from json import loads

url = "https://educationdata.urban.org/api/v1/schools/ccd/enrollment/2021/grade-pk/"
response = urlopen(url)
data = loads(response.read())
filtered_data = [entry for entry in data['results'] if entry['fips'] == 6]
filtered_data
[] 

The Following API Returned a Different Set of Results

from urllib.request import urlopen
from json import loads
import pandas as pd

url = "https://educationdata.urban.org/api/v1/schools/ccd/enrollment/summaries?var=enrollment&stat=sum&by=state_location"
response = urlopen(url)
data = loads(response.read())
df = pd.DataFrame(data['results'])
filtered_df = df[df['year'] == 2021].sort_values(by='enrollment', ascending=False)
filtered_df

Sample Output for 2021

plaintext
Copy code
2021    CA    5,874,948
2021    TX    5,428,609
2021    FL    2,832,739
2021    NY    2,526,204
2021    IL    1,867,412
2021    GA    1,740,875
2021    OH    1,682,397
2021    PA    1,671,899
2021    NC    1,526,495
2021    MI    1,397,111
2021    NJ    1,339,937
2021    VA    1,244,624
