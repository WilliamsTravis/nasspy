# nasspy
Python wrappers for the U.S. National Agricultural Statistics Service's Quick Stats API.

To use (generally):

1) Retrieve an API key from [NASS's QuickStats API page](https://quickstats.nass.usda.gov/api#param_define).
   Save this key to a file or provide it directly as an argument. 
2) Import NASS_API from nasspy into a Python environment and create an api object.
3) Retrieve dataframes of available parameters and definitions.
4) Retrieve a list of input options for any one parameter.
5) Use the above parameters and options to build a query.
6) And retrieve the results of that query as a Pandas data frame.

To use (in practice):
  
```python
from functions import NASS_API
        
# 1) Create an api object
api = NASS_API(keypath='~/.keys/nass_api_key.txt')

# 2) Check available 'what', 'when', and 'where' parameters as pandas dataframes
whats = api.what_parameters
wheres = api.where_parameters
whens = api.when_paramaters
print(whats)
#>               Parameter  Max Length  \
#> 0           source_desc          60   
#> 1           sector_desc          60   
#> 2            group_desc          80   
#> 3        commodity_desc          80   
#> 4            class_desc         180   
#> 5   prodn_practice_desc         180   
#> 6    util_practice_desc         180   
#> 7     statisticcat_desc          80   
#> 8             unit_desc          60   
#> 9            short_desc         512   
#> 10          domain_desc         256   
#> 11       domaincat_desc         512   
#> 12                value          24   
#> 13                 CV %           7   
#> 
#>                                            Definition  
#> 0   Source of data (CENSUS or SURVEY). Census prog...  
#> 1   Five high level, broad categories useful to na...  
#> 2   Subsets within sector (e.g., under sector = CR...  
#> 3   The primary subject of interest (e.g., CORN, C...  
#> 4   Generally a physical attribute (e.g., variety,...  
#> 5   A method of production or action taken on the ...  
#> 6   Utilizations (e.g., GRAIN, FROZEN, SLAUGHTER) ...  
#> 7   The aspect of a commodity being measured (e.g....  
#> 8   The unit associated with the statistic categor...  
#> 9   A concatenation of six columns: commodity_desc...  
#> 10  Generally another characteristic of operations...  
#> 11  Categories or partitions within a domain (e.g....  
#> 12   Published data value or suppression reason code.  
#> 13  Coefficient of variation. Available for the 20...  

# 3) For any one parameter, return a list of options
api.get_parameter_options("commodity_desc")  # A 'What' option
#> ['AG LAND',
#>  'AG SERVICES',
#>  'AG SERVICES & RENT',
#>  'ALCOHOL COPRODUCTS',
#>  'ALMONDS',
#>  'ALPACAS',
#>   ...]

# 4) Operators may also be used for more flexible filtering
print(api.operator_options)
#>          CALL   FAMILIAR ANALOG                  DESCRIPTION
#> 0        __LE                <=       Less than or equal to.
#> 1        __LT                 <                   Less than.
#> 2        __GT                 >                Greater than.
#> 3        __GE                >=    Greater than or equal to.
#> 4        __NE                !=                Not equal to.
#> 5      __LIKE              like              Pattern is in. 
#> 6  __NOT_LIKE          not like           Pattern is not in.

# 5) For numeric parameters, it appears necessary to use an operator.
#    e.g.: "year__GE=1980"  for years since 1980


# 6) Use the above to build a list of queries (["<param><operator>=<option>", ...])
query = ['state_name=IOWA', 'commodity_desc=CORN',  'year__GE=1950',
         'freq_desc=WEEKLY']

# 7) And run that query to retrieve a pandas data frame
data = api.get_query(query)

# 8) Unfortunately, unavailable queries are interpreted as bad requests:
query = ['state_name=IOWA', 'commodity_desc=CORN',  'year__GE=2014',
         'freq_desc=WEEKLY', 'agg_level_desc=COUNTY']
api.get_query(query)
#> {'error': ['bad request - invalid query']}

# And there is 50,000 record limit on returns
# (Here, corn since 1950 for all states with an "I" in their name)
query = ['state_name_like=I', 'commodity_desc=CORN',  'year__GE=1950',
         'freq_desc=WEEKLY']
api.get_query(query)
#> {'error': ['exceeds limit=50000']}
```

<sup>Created on 2019-09-04 by the [reprexpy package](https://github.com/crew102/reprexpy)</sup>
