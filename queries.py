#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pprint

# B.2. Data investigations with MongoDB ========================================

def get_db():
    ''' Creates connection to local MongoDB database.
    '''
    from pymongo import MongoClient
    client = MongoClient('localhost:27017')
    db = client.OpenStreetMap
    return db

db = get_db()

def aggregate(query):
    ''' Runs a MongoDB aggregation query on the connected database.

    In:
        query (string): An query using MongoDB's aggregation framework
    Out:
        list: List of documents returned by the query
    '''    
    return [doc for doc in db.Versailles.aggregate(query)]

    
# B.2.a. General statistics ====================================================

doc_count = [{"$group": {"_id": "Number of documents", "count":{"$sum": 1}}}]

print "\n B.2.a. GENERAL STATISTICS"
print "    o Number of documents:"
pprint.pprint(aggregate(doc_count))

node_count = [{"$match": {"type": "node"}},
              {"$group": {"_id": "$type", "count": {"$sum": 1}}}]

print "\n    o Number of nodes:"
pprint.pprint(aggregate(node_count))

way_count = [{"$match": {"type": "way"}},
             {"$group": {"_id": "$type", "count": {"$sum": 1}}}]

print "\n    o Number of ways:"            
pprint.pprint(aggregate(way_count))
 
 
# B.2.b. Specific statistics ===================================================
 
unique_uids = [{"$group": {"_id": "$created.uid", "count": {"$sum": 1}}},
               {"$group": {"_id": "Unique users", "count": {"$sum": 1}}}]

print "\n B.2.a. SPECIFIC STATISTICS"
print "    o Number of unique users who edited the data:"
pprint.pprint(aggregate(unique_uids))

top10_users = [{"$group": {"_id": "$created.user", "count": {"$sum": 1}}},
               {"$sort": {"count": -1}},
               {"$limit": 10}]

print "\n    o Top 10 contributors:"
pprint.pprint(aggregate(top10_users))

top10_cities = [{"$match": {"address.city": {"$exists": 1}}},
                {"$group": {"_id": "$address.city", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 10}]

print "\n    o Number of nodes per city (top 10):"
pprint.pprint(aggregate(top10_cities))

'''Cities edited by top 10 contributors:'''

# First we need to retrieve the top 10 users, but only for elements that have 
# a city name:
match = [{"$match": {"address.city": {"$exists": 1}}},
         {"$group": {"_id": "$created.user", "count": {"$sum": 1}}},
               {"$sort": {"count": -1}},
               {"$limit": 10},
         {"$project": {"_id": 1}}]

# Turn the result into a list of users:
user_list = [u[u'_id'] for u in aggregate(match)]
print "\nTop 10 contributors for elements that contain a city name:"
print user_list

# Use this list to filter down users:
cities_by_user = [{"$match": {"created.user": {"$in": user_list},
                              "address.city": {"$ne": None}}},
                  {"$group": 
                     {"_id": {"user": "$created.user", "city": "$address.city"},
                      "count": {"$sum": 1}}},
                  {"$sort": {"_id.user": 1}}]
print "\nNumber of contribution by these 10 users, by city:"
pprint.pprint(aggregate(cities_by_user))

# B.2.c. Visiting the Château de Versailles ====================================

tourism_spots = [{"$match": 
                      {"lat": {"$gte": 48.801217},
                       "lat": {"$lte": 48.828209},
                       "lon": {"$gte": 2.079505},
                       "lon": {"$lte": 2.123966},
                       "tourism": {"$exists": 1}
                      }
                 },
                 {"$group": {"_id": "$tourism", "count": {"$sum": 1}}}
                ]

print "\nB.2.c. VISITING THE CHATEAU DE VERSAILLES"
print "    o Tourist points of interest:"
pprint.pprint(aggregate(tourism_spots))

attractions = [{"$match": 
                      {"lat": {"$gte": 48.801217},
                       "lat": {"$lte": 48.828209},
                       "lon": {"$gte": 2.079505},
                       "lon": {"$lte": 2.123966},
                       "tourism": "attraction"
                      }
                 },
                 {"$project": {"_id": 0,
                               "attraction_name": "$name"}}
                ]

print "\n    o Attractions:"                
pprint.pprint(aggregate(attractions))

artworks = [{"$match": 
                      {"lat": {"$gte": 48.801217},
                       "lat": {"$lte": 48.828209},
                       "lon": {"$gte": 2.079505},
                       "lon": {"$lte": 2.123966},
                       "tourism": "artwork"
                      }
             },
             {"$group": {"_id": "$artwork_type",
                         "count": {"$sum": 1}}}
           ]

print "\n    o Artworks:"
pprint.pprint(aggregate(artworks))

fountains = [{"$match": 
                      {"lat": {"$gte": 48.801217},
                       "lat": {"$lte": 48.828209},
                       "lon": {"$gte": 2.079505},
                       "lon": {"$lte": 2.123966},
                       "amenity": "fountain"
                      }
              },
              {"$group": {"_id": "$amenity", "count": {"$sum": 1}}}
            ]

print "\n    o Fountains:"
pprint.pprint(aggregate(fountains))