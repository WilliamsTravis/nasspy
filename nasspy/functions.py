
from os.path import expanduser
import os
import pandas as pd
import requests

_root = os.path.abspath(os.path.dirname(__file__))
def dp(path):
    return os.path.join(_root, 'data', path)

class nass_api:
    def __init__(self, keypath='~/.keys/nass_api_key.txt', key=None):
        self.sample_query = ['commodity_desc=CORN', 'year__GE=2010',
                             'state_alpha=VA']
        self.url = 'http://quickstats.nass.usda.gov/api'
        self.website = 'https://quickstats.nass.usda.gov/api'
        self.what_parameters = pd.read_csv(dp('nass_api_params_what.txt'),
                                           sep='|', index_col=False)
        self.when_paramaters = pd.read_csv(dp('nass_api_params_when.txt'),
                                           sep='|')
        self.where_parameters = pd.read_csv(dp('nass_api_params_where.txt'),
                                            sep='|')
        self.operator_options = pd.read_csv(dp('nass_api_params_operators.txt'),
                                            sep='|')
        self.all_parameters = ['source_desc', 'sector_desc', 'group_desc',
                               'commodity_desc', 'class_desc',
                               'prodn_practice_desc', 'util_practice_desc',
                               'statisticcat_desc', 'unit_desc', 'short_desc',
                               'domain_desc', 'domaincat_desc', 'value',
                               'CV %', 'year', 'freq_desc', 'begin_code',
                               'end_code', 'reference_period_desc',
                               'week_ending', 'load_time', 'agg_level_desc',
                               'state_ansi', 'state_fips_code', 'state_alpha',
                               'state_name', 'asd_code', 'asd_desc',
                               'county_ansi', 'county_code', 'county_name',
                               'region_desc', 'zip_5', 'watershed_code',
                               'watershed_desc', 'congr_district_code',
                               'country_code',  'country_name',
                               'location_desc']
        if not keypath and not key:
            print("Request a NASS API key, save it in a local text file " +
                  "(keypath argument) or use it directly (key argument): " +
                  "\nhttps://quickstats.nass.usda.gov/api")
        elif key:
            self.key = key
        elif keypath:
            if '~' in keypath:
                keypath = keypath.replace('~', expanduser('~'))
            self.key = open(keypath).read().splitlines()[0]
        else:
            print("Looks like the key is incorrect. Request a NASS API key " +
                  "at https://quickstats.nass.usda.gov/api")

    def print_operators(self):
        print("__LE = <= \n__LT = <\n__GT = >\n__GE = >= \n" +
              "__LIKE = like\n__NOT_LIKE = not like\n__NE = not equal ")

    def get_parameter_options(self, parameter):
        base = '/'.join([self.url, 'get_param_values', '?key=']) + self.key
        request = '&'.join([base, 'param=' + parameter])
        r = requests.get(request)
        data = r.json()
        options = data[parameter]
        return options

    def get_query_count(self, query):
        base = '/'.join([self.url, 'get_counts', '?key=']) + self.key
        query_part = '&'.join(query)
        request = '&'.join([base, query_part])
        r = requests.get(request)
        data = r.json()
        number = int(data['count'])
        return number

    def get_query(self, query):
        base_part = '/'.join([self.url, 'api_GET', '?key=']) + self.key
        query_part = '&'.join(query)
        request = '&'.join([base_part, query_part])
        r = requests.get(request)
        data = r.json()
        try:
            df = pd.DataFrame(data['data'])
        except:
            return data
        return df
