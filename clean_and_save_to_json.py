#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import xml.etree.cElementTree as ET
import pprint


# A.1.a. Data tags =============================================================

filename = './Versailles.osm/Versailles.osm'

def count_tags(filename):
    ''' Identifies unique tag types and counts occurences for each
    In:
        filename (string): Path to OSM XML file to assess
    Out:
        dict: Unique tag types as keys, counts as values   
    '''     
    tags = {}
    context = ET.iterparse(filename, events = ('start',))  # Detect starts only
    for event, elem in context:     # Go through each element in the OSM XLM file
        if not(elem.tag in tags):   # Create new dict key if not already there    
            tags[elem.tag] = 0      
        tags[elem.tag] += 1         
    return tags
    
print "\nA.1.a. DATA TAGS:"
pprint.pprint(count_tags(filename))
raw_input("Press Enter to continue...")


# A.1.b. Latitude / longitude ==================================================

lat_bounds = (48.7582257, 48.9188896)  # Bounds of the selected map area
lon_bounds = (2.0190811, 2.1783828)

def is_number(s):
    ''' Returns True if string or float s is or can be coerced into a float, 
    False otherwise'''
    try:
        float(s)
        return True
    except ValueError:
        return False
        
def is_within_bounds(f, bounds):
    ''' Checks whether f is within the interval defined by bounds
    In:
        f (float): Value to test
        bounds (tuple): lower, upper bounds of the interval where f might be 
                        included.
    Out:
        bool: True if f is contained in the interval (equality allowed),
              False if f is strictly lower than lower bound or strictly greater
              than upper bound.
    '''
    if f >= bounds[0] and f <= bounds[1]:
        return True
    return False
               
def check_positions(filename):  
    ''' Checks latitude and longitude for validity and accuracy
    In:
        filename (string): Path to the file to check
    Out:
        dict: Values = Counts of the following occurences (used as keys):
            Null -- at least one of latitude and longitude is None
            Empty -- at least one of latitude and longitude is ""
            Non_number -- at least one of latitude and longitude is not a 
                          float or cannot be coerced into a float
            Out_of_bounds -- at least one of latitude and longitude is outside
                             the bounds of the selected map area
            Correct -- none of the above occurs
    '''
    counts = {'Null': 0, 'Empty': 0, 'Non_number': 0, 'Out_of_bounds': 0, 
              'Correct': 0}
    context = ET.iterparse(filename, events = ('start', )) # Detect starts only
    for event, elem in context:
        if elem.tag == 'node':  # Check for each node element
            lat = elem.get('lat').strip()  # Get rid of unwanted spaces
            lon = elem.get('lon').strip()
            if (lat is None or lon is None):
                counts['Null'] += 1
            elif (lat == "" or lon == ""):
                counts['Empty'] += 1
            elif not (is_number(lat) and is_number(lon)):
                counts['Non_number'] += 1
            elif not (is_within_bounds(float(lat), lat_bounds) and 
            is_within_bounds(float(lon), lon_bounds)):  
            # If lat or lon is out of bounds:
                counts['Out_of_bounds'] += 1
            else:
                counts['Correct'] += 1
    return counts

print "\nA.1.b. LATITUDE / LONGITUDE:"    
pprint.pprint(check_positions(filename))
raw_input("Press Enter to continue...")


# A.1.c. Postcode format ======================================================

import re

postcode_re = re.compile(r'^\d{5}$')  # Regex match to an isolated string of 
                                      # 5 consecutive digits

def audit_postcodes(filename):
    ''' Checks postocde to ensure every tag with an addr:postcode key has a postcode 
    value and that they follow the standard French postcode format (5 
    consecutive digits)
    In:
        filename (string): Path to the file to check
    Out:
        dict: Values = Counts of the following occurences (used as keys):
            Null -- there is a postcode key but no value (None)
            Empty -- there is a postcode key but its value is ""
            Incorrect -- there is a postcode key but its value does not follow 
                         the convention
            Correct -- none of the above occurs
    '''
    counts = {'Null': 0, 'Empty': 0, 'Incorrect': 0, 'Correct': 0}
    context = ET.iterparse(filename, events = ('start', )) # Detect starts only
    for event, elem in context:
        if elem.tag == 'node':
            for elt in elem.findall('tag'):
                if elt.get('k') == 'addr:postcode':  
                # If the tag contains a postcode field
                    pc = elt.get('v').strip()  # Then get the postcode value
                    if pc == None:
                        counts['Null'] += 1
                    elif pc == "":
                        counts['Empty'] += 1
                    elif not re.match(postcode_re, pc): 
                    # If not in line with the 5-digit convention:
                        counts['Incorrect'] += 1
                    else:
                        counts['Correct'] += 1
    return counts
    
print "\nA.1.c. POSTCODE FORMAT:"
pprint.pprint(audit_postcodes(filename))
raw_input("Press Enter to continue...")


# A.1.d. Street / way types ====================================================

from collections import defaultdict

street_type_re = re.compile(r'^\S+\.?', re.IGNORECASE)  # Regex to find 
# continuous groups of non-whitespace characters, each possibly ending with a .

# List of expected types of streets and ways:
expected = [u"rue", u"avenue", u"boulevard", 
            u"route", u"place", u"villa", 
            u"impasse", u"passage", u"voie", 
            u"square", u"sentier", u"ruelle",
            u"allée", u"chemin", 
            u"rond-point", u"cours",
            u"parc", u"promenade", u"résidence", 
            u"domaine", u"quai", u"cour", u"clos",
            u"autoroute", u"route nationale", 
            u"route départementale", 
            u"route communale", u"hameau"]

def audit_street_type(street_types, street_name):
    ''' For each street name, selects the first word (assumed to be street type) and
    compares with the list of expected street types. 
    In case it is not there:
    The street_types dict (passed by the upper environment) uses the unexpected 
    street type as a key and the full street name is added to the value (which
    is a set).
    
    In: 
        street_types (dict of sets): Keys are unique unexpected street types, 
            values are sets of full street names with these street types. These 
            sets get updated in place by the function.
        street_name (string): The street name to parse and compare with the list
            of expected street types.
    Out:
        Nothing
    '''
    m = street_type_re.search(street_name)
    if m:
        street_type = unicode(m.group())  # Convert to unicode because of French-specific characters
        if street_type.lower() not in expected:
            street_types[street_type].add(street_name)  # Record all streets 
            # with unexpected street types


def is_street_name(elem):
    ''' Checks whether a 'tag' element of the OSM XML file refers to a street name.
    Returns True if this is the case, False if not.
    '''
    return (elem.attrib['k'] == "addr:street")
    

def audit_all_streets(filename):
    ''' Applies audit_street_type to all elements of the OSM XML file containing a
    street name. Returns the collection of unexpected street types in the form 
    of a dictionary where key = unexpected street type, value = set of street
    names with this street type.
    
    In:
        filename (string): Path to the file to check
    Out:
        dict: Keys are unique street types not found in the reference list 
        ("expected"), values are sets containing all unique street names with
        these street types.
    '''
    osm_file = open(filename, "r")
    street_types = defaultdict(set)
    
    for event, elem in ET.iterparse(osm_file, events = ("start",)): 
                                                            # Detect starts only
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):  # Iterate through all "tag" elements
                if is_street_name(tag):   # Audit street type when the element 
                                          # contains a street name
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types

'''Values to replace and to be repaced with:'''
street_mapping = { u"allee": u"Allée",
            u"Allee": u"Allée",
            u"hameau": u"Hameau",
            u"Residence": u"Résidence",
            u"résidence": u"Résidence",
            u"Centre Commercial Régional": u"Centre Commercial",
            u"Centre commercial": u"Centre Commercial",
            u"C.C.": u"Centre Commercial",
            u"CCR": u"Centre Commercial",
            u"\xc9lys\xe9e 2": u"Résidence \xc9lysée 2",
            u"Aérodrome - ": u"",
            u"Otis": u"Avenue Otis",
            u"Jean Macé": u"Rue Jean Macé",
            u"Guyancourt": u"Rue Louis Breguet"
            }

def update_street_name(street_name, mapping):
    ''' Uses the mapping dictionary to correct street types: For each key in 
    mapping, looks for it in street_name and replaces this string with the 
    associated value (which is the correctly spelled street type).
    
    In: 
        street_name (string): Full street name possibly requiring a correction
        mapping (dictionary): Keys are wrongly spelled street types, values are
            strings to use as replacements within street_name.
    Out:
        string: Correctly spelled street name.
    '''
    for bad_name in mapping:
        match = re.compile('^' + bad_name)
        try:  # Substitute the string bad_name with the associated value in 
              # mapping. The rest of the street_name string is untouched.
            street_name = re.sub(match, mapping[bad_name], street_name)
        except LookupError:  # If this happens, we need to manually amend the 
                             # mapping.
            print "Missing entry in mapping"
            continue
    return street_name


street_types = audit_all_streets(filename)
print "\nA.1.d. STREET / WAY TYPES:"
print "    o Unexpected street types:"
pprint.pprint(street_types.keys())  # Print unexpected street types (without the
                                    # related street names)
raw_input("Press Enter to continue...")

print "\n    o Transforming street names:"
for street_type, ways in street_types.iteritems():  
# For each unexpected street type:
    for street_name in ways:
        better_name = update_street_name(street_name, street_mapping)  
        # Display replacements:
        if street_name != better_name:
            print street_name, "=>", better_name
raw_input("Press Enter to continue...")


# A.2. Accuracy and consistency ================================================

from difflib import SequenceMatcher
import csv

pc_cities = set()
    
with open(filename, 'r') as osm_file:
    for event, elem in ET.iterparse(osm_file, events = ("start",)):
        if elem.tag == "node" or elem.tag == 'way':
            pc_tag = elem.find("./tag[@k='addr:postcode']")  # Use XPath command
            # to locate postcode in node or way
            try:
                elem_pc = pc_tag.attrib['v']
            except AttributeError:  # Case no tag attribute 'v'
                elem_pc = None
            
            city_tag = elem.find("./tag[@k='addr:city']")  # Use XPath command 
            # to locate city in node or way
            try:
                elem_city = city_tag.attrib['v']
            except AttributeError:  # Case no tag attribute 'v'
                elem_city = None
            if not (elem_pc is None and elem_city is None): # As long as at 
            # least one of postcode or city name exists, add to set:
                pc_cities.add((elem_pc, elem_city))
                
print "\nA.2. ACCURACY AND CONSISTENCY"            
print "\n    o All postcode / city combinations in file:"    
pprint.pprint(pc_cities)
raw_input("Press Enter to continue...")

city_to_pc_map = {
     u'78170': '78170',
     u'Bougival': '78380',
     u'Buc': '78530',
     u'Croissy-sur-Seine': '78290',
     u'Guyancourt': '78280',
     u'La Celle-Saint-Cloud': '78170',
     u'Le Chesnay': '78150',
     u'le Chesnay': '78150',
     u'Le V\xe9sinet': '78110',
     u'Marly-le-Roi': '78160',
     u'Montesson': '78360',
     u'Montigny-le-Bretonneux': '78180',
     u'Noisy-le-Roi': '78590',
     u'Roquencourt': '78150',
     u"Saint-Cyr-l'\xc9cole": '78210',
     u'Saint-Germain-en-Laye': '78100',
     u'Versailles': '78000',
     u'Viroflay': '78220'}

pc_to_city_map = {
    '78103': 'St Germain En Laye',
    '78101': 'St Germain En Laye',
    '78884': 'St Quentin En Yvelines',
    '92852': 'Rueil Malmaison'
}

laposte_file = './Reference/laposte_hexasmal.csv'

def parse_reference_file(filename):
    ''' Take the reference file from La Poste and parse into a dictionaty with 
    postcode as keys. Several towns can have the same postcode, therefore each 
    dict value is a list.
    
    In: 
        filename (string): Path to the reference file to parse
    Out:
        dict of lists: Keys = postcodes, Values = lists of city names associated
            to the key postcode.
    '''    
    data = defaultdict(list)
    with open(filename, 'r') as f:
        reader = csv.reader(f, delimiter = ';') # French CSVs use ; separators
        reader.next()
        for row in reader:
            data[str(row[2])].append(row[1].title())  # Use titlecase everywhere
            # for consistency
    return data
    
def get_pc_from_city(city):
    ''' Returns postcode given city name, using the manually-defined 
    "city_to_pc_map" mapping'''
    return city_to_pc_map[city]

def get_city_from_pc(pc, city, reference):
    ''' Return a correct city name given postcode and a possibly incorrect city 
    name, using the reference file. Because a postcode key can have several city
    values in the reference file, we return the city name with the highest 
    similarity to the city name that we are trying to check/correct.
    
    In:
        pc (string): Postcode for the PC / City combination we are assessing
        city (string): City name for the same.
        reference (dict of lists): Reference data parsed from the reference file
            where keys = postcodes and values = lists of city names associated
            with the key postcode.
    Out:
        string: Corrected city name.
    '''
    if city:
        best_match = [None, 0.] 
        # Initialise: best_match[0] is for the best-matching city name, 
        # best_match[1] is for the match ratio of best_match[0] with the 'city' 
        # string.
        for c in reference[pc]:  # For each city name associated with this 
                                 # particular postcode:
            match_ratio = SequenceMatcher(None, c, city.title()).ratio()  
            # Calculate similarity
            if match_ratio >= best_match[1] or best_match[1] == 0:
                best_match[0] = c  # This is our new best match
                best_match[1] = match_ratio
        #print 'City present:', city, 'Returning best match:', best_match[0]
        return best_match[0]
    else:  # If there is a postcode but no city name in the OSM data, we pick 
           # the first city name associated with this postcode in the reference 
           # dictionary.
        try:          
            reference[pc][0]  
            # print 'No city: Returning first value:', reference[pc][0]
            return reference[pc][0] 
        except IndexError:
            # print 'No city found for postcode', pc
            return
        
def correct_pc_city(pc, city, reference):
    ''' Given a postcode and a city name (both potentially incorrect, and one or the
    other can be missing -- note that if both are missing, this function is not 
    even called):
    - Gets the correct postcode from the city name using get_pc_from_city() + 
    one "manual" adjustment to correct a typo in the data
    - Once all cities have the correct postcode, fix all city names by applying
    get_city_from_pc(). This ensures all city names are correct and follow the
    same spelling and case conventions.
    - Finally, correct four cases where special delivery postcodes are used, 
    which cannot be found in the reference data. This uses the pc_to_city_map
    dictionary.

    In:
        pc (string): Postcode, potentially None or incorrect
        city (string): City name, potentially None or incorrect
        reference (dict of lists): Reference data parsed from the reference file
            where keys = postcodes and values = lists of city names associated
            with the key postcode.
    Out:
        tuple of strings: Corrected postcode, corrected city name
    '''

    '''First step: ensure each city has a valid postcode. '''
    if pc is None: 
        new_pc = get_pc_from_city(city)  # Use the city name to get the postcode
        #print 'No Postcode, returning value from map:', new_pc
    else:
        if pc == '78530' and city == 'Jouy-en-Josas':  # We found one typo where
            # two postcodes got confused for one another
            new_pc = '78350'
        else:
            new_pc = pc  # In the general case keep the same postcode.
        #print 'Postcode present, returning same value (except Jouy en Josas):' \
        #, new_pc
    
    ''' Second step: ensure all postcodes have a correctly formatted city:'''
    new_city = get_city_from_pc(new_pc, city, reference)

    ''' Third step: correct the last four cases where postcode is 
    missing from the reference file, using our second manually-defined 
    mapping.'''
    if new_pc in pc_to_city_map:
        new_city = pc_to_city_map[new_pc]
        
    return new_pc, new_city
            

ref_data = parse_reference_file(laposte_file)

pc_city = set()
for pc, city in pc_cities:  # Apply correct_pc_city() to all postcode/city 
    # combinations found in the OSM XML file:
    new_pc, new_city = correct_pc_city(pc, city, ref_data)
    #print 'OUTCOME: ', new_pc, new_city, '\n'
    pc_city.add((new_pc, new_city))
    
print "\n    o All postcode/city combinations after corrections:"        
pprint.pprint(pc_city)  # Outcome of our manipulations
raw_input("Press Enter to continue...")


# B.1. Data load into a MongoDB database =======================================
''' Data schema to use in the output JSON file:

[...,
    {
    "id": "2406124091",
    "type: "node",
    "visible":"true",
    "created": {
              "version":"2",
              "changeset":"17206049",
              "timestamp":"2013-08-03T16:43:42Z",
              "user":"linuxUser16",
              "uid":"1219059"
            },
    "lat": 41.9757030,
    "lon": -87.6921867,
    "address": {
              "housenumber": "5157",
              "postcode": "60625",
              "street": "North Lincoln Ave"
            },
    "amenity": "restaurant",
    "cuisine": "mexican",
    "name": "La Cabana De Don Luis",
    "phone": "1 (773)-271-5176"
    },
...
]

'''

import codecs
import json
from random import sample, seed
seed(123)

lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')  # Regex for two pieces
# of lowercase strings separated by a colon character
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')  # Regex for any
# potentially problematic character

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]  
# Keys to retain in the 'created' field

def process_tags(tag, tag_id):
    ''' Parses node tags and way tags as per convention. Assumes no problematic 
    characters.
    
    In:
        tag (XML element): A node or way's "tag" sub-element from the OSM XML
            data
        tag_id (string): The node or way's "id" attribute
    Out:
        dict: Contains the following key:value pairs:
            'id': node or way id
            'key': "tag" sub-element's key (anything after the colon in the 
                'k' attribute)
            'value': "tag" sub-element's value ('v' attribute)
            'type': "tag" sub-element's type (anything before the colon in the 
                'k' attribute) if there is a colon, None otherwise
    '''
    k = tag.get('k').strip()
    v = tag.get('v').strip()
    if re.match(lower_colon, k):  # If there is a ':' in the tag key:
        tag_type, tag_key = k.split(':', 1)  # tag_type is anything before ':', 
                                             # tag_key is anything after
        tag_value = v
        if tag_type == "addr":
            tag_type = "address"  # Use correct spelling
    else:   # If there isn't a ':' in the tag key:
        tag_type = None  # Returns None as the tag type
        tag_key = k
        tag_value = v
    return  {'id': tag_id, 'key': tag_key, 'value': tag_value, 'type': tag_type}
    # Return as a dict for convenience
    
def shape_element(element):
    ''' Converts an XML element to the selected JSON schema.
        
    In:
        element (XML element): An element from the OSM XML datafile.
    Out:
        dict: A dictionary with keys and values as per the defined JSON schema.
    '''
    node = {}
    if element.tag == "node" or element.tag == "way" :
        ''' The following values are pulled directly from the XML data:'''
        node['id'] = element.get('id')
        node['type'] = element.tag
        node['visible'] = element.get('visible')
        node['created'] = {n: element.get(n) for n in CREATED} 
        # 'created' is a dict of dicts
        try:
            node['lat'] = float(element.get('lat'))  # Convert coordinates to 
                                                # floats if not already the case
            node['lon'] = float(element.get('lon')) 
        except TypeError:
            node['lat'] = element.get('lat')
            node['lon'] = element.get('lon')
        
        '''"Tag" sub-elements require specific treatment:'''
        for t in element.findall('tag'):  # For each sub-element tagged "tag":
            if not re.match(problemchars, t.get('k')) and \
                len(re.findall(':', t.get('k'))) <= 1: 
            # (i.e. ignore when there are problem chars or more than one ':')
                tag_content = process_tags(t, element.get('id'))  
                # Parse tag and extract id, key, value and type
                if tag_content['type'] is not None:  
                # ie. if the 'k' field contained a colon character
                    if (tag_content['type'] not in node.keys()) or \
                        not (isinstance(node[tag_content['type']], dict)):
                    # Initialise an empty dict if there is no key of this 'type'
                    # or its value is not already a dict
                        node[tag_content['type']] = {}
                    node[tag_content['type']][tag_content['key']] = \
                        tag_content['value']
                    # for instance: node['address']['postcode'] = '78100'
                else: # ie. if the 'k' field didn't contain a colon character
                    node[tag_content['key']] = tag_content['value']
        
        ''' For "nd" tags, we collect all nodes contained in the way:'''
        for t in element.findall('nd'):  
            if 'node_refs' not in node.keys():
                node['node_refs'] = []
            node['node_refs'].append(t.get('ref'))
                    
        return node
    else:
        return None


def process_map(file_in, pretty = False):
    ''' Iterates through the OSM file and saves it into a correctly formatted JSON 
    file, applying cleaning procedures along the way.
    
    In:
        file_in (string): Path to OSM XML file to clean up and convert to JSON
        pretty (bool): If True, add whitespaces as required to the JSON file to
            ensure a pretty formatting. False (default) for large data as 
            prettyfying is expansive.
    Out:
        list of dicts: JSON-formatted data, identical to the data saved to disk.
    '''
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)  # Create a properly shaped JSON-type 
                                         # element as per defined schema.
            if el:           
                ''' Apply cleaning procedures to the address fields: 
                street names, postcodes and cities: '''
                if 'address' in el: 
                    if 'street' in el['address']:  # Clean up street names
                        el['address']['street'] = \
                            update_street_name(
                                el['address']['street'], street_mapping
                                              )
                    if 'postcode' in el['address'] or 'city' in el['address']:  
                    # Clean up postcodes & cities
                    # We ensure either postcode or city (or both) is present
                        try:
                            pc = el['address']['postcode']  # Postcode present
                        except KeyError:
                            pc = None  # Postcode is absent
                        try:
                            city = el['address']['city']  # City present
                        except KeyError:
                            city = None  # City is absent
                        el['address']['postcode'], el['address']['city'] = \
                            correct_pc_city(pc, city, ref_data) 
                        # Apply clean-up function to postcode and city name
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")  # Prefered for large 
                    # datasets as prettyfying the JSON file is expansive
    return data

data = process_map('./Versailles.osm/Versailles.osm', False)

print "\nB.1. DATA LOAD INTO A MONGODB DATABASE"
print "    o Data sample:"
pprint.pprint(sample(data, 5))