# nasspy
Python wrappers for the National Agricultural Statistics Service's Quick Stats API.

To use:

    1) Create an api object: 
        api = NASS_API(<your nass key as a string>)
  
    2) Get a list of available parameters with api.all_parameters
    
    3) Get a list of the definitions of these parameters using
        api.what_parameters, api.where_parameters, and api.when_parameters

    4) Get a list of input options for any one parameter using
        api.get_parameter_options('parameter')

    5) Build a query as a list of strings like this:
        ['<parameter1>=<input1>', '<parameter2>=<input2>', ...]

    6) Filter each query by appending an operator to each string element:
        '<parameter><operator>=<input>'

    7) For count use the query list as the argument in api.get_query_count:
        data = api.get_query_count(query)

    8) For the data itself use the query list in api.get_query:
        data = api.get_query(query)

In practice:
  
```python
from functions import NASS_API
        
# 1) Create api object
api = NASS_API()

# 2) Check available 'what', 'when', and 'where' parameters
whats = api.what_parameters
wheres = api.where_parameters
whens = api.when_paramaters

# 3) For any one parameter, print out options
api.get_parameter_options("commodity_desc")  # A 'What' option
#> ['AG LAND',
 'AG SERVICES',
 'AG SERVICES & RENT',
 'ALCOHOL COPRODUCTS',
 'ALMONDS',
 'ALPACAS',
  ... ]

# 4) To query with a numeric parameter, one of these operators must be used
print(api.operator_options)
#>          CALL   FAMILIAR ANALOG                  DESCRIPTION
#> 0        __LE                <=       Less than or equal to.
#> 1        __LT                 <                   Less than.
#> 2        __GT                 >                Greater than.
#> 3        __GE                >=    Greater than or equal to.
#> 4        __NE                !=                Not equal to.
#> 5      __LIKE              like              Pattern is in. 
#> 6  __NOT_LIKE          not like           Pattern is not in.

# For instance, to retrieve data for years since 1980 the 'When' query becomes:
"year__GE=1980"

# 5) Use these to build a list of queries (["<param><operator>=<option>", ...])
query = ['state_name=IOWA', 'commodity_desc=CORN',  'year__GE=1950',
         'freq_desc=WEEKLY']

# 6) And run that query to retrieve a pandas data frame
data = api.get_query(query)

# Unfortunately, unavailable queries are interpreted as bad requests:
query = ['state_name=IOWA', 'commodity_desc=CORN',  'year__GE=2014',
         'freq_desc=WEEKLY', 'agg_level_desc=COUNTY']
api.get_query(query)
#> {'error': ['bad request - invalid query']}
```

<sup>Created on 2019-09-04 by the [reprexpy package](https://github.com/crew102/reprexpy)</sup>
