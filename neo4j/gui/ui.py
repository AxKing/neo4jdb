import streamlit as st
import json
from streamlit_agraph import agraph, Node, Edge, Config
from neo4j import GraphDatabase
import pandas as pd

uri = "bolt://localhost:7687"  # Replace with your Neo4j server URI
username = "neo4j"
password = "password"


def get_basic_nodes(node_type):
    query = f'MATCH (n:{node_type}) RETURN n;'
    with GraphDatabase.driver(uri, auth=(username, password)) as driver:
       nodes, summary_obj, key_list = driver.execute_query(query)
    return nodes

def doc_by_entity(entity):
       query = f"""MATCH (e:Entity {{name: '{entity}'}})<-[:mentions]-(s:Snippet)-[:was_found_in]->(d:Document) RETURN DISTINCT d;"""
       with GraphDatabase.driver(uri, auth=(username, password)) as driver:
              records, summary_obj, key_list = driver.execute_query(query)
              return records

def doc_in_date_range(entity, date1, date2):
    yr1, m1, d1 = date1.split('-')
    yr2, m2, d2 = date2.split('-')
    query = f"""
    MATCH (e:Entity {{name: '{entity}'}})<-[:mentions]-(s:Snippet)-[:was_found_in]->(d:Document) 
    WHERE d.date >= date({{year:{yr1}, month:{m1}, day:{d1}}})
    AND d.date <= date({{year:{yr2},month:{m2},day:{d1}}})
    RETURN DISTINCT d;"""
    with GraphDatabase.driver(uri, auth=(username, password)) as driver:
        records, summary_obj, key_list = driver.execute_query(query)
    return records

# This is the main dropdown
query_selection = st.selectbox(
    'Please select the Query you\'d like to run...',
    (
       'SELECT QUERY', 
       'List all Document Nodes', 
       'List all Entity Nodes', 
       'List all Category Nodes', 
       'Pick an entity and see their documents', 
       'Test Query')
)
if query_selection == 'List all Document Nodes':
       doc_records = get_basic_nodes('Document')
       data = []
       for record in doc_records:
              node = record['n']
              data.append({"name": node['name'],
              "url": node['url'],
              'date': node['date']})
       df = pd.DataFrame(columns=['name', 'url', 'date'], data=data)
       #        st.write(node['name'], node['url'], node['date'])
       st.write(df)

if query_selection == 'List all Entity Nodes':
       data = []
       ent_records = get_basic_nodes('Entity')
       for record in ent_records:
              node = record['n']
              data.append({"name": node['name']})
       df = pd.DataFrame(columns=['name'], data=data)
       #        st.write(node['name'], node['url'], node['date'])
       st.write(df)

if query_selection == 'List all Category Nodes':
       data = []
       cat_records = get_basic_nodes('Category')
       for record in cat_records:
              node = record['n']
              data.append({"name": node['name']})
       df = pd.DataFrame(columns=['name'], data=data)
       st.write(df)

if query_selection == "Pick an entity and see their documents":
       data = ['Select Entity']
       ent_records = get_basic_nodes('Entity')
       for record in ent_records:
              node = record['n']
              data.append(node['name'])
       data = tuple(data)
       
       query_selection = st.selectbox(
       'Please select the Query you\'d like to run...',
       data
       )
       if query_selection != 'Select Entity':
              # Given an Entity name, return all documents
             
              docs = doc_by_entity(query_selection)
              data = []
              for record in docs:
                     node = record['d']
                     data.append({"name": node['name'],
                            "url": node['url'],
                            'date': node['date']})
              df = pd.DataFrame(columns=['name', 'url', 'date'], data=data)
              st.write(df)


if query_selection == 'Pick and Entity and a date range, return documents':
# Given an Entity and a date range, return all documents
# Requires entity name, and two dates.
# date1 < date2
       data = ['Select Entity']
       ent_records = get_basic_nodes('Entity')
       for record in ent_records:
              node = record['n']
              data.append(node['name'])
       data = tuple(data)



# Example
entity = 'FDA'
date1 = '2020-2-15'
date2 = '2023-12-31'
docs = doc_in_date_range(entity, date1, date2)
for doc in docs:
    node = doc['d']
    print(node['name'], node['url'])









if query_selection == 'Test Query':
       query = 'match (u)<-[e]-(v) return u,e,v limit 10'
       with GraphDatabase.driver(uri, auth=(username, password)) as driver:
              records, summary_obj, key_list = driver.execute_query(query)
              used_node_ids = set()
              nodes = []
              edges = []
              # st.write(records)
              for u, e, v in records:
                     # st.write(e)
                     st.write("u:", u,"e:", e,"v:", v)
                     if u.element_id not in used_node_ids:
                            used_node_ids.add(u.element_id)
                            nodes.append( Node(id=u.element_id, 
                                   size=25,
                                   label = list(u.labels)[0],
                                   shape="circle",
                                   ))
                     if v.element_id not in used_node_ids:
                            used_node_ids.add(v.element_id)
                            nodes.append( Node(id=v.element_id, 
                                   size=25, 
                                   shape="circle",
                                   ))
                     edges.append( Edge(source=v.element_id, 
                     label=e.type, 
                     target=u.element_id, 
                     # **kwargs
                   ) 
            )
              config = Config(width=750,
                height=950,
                directed=True, 
                physics=True, 
                hierarchical=False,
                # **kwargs
                )

              return_value = agraph(nodes=nodes, 
                      edges=edges, 
                      config=config)
# <Relationship element_id='5:7191aa7a-6f49-473d-8f94-a87c74fc2fc7:4' 
# nodes=(
# <Node element_id='4:7191aa7a-6f49-473d-8f94-a87c74fc2fc7:61' 
#      labels=frozenset({'Snippet'})  
#      properties={'text': 'Nibh praesent tristique magna sit. Porttitor leo a diam sollicitudin tempor id eu nisl. Varius vel pharetra vel turpis nunc eget lorem.'}>, 
# <Node element_id='4:7191aa7a-6f49-473d-8f94-a87c74fc2fc7:59' 
# labels=frozenset({'Entity'}) properties={'name': 'Eco Nest Homes'}>) 
# type='mentions' properties={}>




# nodes.append( Node(id="Captain_Marvel", 
#                    size=25,
#                    shape="circularImage",
#                    image="http://marvel-force-chart.surge.sh/marvel_force_chart_img/top_captainmarvel.png") 
#             )


# config = Config(width=750,
#                 height=950,
#                 directed=True, 
#                 physics=True, 
#                 hierarchical=False,
#                 # **kwargs
#                 )

# return_value = agraph(nodes=nodes, 
#                       edges=edges, 
#                       config=config)