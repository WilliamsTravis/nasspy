import copy
import datetime as dt
import math
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
        self.api_url = 'http://quickstats.nass.usda.gov/api'
        self.quickstats_url = 'https://quickstats.nass.usda.gov/api'
        self.what_parameters = pd.read_csv(dp('nass_api_params_what.txt'),
                                           sep='|', index_col=False)
        self.when_parameters = pd.read_csv(dp('nass_api_params_when.txt'),
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
        if '~' in keypath:
                keypath = keypath.replace('~', expanduser('~'))
        self.keypath = keypath
        self.key = key
        self._save_key()

    def print_operators(self):
        print("__LE = <= \n__LT = <\n__GT = >\n__GE = >= \n" +
              "__LIKE = like\n__NOT_LIKE = not like\n__NE = not equal ")

    def get_parameter_options(self, parameter):
        base = '/'.join([self.api_url, 'get_param_values', '?key=']) + self.key
        request = '&'.join([base, 'param=' + parameter])
        r = requests.get(request)
        data = r.json()
        options = data[parameter]
        return options

    def get_query_count(self, query):
        base = '/'.join([self.api_url, 'get_counts', '?key=']) + self.key
        query_part = '&'.join(query)
        request = '&'.join([base, query_part])
        r = requests.get(request)
        data = r.json()
        number = int(data['count'])
        return number

    def get_query(self, query):
        # Check the number of records available first
        n = self.get_query_count(query)

        # If n is greater than 50,000
        if n <= 50000:
            df = self._get_one_query(query)
        else:
            print("More than 50,000 records, attempting to split query by " +
                  "year...")

            # Get Query data
            df = self._get_queries(n, query)

        return df

    def _get_one_query(self, query):
        # Build the full request url
        base_part = '/'.join([self.api_url, 'api_GET', '?key=']) + self.key
        query_part = '&'.join(query)
        request = '&'.join([base_part, query_part])
        r = requests.get(request)
        data = r.json()
        try:
            return pd.DataFrame(data['data'])
        except:
            return data

    def _get_queries(self, n, query):

        # If we have any year filters
        year_check = [q for q in query if "year" in q]

        # Get none numbers 
        def notYear(string):
            return "".join([s for s in string if not s.isdigit()])
        op_check = [notYear(yc) for yc in year_check]

        # There are several cases:
        # Case 1: multiple single years
        if not any([oc for oc in op_check if oc in self.operator_options['CALL']]):
            pass
            
#
#        # If we have a year range
#        if len(year_check) == 2:
#            query_copy = copy.copy(query)
#            yc1 = [y for y in year_check if "GE" in y][0]
#            yc2 = [y for y in year_check if "LE" in y][0]
#            query_copy.remove(yc1)
#            query_copy.remove(yc2)
#            year1 = int("".join([y for y in yc1 if y.isdigit()]))
#            year2 = int("".join([y for y in yc2 if y.isdigit()]))
#
#        # If we only have one year filter
#        elif len(year_check) == 1:
#            yc = year_check[0]
#            query_copy = copy.copy(query)
#            query_copy.remove(yc)
#            year1 = int("".join([y for y in yc if y.isdigit()]))
#
#            # GE goes to present
#            if '__GE' in yc:
#                year2 = dt.datetime.today().year
#
#            # LE goes to past
#            if '__LE' in yc:
#                year2 = year1
#                year1 = 1900
#
#        # If we have no year filters the full record is used
#        elif len(year_check) == 0:
#            query_copy = copy.copy(query)
#            year1 = 1900
#            year2 = dt.datetime.today().year
#
#        # Build queries - tricky
#        queries = self._split_queries(n, year1, year2, query_copy)
#        rlist = [self._get_one_query(q) for q in queries]
#
#        # We may not have split this enough
#        error_idx = [rlist.index(rl) for rl in rlist if
#                     type(rl) != pd.core.frame.DataFrame]
#        rlist2 = [rl for rl in rlist if type(rl) == pd.core.frame.DataFrame]
#
#        for idx in error_idx:
#            n = self.get_query_count(queries[idx])
#            year_check = [q for q in queries[idx] if "year" in q]
#            q = queries[idx]
#            query_copy = copy.copy(q)
#            yc1 = [y for y in year_check if "GE" in y][0]
#            yc2 = [y for y in year_check if "LE" in y][0]
#            query_copy.remove(yc1)
#            query_copy.remove(yc2)
#            year1 = int("".join([y for y in yc1 if y.isdigit()]))
#            year2 = int("".join([y for y in yc2 if y.isdigit()])) 
#            qs = self._split_queries(n, year1, year2, q)
#
#        df = pd.concat(rlist2)

    def _keygen(self):

        print("Request a NASS API key here: " +
              "\nhttps://quickstats.nass.usda.gov/api \n")
        if not os.path.exists(os.path.dirname(self.keypath)):
            os.makedirs(os.path.dirname(self.keypath))
        key = input("Enter nass key: ")
        with open(expanduser(self.keypath), "r+") as keyfile:
            keyfile.write(key)
        print("NASS API key saved to " + self.keypath)
        self.key = key

    def _save_key(self):
        # Nothing entered
        if not os.path.exists(self.keypath) and not self.key:
            self.keygen()

        # Key file with not explicit key
        elif os.path.exists(self.keypath) and not self.key:
            self.key = open(self.keypath).read().splitlines()[0]

        # Now check the key with a sample query
        sample_query = ['state_name=IOWA', 'commodity_desc=CORN',
                       'year__GE=2018', 'freq_desc=yearly']
        check = 0
        while check == 0:
            r = self.get_query(sample_query)
            if ['unauthorized'] in r.values():
                print("\nUnauthorized key, try again")
                self._keygen()
            else:
                check = 1
