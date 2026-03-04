import json
import requests
from pandas import json_normalize

def input_data(uri, instance, token = None):
    """
    Finds information about an SBOL part based on its uri
    
    Requirements
    -------
    import json
    import requests
    from pandas import json_normalize
    Input_Query.txt
    
    Parameters
    ----------
    uri : string
        the unique identifier of a part, note that due to spoofing it may not be the same as the url
        e.g. uri = 'https://synbiohub.org/public/igem/BBa_E0040/1' (url may be https://dev.synbiohub.org/public/igem/BBa_E0040/1)
    instance : string
        the synbiohub instance where information is to be retrieved from (where the sparql query is to be run)
        e.g. 'https://synbiohub.org/'
    
    Returns
    -------
    self_df: pandas dataframe, shape()
        Dataframe with the columns: 'count' (same as count below), 'deff' (uri), 'displayId' (same as display_id below),
        'title' (same as title below), 'role' (same as role below)
    display_id: string
        The display id of the poi e.g. 'BBa_E0040'
    title: string
        The human readable name of the poi e.g. 'GFP'
    role: string
        The number (as a string) of the sequence ontology of the role of the poi e.g. '0000316'    
    count: integer
        The number of times the poi is used (how often it is a subpart) e.g. 2348
       
    Example
    --------
    self_df, display_id, title, role, count = input_data('https://synbiohub.org/public/igem/BBa_E0040/1', 'https:dev.synbiohub.org/')
    
    Output: 
        self_df: (dataframe with 1 row with index zero, columns shown below in the correct order)
            count                                                  2348
            deff          https://synbiohub.org/public/igem/BBa_E0040/1
            display_id                                        BBa_E0040
            title                                                   GFP
            role                                                0000316
        display_id: 'BBa_E0040'
        title: 'GFP'
        role: '0000316'
        count: 2348
    """
        
    status = 200
    
    headers = {}
    if token is not None:
        headers['X-authorization'] = token
    req = requests.get(instance, headers=headers)
    if req.status_code != 200: #if synbiohub is offline return an error
        status = 424
    else:
        fl = open("Input_Query.txt", "r")
        sparqlquery = fl.read()
        
        #replace the uri in the pre written sparql query with the uri of the part
        sparqlquery = sparqlquery.replace('https://synbiohub.org/public/igem/BBa_B0012/1',uri)

        #accept repsonses
        r = requests.post(instance+"sparql", data = {"query":sparqlquery}, headers = {"Accept":"application/json", "X-authorization": token} if token is not None else {"Accept":"application/json"})
        
        #format responses
        d = json.loads(r.text)
        a = json_normalize(d['results']['bindings'])
        
        #renames columns
        rename_dict = {'count.datatype':'cd', 'count.type':'ct', 'count.value':'count', 'def.type':'dt', 'def.value':'deff', 'displayId.type':'dist', 'displayId.value':'displayId', 'role.type':'rt', 'role.value':'roletog', 'title.type':'tt', 'title.value':'title'}
        a.columns = [rename_dict[col] for col in a.columns]
        
        #split column roletog at SO: to leave the http://identifiers.org/so in the column http
        #and the roler number (e.g. 0000141) in the column role
        a[['http','role']] = a.roletog.str.split("SO:",expand=True) 
        
        #drop unnecessary columns to leave: ['count', 'deff', 'displayId', 'title', 'role']
        a = a.drop(['cd', 'ct', 'dt', 'dist', 'rt', 'roletog', 'tt', 'http'],axis=1)
        
        #creates a df that has only one row (where the deff is the part in question)
        self_df = a[a.deff == uri]
        
        #obtains the displayid using the self df
        display_id = self_df['displayId'][0]
        
        #obtains the title/human readable name using the self df
        title = self_df['title'][0]
        
        #in case there was no title
        if str(title) == "nan":
            title = display_id
            
        #obtains the role (as a number, e.g. 000141) using the self df
        role = self_df['role'][0]
        
        #obtains the count using the self df
        count = self_df['count'][0]
        
    return (self_df, display_id, title, role, count)
