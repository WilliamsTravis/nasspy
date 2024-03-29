# nasspy
#### Python wrappers for the U.S. National Agricultural Statistics Service's Quick Stats API.

#### To install:
`python setup.py install`

#### To use (generally):

1) Retrieve an API key from [NASS's QuickStats API page](https://quickstats.nass.usda.gov/api#param_define).
   Save this key to a file or provide it directly as an argument. 
2) Import the nass_api class from nasspy into a Python environment and create an api object.
3) Retrieve dataframes of available parameters and definitions.
4) Retrieve a list of input options for any one parameter.
5) Use the above parameters and options to build a query.
6) And retrieve the results of that query as a Pandas data frame.

#### To use (in practice):
  
```python
from nasspy import nass_api
```

#### 1) Create an api object. To use your NASS API key follow the prompts to set and save the key to a file using the default save path. The default save path is ~/.keys/nass_api_key.txt. You may also save the key to a specific file and specify that file path when creating the object. You may also enter the key directly as an argument and have it saved to the file path specified. 
```python
api = nass_api()

# or

api = nass_api(keypath='/any/path/anyfile.txt')

# or 

api = nass_api(key="KEYCHARACTERSHERE", keypath='/any/path/anyfile.txt')
```

#### 2) Check available 'what', 'when', and 'where' parameters as Pandas dataframes.
```python
whats = api.what_parameters
wheres = api.where_parameters
whens = api.when_parameters
print(whats.head(4))
#>               Parameter  Max Length   Definition 
#> 0           source_desc          60   Source of data (CENSUS or SURVEY). Census prog...  
#> 1           sector_desc          60   Five high level, broad categories useful to na...  
#> 2            group_desc          80   Subsets within sector (e.g., under sector = CR...  
#> 3        commodity_desc          80   The primary subject of interest (e.g., CORN, C... 
```

#### 3) For any one parameter, return a list of options.
```python
api.get_parameter_options("commodity_desc")  # A 'What' option
#> ['AG LAND',
#>  'AG SERVICES',
#>  'AG SERVICES & RENT',
#>  'ALCOHOL COPRODUCTS',
#>  'ALMONDS',
#>  'ALPACAS',
#>   ...]
```

#### 4) Operators may be appended to parameters for more flexible filtering.
```python
print(api.operator_options)
#>          CALL   FAMILIAR ANALOG                  DESCRIPTION
#> 0        __LE                <=       Less than or equal to.
#> 1        __LT                 <                   Less than.
#> 2        __GT                 >                Greater than.
#> 3        __GE                >=    Greater than or equal to.
#> 4        __NE                !=                Not equal to.
#> 5      __LIKE              like              Pattern is in. 
#> 6  __NOT_LIKE          not like           Pattern is not in.
```


#### 5) For numeric parameters, it appears necessary to use an operator (e.g.: "year__GE=1980"  for years since 1980).

#### 6) Use the above to build a query as alist of subqueries (`["<param><operator>=<option>", ...]`)
```python
query = ['state_name=IOWA', 'commodity_desc=CORN', 'year__GE=2018', 'freq_desc=WEEKLY']
```
 
#### 7) And run that query to retrieve a pandas data frame.
```python
data = api.get_query(query)
print(data.head())
#>   CV (%) Value agg_level_desc asd_code  ... watershed_desc week_ending  year zip_5
#> 0            6          STATE           ...                 2019-06-02  2019      
#> 1            7          STATE           ...                 2019-06-09  2019      
#> 2            8          STATE           ...                 2019-06-16  2019      
#> 3           10          STATE           ...                 2019-06-23  2019      
#> 4           11          STATE           ...                 2019-06-30  2019      
#>
#> [5 rows x 39 columns]
```

#### 8) Unfortunately, unavailable queries are interpreted as bad requests.
```python
query = ['state_name=IOWA', 'commodity_desc=ALPACAS', 'year__GE=2018', 'freq_desc=WEEKLY']
api.get_query(query)
#> {'error': ['bad request - invalid query']}
```

#### 9) And there is 50,000 record limit on returns. Here, corn records since 1950 for all states with an "I" in their name.
```python
query = ['state_name_like=I', 'commodity_desc=CORN',  'year__GE=1950', 'freq_desc=WEEKLY']
api.get_query(query)
#> {'error': ['exceeds limit=50000']}
```
