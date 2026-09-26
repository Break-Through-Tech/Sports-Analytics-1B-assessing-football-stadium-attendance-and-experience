# Exploratory Data Analysis: College Football Attendance

## 1. Dataset Summary & Coverage
Our initial exploratory data analysis focused on linking game attendance records with stadium capacity to create a relative "turnout" metric. 
* The geocoded stadium dataset contains complete capacity and team information for 253 records.
* Exact team-name matching initially connected 86.31% of FBS games (2,232 out of 2,586) to a stadium.
* After mapping clearly equivalent team names (e.g., "App State" to "Appalachian State"), the FBS match rate improved to 92.61%, providing capacity data for 2,395 FBS games.
* FCS stadium coverage was extremely limited, with only 25 of 1,380 FCS attendance records (1.81%) matching. As a result, calculating turnout rates from this dataset for FCS schools would produce a highly incomplete sample.

## 2. Key Statistics & Patterns
Using the 2,395 matched FBS records, we calculated the initial turnout rate by dividing reported attendance by listed stadium capacity.
* **Median Turnout Rate:** 86.7%
* **Mean Turnout Rate:** 81.0%

The distribution of FBS turnout rates is heavily left-skewed, indicating that the majority of games operate near capacity, though there is a long tail of games with significantly lower turnout.

## 3. Considerations for the "High-Turnout" Target
Before we finalize our binary classification target (High vs. Low Turnout), we identified data inconsistencies that must be addressed during the data cleaning phase:
* **Over-Capacity Games:** A total of 469 games reported attendance higher than the listed stadium capacity.
* **Potential Causes:** While most were only moderately above capacity, larger differences likely stem from capacity-data inconsistencies or games being played at neutral-site venues rather than the team's normal home stadium.
