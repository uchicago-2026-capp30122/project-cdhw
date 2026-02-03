#import packages here:
import httpx
#ex) csv, json, os, sys, from pathlib import Path (used in PA1),
#ex) if writing a cache function, then: from .<parent directory> import <cache_function>

API_URL = #api/dev url


#variables to request (column names)

#create a CSV file populated w/ the variables/columns & years of interest.

response = httpx.get(API_URL, follow_redirects=True)

#raise error if request failed

#convert to JSON

#may need Census API key (free) to avoid rate limits.


