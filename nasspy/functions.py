import copy
import datetime as dt
from multiprocessing import cpu_count, Pool
import numpy as np
from os.path import expanduser
import os
import pandas as pd
import requests
import sys
from tqdm import tqdm

# For data, find local path of this package
_root = os.path.abspath(os.path.dirname(__file__))


# Data path
def dp(path):
    return os.path.join(_root, 'data', path)


# Extract non-digits from a string
def notDigits(string):
    return "".join([s for s in string if not s.isdigit()])

# Extract digits from a string
def isDigits(string):
    return "".join([s for s in string if s.isdigit()])


# Check if a string contains any of a list of other strings
def isIn(string, strings):
    return any(s in string for s in strings)


# Fix the comma problem in a pandas series
def fixValues(value):
    if ',' in value:
        value = value.replace(',', '')
    try:
        return float(value)
    except:
        return np.nan
        

# The API wrapper 
class nass_api:
    def __init__(self, keypath='~/.keys/nass_api_key.txt', key=None):
        self.sample_query = ['commodity_desc=CORN', 'freq_desc=ANNUAL',
                             'year=1950', 'state_alpha=VA']
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
        # Get just the count of the request
        request = self._build_request(query, count=True)
        r = requests.get(request)
        data = r.json()
        try:
            number = int(data['count'])
            return number
        except:
            return data

    def get_query(self, query, verbose=True):
        # Check for issues
        self._query_check(query)

        # Check the number of records available first
        n = self.get_query_count(query)

        try:
            # If n is greater than 50,000
            if n <= 50000:
                df = self._get_one_query(query)
            else:
                print("More than 50,000 ({:,}) records available".format(n) +
                      ", attempting to split query by year...")
    
                # Get Query data
                df = self._get_queries(query, n)

            if verbose:
                # Check to see how well we did compared to what was available
                ndf = df.shape[0]
                print("")
                print("{:,} out of {:,} records retrieved".format(ndf, n))
            
            # Fix commas, strings, and missing values
            df['Value'] = df['Value'].apply(fixValues)
            df = df.dropna(subset=['Value'])

            if verbose:
                # One last return statement to account for non-values
                ndrop = ndf - df.shape[0]
                print("{:,} non-values dropped.".format(ndrop))

            # Return df if this works
            return df

        except:
            # If it fails, n should include an error statement in a dictionary
            if verbose:
                print("Request Failed")

            return n


    # Is it better to define these externally?
    def _build_request(self, query, count=False):
        # Build just the requests
        if count:
            base = '/'.join([self.api_url, 'get_counts', '?key=']) + self.key
            query_part = '&'.join(query)
            request = '&'.join([base, query_part])
        else:
            base_part = '/'.join([self.api_url, 'api_GET', '?key=']) + self.key
            query_part = '&'.join(query)
            request = '&'.join([base_part, query_part])
        return request

    def _get_one_query(self, query):
        # Use if n requests is small enough
        request = self._build_request(query)
        r = requests.get(request)
        data = r.json()
        try:
            return pd.DataFrame(data['data'])
        except:
            return query

    def _get_queries(self, query, n):
        # Sorry about this mess

        # Check if we have any year filters (one operator or multiple years)
        year_check = [q for q in query if "year" in q]

        # If there are multiple single year queries we cant handle it yet.
        if len(year_check) > 1:
            print("Failure: Query already split by year, try refining your" +
                  "request.")
            return

        # If there isn't a year operator, that means the whole record
        elif len(year_check) == 0:
            year1 = 1900
            year2 = dt.datetime.today().year
            
        # If there is an operator, which is it and what year?
        else:
            ops = self.operator_options['CALL'].values
            yc = year_check[0]
            year = int(isDigits(yc))
            op = [o for o in ops if o in yc][0]

            # Year 1 and 2 depend on the operator
            if op == '__GE':
                year1 = year
                year2 = dt.datetime.today().year
            elif op == '__LE':
                year1 = 1900
                year2 = year
            else:
                print("Haven't worked out the " + op + "case yet. Try a " +
                      " different operator for now.")
                return

        # Remove the original year operator from the query
        query_copy = copy.copy(query)
        for yc in year_check:
            query_copy.remove(yc)

        # Now we can generate a list of single year queries
        year_queries = ["year=" + str(y) for y in range(year1, year2 + 1)]

        # And with that individual full queries
        queries = [query_copy + [yq] for yq in year_queries]

        # And with that, get a list of data frames and more too big queries
        dfs = []
        pool = Pool(int(cpu_count() - 1))
        fun = copy.copy(self._get_one_query)       
        for df in tqdm(pool.imap(fun, queries), total=len(queries),
                       position=0, leave=True):
            dfs.append(df)
        pool.close()
        missed = [df for df in dfs if type(df) is list]
        dfs = [df for df in dfs if type(df) is pd.core.frame.DataFrame]

        # Now, how to further reduce?
        if len(missed) > 0:
            print("\nThere are still sub requests with more than 50,000 " + 
                  "trying to split records using time frequency...")
            new_queries = []
            for query in missed:
                query = np.array(query)

                # Where are there repeats?
                query_ops = [o.split("_")[0] for o in query]
                query_counts = [query_ops.count(q) for q in query_ops]
                repeat_idx = np.where(np.array(query_counts) > 1)[0]
                single_idx = np.where(np.array(query_counts) == 1)[0]

                # Split the query up by repeats
                base_q = query[single_idx]
                repeat_qs = query[repeat_idx]
                new_qs = [list(base_q) + [rp] for rp in repeat_qs] 

                # Add to the new queries list
                new_queries = new_queries + new_qs

            # Okay, now request all these just like before
            new_dfs = []
            pool = Pool(int(cpu_count() - 1))
            for df in tqdm(pool.imap(fun, new_queries), total=len(new_queries),
                           position=0, leave=True):
                new_dfs.append(df)
            pool.close()
            missed2 = [df for df in new_dfs if type(df) is list]
            new_dfs = [df for df in new_dfs if
                       type(df) is pd.core.frame.DataFrame]

            # combine df lists
            dfs = dfs + new_dfs

            # If that didn't work I give up.
            if len(missed2) > 0:
                # Let's try splitting by agg_level_desc
                if "group" not in query_ops:
                    print("\nSplitting by year and time frequency wasn't " +
                          "enough. Some years still had " +
                          "more than 50,000 records, attempting to split  one " +
                          "more time using group description...")
                    group_ops = self.get_parameter_options("group_desc")
                    op_cat = "group_desc="
                elif "agg" not in query_ops:
                    print("\nSplitting by year and time frequency wasn't " +
                          "enough. Some years still had more " +
                          "than 50,000 records, attempting to split one " +
                          "more time using aggregation level description...")
                    group_ops = self.get_parameter_options("agg_level_desc")
                    op_cat = "agg_level_desc="
    
                # Building a new new set of queries
                new_queries = []
                for q in missed2:
                    new_groups = [op_cat + a for a in group_ops]
                    new_qs = [q + [ng] for ng in new_groups]
                    new_queries = new_queries + new_qs
    
                # Okay, now request all these just like before
                new_dfs = []
                pool = Pool(int(cpu_count() - 1))
                for df in pool.imap(fun, new_queries):
                    new_dfs.append(df)
                pool.close()
                new_dfs = [df for df in new_dfs if
                           type(df) is pd.core.frame.DataFrame]

                # Combine our two lists of data frames
                dfs = dfs + new_dfs

        # And if that works, concatenate these into one data frame
        df = pd.concat(dfs, sort=True)

        # Done.
        return df

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

    def _query_check(self, query):
        '''
        There are some situations/errors that might go unnoticed.
        '''
        # Check if we have any year filters
        year_check = [q for q in query if "year" in q]
        op_check = [notDigits(yc) for yc in year_check]
        ops = self.operator_options['CALL'].values
        year_op_check = [op for op in op_check if isIn(op, ops)]

        # If there are more than one year operators it only considers one
        if len(year_op_check) > 1:
            print("Please use only one year operator. Multiple single year " +
                  "queries are fine, though.")
            return

    def _save_key(self):
        # Nothing entered
        if not os.path.exists(self.keypath) and not self.key:
            self.keygen()

        # Key file with not explicit key
        elif os.path.exists(self.keypath) and not self.key:
            self.key = open(self.keypath).read().splitlines()[0]

        # Now check the key with a sample query
        check = 0
        while check == 0:
            df = self.get_query(self.sample_query, verbose=False)
            if type(df) is dict and ['unauthorized'] in df.values():
                print("\nUnauthorized key, try again")
                self._keygen()
            else:
                check = 1
