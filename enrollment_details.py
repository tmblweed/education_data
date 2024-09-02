import requests
import pandas as pd
import time
import os
import logging
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# FIPS codes dictionary as provided
fips_codes = {
    1: "Alabama",
    2: "Alaska",
    3: "American Samoa",
    4: "Arizona",
    5: "Arkansas",
    6: "California",
    7: "Canal Zone",
    8: "Colorado",
    9: "Connecticut",
    10: "Delaware",
    11: "District of Columbia",
    12: "Florida",
    13: "Georgia",
    14: "Guam",
    15: "Hawaii",
    16: "Idaho",
    17: "Illinois",
    18: "Indiana",
    19: "Iowa",
    20: "Kansas",
    21: "Kentucky",
    22: "Louisiana",
    23: "Maine",
    24: "Maryland",
    25: "Massachusetts",
    26: "Michigan",
    27: "Minnesota",
    28: "Mississippi",
    29: "Missouri",
    30: "Montana",
    31: "Nebraska",
    32: "Nevada",
    33: "New Hampshire",
    34: "New Jersey",
    35: "New Mexico",
    36: "New York",
    37: "North Carolina",
    38: "North Dakota",
    39: "Ohio",
    40: "Oklahoma",
    41: "Oregon",
    42: "Pennsylvania",
    43: "Puerto Rico",
    44: "Rhode Island",
    45: "South Carolina",
    46: "South Dakota",
    47: "Tennessee",
    48: "Texas",
    49: "Utah",
    50: "Vermont",
    51: "Virginia",
    52: "Virgin Islands of the US",
    53: "Washington",
    54: "West Virginia",
    55: "Wisconsin",
    56: "Wyoming",
    58: "Department of Defense Dependent Schools (overseas)",
    59: "Bureau of Indian Education",
    60: "American Samoa",
    61: "Department of Defense Dependent Schools (domestic)",
    63: "Department of Defense Education Activity",
    64: "Federated States of Micronesia",
    65: "Mariana Islands waters (including Guam)",
    66: "Guam",
    67: "Johnston Atoll",
    68: "Marshall Islands",
    69: "Northern Mariana Islands",
    70: "Palau",
    71: "Midway Islands",
    72: "Puerto Rico",
    74: "US Minor Outlying Islands",
    75: "Atlantic coast from North Carolina to Florida, and the coasts of Puerto Rico and Virgin Islands",
    76: "Navassa Island",
    78: "Virgin Islands of the US",
    79: "Wake Island",
    81: "Baker Island",
    84: "Howland Island",
    86: "Jarvis Island",
    89: "Kingman Reef",
    95: "Palmyra Atoll",
    -1: "Missing/not reported",
    -2: "Not applicable",
    -3: "Suppressed data"
}

def fetch_pre_k_data(year, state=None, retries=3, delay=5):
    """
    Fetch Pre-K enrollment data for a given year and state (if specified) from the API.
    """
    base_url = f"https://educationdata.urban.org/api/v1/schools/ccd/enrollment/{year}/grade-pk/"
    params = {"fips": state} if state else {}

    for attempt in range(retries):
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
            data = response.json()
            return pd.DataFrame(data['results']) 
        except requests.exceptions.HTTPError as e:
            logging.warning(f"Attempt {attempt + 1} failed with status code {response.status_code}. Retrying in {delay} seconds...")
            time.sleep(delay)
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            break

    logging.error(f"Failed to fetch data after {retries} attempts.")
    return pd.DataFrame()

def save_data_to_csv(df, year, state):
    """
    Save the DataFrame to a CSV file in a specified directory.
    """
    state_folder = state if state else "all_states"
    directory = f"pre_k_enrollment/{year}/{state_folder}/"
    os.makedirs(directory, exist_ok=True)
    
    filename = f"{directory}pre_k_data_{year}_{state_folder}.csv"
    df.to_csv(filename, index=False)
    logging.info(f"Data saved to {filename}")

def load_and_query_data(year, state=None):
    """
    Load data from a CSV file and perform a query on it.
    """
    state_folder = state if state else "all_states"
    filepath = f"pre_k_enrollment/{year}/{state_folder}/pre_k_data_{year}_{state_folder}.csv"
    
    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
        # map fips codes to states 
        df['state'] = df['fips'].map(fips_codes)
        
        # Summarize total enrollment by fips
        total_enrollment_by_fips = (
                                df.groupby("state")["enrollment"]
                                  .sum()
                                  .reset_index()
                                  .sort_values(by='enrollment', ascending=False)
                                  .reset_index(drop=True)
                            )
        return total_enrollment_by_fips
    else:
        logging.warning(f"No data found for {state_folder} in {year}")

def main(years, state=None):
    states = {}

    for year in years:
        if states:  # If specific states are provided
            for fips_code, state in states.items():
                data = fetch_pre_k_data(year, fips_code)
                if not data.empty:
                    save_data_to_csv(data, year, state)
                else:
                    logging.info(f"No data to save for {state} in {year}")
        else:  # Fetch data for all states combined
            data_all_states = fetch_pre_k_data(year)
            if not data_all_states.empty:
                save_data_to_csv(data_all_states, year, None)
            else:
                logging.info(f"No data to save for all states in {year}")

        total_enrollment = load_and_query_data(year, state)
        if total_enrollment is not None:
            logging.info("\n" + total_enrollment.to_string(index=False))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and process Pre-K enrollment data.")
    parser.add_argument('--years', type=int, nargs='+', required=True, help="List of years to load data for.")
    parser.add_argument('--state', type=int, help="The FIPS code of the state to load data for. If not provided, all states will be processed.")

    args = parser.parse_args()
    main(args.years, args.state)
