import pandas as pd
import requests
import json
from pandas import json_normalize
from uri_to_url import uri_to_url

def most_used_by_type_bar(uri, instance, display_id, title, role, count):
    """
    Uses a sparql query to obtain information about the most used parts (of the same type as the poi e.g. all terminators)
    and format the data in such a way that a graph can be made comparing the poi (part of interest) to the most used parts
    of that role type.
    
    Requirements
    -------
    import pandas as pd
    import requests
    import json
    from pandas import json_normalize
    Most_Used_By_Type_Query.txt
    
    Parameters
    ----------
    uri : string
        the unique identifier of a part, note that due to spoofing it may not be the same as the url
        e.g. uri = 'https://synbiohub.org/public/igem/BBa_E0040/1' (url may be https://dev.synbiohub.org/public/igem/BBa_E0040/1)
    instance : string
        the synbiohub instance where information is to be retrieved from (where the sparql query is to be run)
        e.g. 'https://synbiohub.org/'
    display_id: string
        The display id of the poi e.g. 'BBa_E0040'
    title: string
        The human readable name of the poi e.g. 'GFP'
    role: string
        The number (as a string) of the sequence ontology of the role of the poi e.g. '0000316'    
    count: integer
        The number of times the poi is used (how often it is a subpart) e.g. 2348
   
    Returns
    -------
    bar_df: pandas dataframe, shape(11,6)
        columns are ['count', 'deff', 'displayId', 'roletog', 'title', 'color']
    
    Example
    --------
    display_id = 'BBa_E0040'
    title = 'GFP'
    role = '0000316'
    count = 2348
    
    uri = 'https://synbiohub.org/public/igem/BBa_E0040/1'
    instance = 'https://dev.synbiohub.org/'
    
    bar_df = most_used_by_type_bar(uri, instance, display_id, title, role, count)
    
    Output:
    count,deff,displayId,roletog,title,color
    948,'https://synbiohub.org/public/igem/BBa_E1010/1','BBa_E1010','http://identifiers.org/so/SO:0000316','mRFP1','rgba(119,157,205,1)'
    830,'https://synbiohub.org/public/igem/BBa_C0051/1','BBa_C0051','http://identifiers.org/so/SO:0000316','CI lam','rgba(119,157,205,1)'
    766,'https://synbiohub.org/public/igem/BBa_C0040/1','BBa_C0040','http://identifiers.org/so/SO:0000316','TetR','rgba(119,157,205,1)'
    662,'https://synbiohub.org/public/igem/BBa_C0012/1','BBa_C0012','http://identifiers.org/so/SO:0000316','lacI','rgba(119,157,205,1)'
    660,'https://synbiohub.org/public/igem/BBa_C0062/1','BBa_C0062','http://identifiers.org/so/SO:0000316','luxr','rgba(119,157,205,1)'
    640,'https://synbiohub.org/public/igem/BBa_E0030/1','BBa_E0030','http://identifiers.org/so/SO:0000316','eyfp','rgba(119,157,205,1)'
    538,'https://synbiohub.org/public/igem/BBa_C0061/1','BBa_C0061','http://identifiers.org/so/SO:0000316','luxI','rgba(119,157,205,1)'
    342,'https://synbiohub.org/public/igem/BBa_E0020/1','BBa_E0020','http://identifiers.org/so/SO:0000316','ecfp','rgba(119,157,205,1)'
    202,'https://synbiohub.org/public/igem/BBa_C0060/1','BBa_C0060','http://identifiers.org/so/SO:0000316','aiiA','rgba(119,157,205,1)'
    186,'https://synbiohub.org/public/igem/BBa_I732006/1','BBa_I732006','http://identifiers.org/so/SO:0000316','lacZ-alpha','rgba(119,157,205,1)'
    2348,'https://synbiohub.org/public/igem/BBa_E0040/1','BBa_E0040','http://identifiers.org/so/SO:0000316','GFP','rgba(119,157,205,1)'

    """
    #if spoofing is happening the uri instance is different than the instance
    spoofed_instance = uri[:uri.find('/', 8)+1]
    
    #get part url from uri
    part_url = uri_to_url(uri, instance, spoofed_instance)
    
    #open the query to collect the necessary data
    fl = open("Most_Used_By_Type_Query.txt", "r")
    sparql_query = fl.read()
    
    #replace the role with the relevant role
    sparql_query = sparql_query.replace("0000167", role)
    
    #perform the query
    r = requests.post(instance+"sparql", data = {"query":sparql_query}, headers = {"Accept":"application/json"})
    
    #format the data
    d = json.loads(r.text)
    bar_df = json_normalize(d['results']['bindings'])
    
    
    #rename columns
    rename_dict = {'count.datatype':'cd', 'count.type':'ct', 'count.value':'count', 'def.type':'dt', 'def.value':'deff', 'displayId.type':'dist', 'displayId.value':'displayId', 'role.type':'rt', 'role.value':'roletog', 'title.type':'tt', 'title.value':'title'}
    bar_df.columns = [rename_dict[col] for col in bar_df.columns]
     
    #drop unneeded columns
    bar_df = bar_df.drop(['cd', 'ct', 'dt', 'dist', 'rt', 'tt'], axis=1)
    
    #remove the poi if it appears in the data
    bar_df = bar_df[bar_df.displayId != display_id]
    
    #incase the poi was dropped reset the index (needed for colours to work)
    bar_df.reset_index(drop=True, inplace = True)
    
    #make sure it still works if less than 11 parts are present in the database
    robustness = min(10, len(bar_df)-1)
    
    #only accept the top robustness parts (usually the top eleven most used parts)
    bar_df = bar_df.iloc[0:robustness+1]
    
    #replace uris with urls
    bar_df['deff'] = uri_to_url(bar_df['deff'], instance, spoofed_instance)
    
    #change the final row in the dataframe (usually row 11)
    #poi row is added like this so the ordering of the columns doesn't have to match
    poi_row = pd.DataFrame.from_dict({'displayId':[display_id], 'title':[title], 'count':[count],
                 'roletog':[f"http://identifiers.org/so/SO:{str(role)}"], 'deff':[part_url]})
    bar_df.iloc[robustness] = poi_row.iloc[0]

    
    #define what colour each role should get (other is ignored)
    colormap = {
        'http://identifiers.org/so/SO:0000167': 'rgba(4,187,61,1)', 
        'http://identifiers.org/so/SO:0000139':'rgba(149,110,219,1)',
        'http://identifiers.org/so/SO:0000316':'rgba(119,157,205,1)',
        'http://identifiers.org/so/SO:0000141':'rgba(202,58,32,1)'
    }
        
    #get full identifiers form of role
    part_role = "http://identifiers.org/so/SO:0000167".replace("0000167", role)
    
    
    try:
        colours = [colormap[part_role]] #make colours based on colormap
    except KeyError:
        colours = ["rgba(255, 128,0,1)"] #oran geif part type is other
        
    #ensure the length of colours is as long as the dataframe (generally 10)
    colours = colours*len(bar_df.index) 
    
    #add the column  colour to the dataframe
    bar_df['color'] = pd.Series(colours, index=bar_df.index)
    
    #if columns lack a human readable name used the displayid instead
    bar_df.title[bar_df.title.isnull()] = bar_df.displayId[bar_df.title.isnull()]
    
    return(bar_df)
