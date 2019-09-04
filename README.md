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

    9) Examples:
  
        Retrieve weekly corn yields from Montana since 1980:
            query = ['state_name=MONTANA', 'commodity_desc=CORN', 'year__GE=1980', 'freq_desc=WEEKLY']
            data = api.get_query(query)
