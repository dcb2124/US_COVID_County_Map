# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 17:02:42 2020

@author: David Billingsley github @dcb2124 davidcbillingsley.com twitter @MarysRoommate
"""

import pandas as pd
from urllib.request import urlopen
import json

with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)
    
import plotly.express as px

#read in the data
#fips has to be read as string because I could not figure out how to get pandas to add leading
#zeros so that plotly would correctly interpret FIPS codes
#for some reason open_office uses ; as the delimiter in its CSV files.
df = pd.read_csv('covid_by_county_population_4.3.csv', dtype={'fips':str}, delimiter=';')

#getting converting to float value in Population column
df['Population'] = df['Population'].astype(float)


nytimes_source_info = 'Reported Cases and Deaths by County: New York Times - https://github.com/nytimes/covid-19-data/blob/master/us-counties.csv'
census_source_info = "Estimated 2019 County Populations: United States Census"
author = "David Billingsley github @dcb2124"

source_info_complete = "Author: " + author + ". Sources: " + nytimes_source_info + '. ' + census_source_info
author

#get the list of states that cases/deaths
#not attributed to any particular county
#by making a pivot table on the states
#and then just take the index
#just counting Puerto Rico as a single county

unknown_counties = df[df['county'] == 'Unknown']
unknown_counties = unknown_counties[unknown_counties['state'] != 'Puerto Rico']

states_w_unknowns = pd.pivot_table(unknown_counties, index='state')



#for each state that has rows with unknown county...
for state in states_w_unknowns.index:
    
    #select all rows for that state (sorted by date for ease of testing)...
    state_table = df[df['state'] == state ].sort_values(by=['date'])
    
    #select all rows where county is unknown in that state...
    state_unknowns = state_table[state_table['county'] == 'Unknown']

    for i in state_unknowns.index:
        
        #select from state_table all rows for the date of row i
        #where cty is unknown
        state_known_ctys_on_date = state_table[state_table['date'] == state_table['date'][i] ]
    
        #remove the row where the cty is unknown    
        state_known_ctys_on_date = state_known_ctys_on_date[state_known_ctys_on_date['county'] != 'Unknown']
        
        #calculate the proportion of cases in that county to the total cases
        #where the county was known; same for deaths
        state_known_ctys_on_date['case_proportion'] = state_known_ctys_on_date['cases']/state_known_ctys_on_date['cases'].sum()
        state_known_ctys_on_date['death_proportion'] = state_known_ctys_on_date['deaths']/state_known_ctys_on_date['deaths'].sum()
        
        
        #then redistribute the unknown cases/deaths to the known counties proportionally
        state_known_ctys_on_date['cases'] = state_known_ctys_on_date['cases'].add(state_known_ctys_on_date['case_proportion'] * state_known_ctys_on_date['cases'])
        state_known_ctys_on_date['deaths'] = state_known_ctys_on_date['deaths'].add(state_known_ctys_on_date['death_proportion'] * state_known_ctys_on_date['deaths'])
        
        
        #then update df to reflect the new cases and deaths
        for j in state_known_ctys_on_date.index:
            df.loc[j, 'cases'] = state_known_ctys_on_date.loc[j, 'cases']
        
        
#calculate new columns cases and deaths per capita
df['cases_per_capita'] = df['cases']/df['Population']
df['deaths_per_capita'] = df['deaths']/df['Population']


#NYTimes doesn't provide county level data for New York City
#So I will redistribute the cases and deaths proportional to each county's
#population in 2019.
ny_ctys_pops_fips_ratio_array = [ 
    ['', 'Kings', 'New York', 36047, 0, 0, 2559903, 0.0, 0.0],
    ['','New York','New York', 36061, 0, 0, 1628706,0.0, 0.0],
    ['','Queens', 'New York', 36081, 0, 0, 2253858,0.0, 0.0],
    ['','Richmond', 'New York', 36085, 0, 0, 476143,0.0, 0.0],
    ['','Bronx', 'New York', 36005, 0, 0, 1418207,0.0, 0.0]]


#get data for new york on specific date        
date_df_nyc = df.loc[df['county'] == 'New York City']

for ind in date_df_nyc.index:
    
    
    #next two lines, I wish i could think of a way that it
    #did not have to calculate this every time.
    
    #reset dataframe for nyc ctys
    ny_ctys_df = pd.DataFrame(ny_ctys_pops_fips_ratio_array)

    #calculate proportion for each county
    ny_ctys_df[7] = ny_ctys_df[6]/ny_ctys_df[6].sum()

    
    #get date for that row
    date = date_df_nyc['date'][ind]
    
    #and create a dataframe with a row for each county on that date
    ny_ctys_df[0] = date
    
    #set cases/deaths proportional to population in each county
   
    ny_ctys_df[4] = date_df_nyc['cases'][ind]*ny_ctys_df[7]
    ny_ctys_df[5] = date_df_nyc['deaths'][ind]*ny_ctys_df[7]
    
    #set cases and deaths per capita
    #this need not be part of this for loop, I may move it later
    #but would need to adjust ny_ctys data frame definition and drop 7
    ny_ctys_df[7] = ny_ctys_df[4]/ny_ctys_df[6]
    ny_ctys_df[8] = ny_ctys_df[5]/ny_ctys_df[6]
    
    
    #drop the column containing ratio of county to city
    #might be necessary if i decided to do new york calc earlier
    #ny_ctys_df.drop(7, axis=1)
    
    #rename columns so that you can add to df above
    ny_ctys_df.columns=df.columns.values
    
    #add it to df
    df = pd.concat([df, ny_ctys_df], ignore_index=True)


#Now let's make maps for every date.
    
#give me a list of dates
date_list = pd.pivot_table(df, index = 'date').index

#iterate through them making maps for data on each date.

def generate_maps(case_data, dates, data_of_interest, latest_only = True, filetype=".png"):
    
    #generate the field information
    
    #just in case I forget to enter it this way
    data_of_interest = data_of_interest.lower()
    
    column_name = data_of_interest + "_per_capita"
    scale_title = 'Reported ' + data_of_interest.capitalize() + ' per Capita'

    #set max of color scale to be whatever the max of the data is over all dates
    range_max = (0, df[column_name].describe()['max'])

    color_dict = { 'deaths' : 'amp', 'cases': 'Reds'}       

    #so I can tell the function to just do this for the latest date   
    if latest_only:
        dates = [date_list[-1]]

    for date in dates:
    
        df_on_date = case_data[case_data['date'] == date]
            
        map_title = "Reported COVID-19 " + data_of_interest.capitalize() + " per Capita by County as of " + date 
        img_filename = 'dated_maps\\' + column_name + '_map_' + date + filetype
        
        cty_map_fig = px.choropleth(df_on_date, geojson=counties, locations='fips', 
                                    color=column_name,
                                    color_continuous_scale=color_dict[data_of_interest],
                                    range_color=range_max,
                                    scope="usa",
                                    labels={column_name:scale_title},
                                    hover_name='county',
                                    hover_data=[column_name],
                                    width=1920,
                                    height=1080,
                                    title=map_title
                                  )
        
        cty_map_fig.update_layout(
            
            annotations = [dict(
                x= 0.56,
                y= -0.1,
                xref='paper',
                yref='paper',
                text=source_info_complete
                )]
            )
        
        cty_map_fig.write_image(img_filename)
        

generate_maps(df, date_list, 'cases', latest_only=True)
generate_maps(df, date_list, 'deaths', latest_only=True)



#TODO
#learn how to make gif out of all dates to show progression
#update for latest NYTimes data and align populations. remember to format fips code
#embed in website?
#logscale?
#break this up into functions?
#functionality for selecting out a date range, without generating all maps
#update to a more customized map with plotly.graph_objects
#change to cases deaths per 1000 or 1million 










