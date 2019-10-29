#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sample script. Retrieving data for top irrigated crops in Southwest Colorado.

Created on Tue Oct 29 11:11:03 2019

@author: travis
"""

from nasspy import nass_api

# Create API object
api = nass_api()

# Create references
whatdf = api.what_parameters
whendf = api.when_parameters
wheredf = api.where_parameters
api.all_parameters

# Use this to check what's available for the above
api.get_parameter_options('region_desc')

# These are the target counties
counties = ["MONTEZUMA", "DOLROES", "LA PLATA"]

# Get everything for these counties
freq_qs = ['freq_desc=' + f for f in api.get_parameter_options('freq_desc')]
county_qs = ["county_name=" + c for c in counties]
query = ["state_alpha=CO"]  + freq_qs + county_qs
api.get_query_count(query)
df = api.get_query(query)

# Only 26,000 annual rows - still let's see which commodity is most prominent
group = df.groupby('commodity_desc')
df['commodity_count'] = group['commodity_desc'].transform("count")
top_crops = df[['commodity_desc', 'commodity_count']].drop_duplicates()
top_crops = top_crops.sort_values('commodity_count', ascending=False)

# Wheat?! How about that? Let's widdle this down a bit.
df2 = df[['year', 'county_name', 'state_alpha', 'Value', 'commodity_desc',
          'short_desc', 'unit_desc', 'class_desc',  'domain_desc',
          'prodn_practice_desc', 'source_desc', 'asd_code',
          'statisticcat_desc','sector_desc', 'reference_period_desc',
          'domaincat_desc', 'state_name', 'state_ansi', 'group_desc',
          'util_practice_desc', 'country_name', 'agg_level_desc',
          'county_ansi', 'freq_desc', 'week_ending']]

# Okay, how about all of colorado? this will be a package test too
query = ["state_alpha=CO"]  + freq_qs
api.get_query_count(query)
df = api.get_query(query)
df2 = df[['year', 'county_name', 'state_alpha', 'Value', 'commodity_desc',
          'short_desc', 'unit_desc', 'class_desc',  'domain_desc',
          'prodn_practice_desc', 'source_desc', 'asd_code',
          'statisticcat_desc','sector_desc', 'reference_period_desc',
          'domaincat_desc', 'state_name', 'state_ansi', 'group_desc',
          'util_practice_desc', 'country_name', 'agg_level_desc',
          'county_ansi', 'freq_desc', 'week_ending']]