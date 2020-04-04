# US_COVID_County_Map
Maps of Cases and Deaths per Capita by County and Date

This project creates dated maps that show the reported cases and deaths from COVID-19 per capita by county or county-equivalent.

COVID-19 case and death data is compiled by the New York Times.
It can be found here: https://github.com/nytimes/covid-19-data/blob/master/us-counties.csv

The populations data is the estimated population as of July 1, 2019 by the United States Census.
Find it here: https://www2.census.gov/programs-surveys/popest/tables/2010-2019/counties/totals/co-est2019-annres.xlsx.

Dependencies:
pandas
numpy
plotly

Other tools used:
OpenOffice/Google Sheets.

Some notes:

1. For several states, the Times has reported some cases with the county listed as "Unknown." The calculate.py script simply redistibutes these cases to counties that already have cases, proportional to the ratio of that county's population to the sum of the population of all counties within that that state that already had cases. In other words, I assumed that none of the "Unknown" cases occurred in a county that did not already have reported cases, and distributed the "Unknown" cases proportional to the populations where known cases had occurred.
2. The NY Times also describes New York City as a single county, when in fact NYC comprises 5 counties. I distributed all NYC cases to each NYC county proportional to the county's share of the NYC population.
3. NY Times also lists Kansas City, Missouri as single county, when it is part of four separate counties. I could not find any information on how KC's population is distributed over these four counties, and KC, unlike NYC, is not coterminous with the counties it lies in. But the number of KC cases is relatively small compared to the cases reported from the individual counties, so I simply ignored this.
