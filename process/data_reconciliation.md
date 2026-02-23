RIDESHARE

The raw data is 93.5 million rows of rideshare trip data in Chicago from 2025.  There are two relevant variables: “Pickup Community Area” and “Dropoff Community Area”.  The raw data will be aggregated into three CSV files:

Rows of ordered pairs (A→B is different from B→A) (including self-pairs) of Chicago community areas (5,929 rows).  Each pair will have a single column with the total number of trips described by that pairing (pickup A → dropoff B)
Rows of each Chicago community area (77 community areas) with 3 columns: total number of pickups in that area, total number of dropoffs in that area, and total number of pickups & dropoffs in that area
Rows of each census tract (866 census tracts) with 3 columns: total number of pickups in that tract, total number of dropoffs in that tract, and total number of pickups & dropoffs in that tract

Pickup Community Area	The Community Area where the trip began. This column will be blank for locations outside Chicago.	pickup_community_area	Number
Dropoff Community Area	The Community Area where the trip ended. This column will be blank for locations outside Chicago.	dropoff_community_area	Number


L STATION ENTRIES
Column Name	Description	API Field Name	Data Type
station_id		station_id	Number
stationname		stationname	Text
date		date	Floating Timestamp
daytype		daytype	Text
rides		rides	Number

ACS DATA
Column Name	Description	API Field Name
Total households with no vehicle available		B08201_002E
Median Household Income in the Past 12 Months (in 2024 Inflation-Adjusted Dollars)		B19013
Age by Number of Disabilities (Total)		C18108_001E
Sex by Age	will need to sum age groups; we're interested % of the population that's 65 & older	"Males, 65 and older
B01001_020E  # 65-66
B01001_021E  # 67-69
B01001_022E  # 70-74
B01001_023E  # 75-79
B01001_024E  # 80-84
B01001_025E  # 85+

Females, 65 and older
B01001_044E
B01001_045E
B01001_046E
B01001_047E
B01001_048E
B01001_049E"
Total Population	for normalizing demographic statistics (from counts to % of population) & weighting aggregations to community areas.	B01003_001E