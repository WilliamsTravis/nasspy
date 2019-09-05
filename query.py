# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 20:31:46 2019

@author: travis
"""
from reprexpy import reprex
from functions import NASS_API
        
# 1) Create an api object
api = NASS_API(keypath='~/.keys/nass_api_key.txt')

# 2) Check available 'what', 'when', and 'where' parameters as pandas dataframes
whats = api.what_parameters
wheres = api.where_parameters
whens = api.when_paramaters
print(whats)

# 3) For any one parameter, return a list of options
api.get_parameter_options("commodity_desc")  # A 'What' option

# 4) Operators may also be used for more flexible filtering
print(api.operator_options)

# 5) For numeric parameters, it appears necessary to use an operator. e.g.:
"year__GE=1980"  # Years since 1980

# 6) Use these to build a list of queries (["<param><operator>=<option>", ...])
query = ['state_name=IOWA', 'commodity_desc=CORN',  'year__GE=1950',
         'freq_desc=WEEKLY']

# 7) And run that query to retrieve a pandas data frame
data = api.get_query(query)

# 8) Unfortunately, unavailable queries are interpreted as bad requests:
query = ['state_name=IOWA', 'commodity_desc=CORN',  'year__GE=2014',
         'freq_desc=WEEKLY', 'agg_level_desc=COUNTY']
api.get_query(query)

# And there is 50,000 record limit on returns
# (Here, corn since 1950 for all states with an "I" in their name)
query = ['state_name_like=I', 'commodity_desc=CORN',  'year__GE=1950',
         'freq_desc=WEEKLY']
api.get_query(query)
