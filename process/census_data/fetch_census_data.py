from pathlib import Path
import httpx
import pandas as pd
import time
import csv

#this script: 1) accesses the Census API & 2) creates a CSV containing the variables & year(s) of interest.
#referencing PA1: http.py & fetch_hearings.py

YEAR = [2024]
CENSUS_CSV_COLUMNS = ("","","", ...)

class FetchException(Exception): #also in PA1 (http.py)  & andes_indus (api_get.py)
    """
    Turn a httpx.Response into an exception.
    """

    def __init__(self, response: httpx.Response):
        super().__init__(
            f"{response.status_code} retrieving {response.url}: {response.text}"
        )



#ex) csv, json, os, sys, from pathlib import Path (used in PA1),
#ex) if writing a cache function, then: from .<parent directory> import <cache_function>

API_URL = #api/dev url


#variables to request (column names)


response = httpx.get(API_URL, follow_redirects=True)

#raise error if request failed

#convert to JSON

#may need Census API key (free) to avoid rate limits.



def cached_get():
    """
    Docstring for cached_get
    """
    time.sleep(10) #polite pause before each API request


def build_census_csv(year, output_filename: Path):
    """
    Create a CSV file populated w/ the following columns/variables of interest:
    
    Parameters:
        output_filename: Path object representing location to write file.
    """
    
def chicago_dataframe():
    """
    Docstring for chicago_dataframe
    """

if __name__ == "__main__":
    build_census_csv("census.csv")
