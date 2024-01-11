import streamlit as st
import json
from streamlit_agraph import agraph, Node, Edge, Config
from neo4j import GraphDatabase
import pandas as pd
import datetime

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
    yr1, m1, d1 = int(yr1), int(m1), int(d1)
    yr2, m2, d2 = date2.split('-')
    yr2, m2, d2 = int(yr2), int(m2), int(d2)
    query = f"""
    MATCH (e:Entity {{name: '{entity}'}})<-[:mentions]-(s:Snippet)-[:was_found_in]->(d:Document) 
    WHERE d.date >= date({{year:{yr1}, month:{m1}, day:{d1}}})
    AND d.date <= date({{year:{yr2},month:{m2},day:{d1}}})
    RETURN DISTINCT d;"""
    with GraphDatabase.driver(uri, auth=(username, password)) as driver:
        records, summary_obj, key_list = driver.execute_query(query)
    return records

def cat_by_entity(entity):
    query = f"""
    MATCH (e:Entity {{name: '{entity}'}})<-[:mentions]-(s:Snippet) -[:relates_to]->(c:Category)
        RETURN DISTINCT c"""
    with GraphDatabase.driver(uri, auth=(username, password)) as driver:
        records, summary_obj, key_list = driver.execute_query(query)
    return records

def entities_by_doc(document):
    query = f"""
    MATCH(d:Document {{name: '{document}'}}) <-[:was_found_in]-(s:Snippet)<-[:mentions]->(e:Entity)
        RETURN DISTINCT e"""
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
       'Pick an Entity and see their documents',
       'Pick an Entity and a date range, and return documents that mention them',
       'Pick an Entity and see what categories they have been related to',
       'Select a Document and see the Entities it mentions', 
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

if query_selection == 'Pick an Entity and see their documents':
       data = ['Select Entity']
       ent_records = get_basic_nodes('Entity')
       for record in ent_records:
              node = record['n']
              data.append(node['name'])
       data = tuple(data)
       
       query_selection = st.selectbox(
       'Please select the Entity:',
       data
       )
       if query_selection != 'Select Entity':
              # Given an Entity name, return all documents
             
              docs = doc_by_entity(query_selection)
              data = []
              for record in docs:
                     node = record['d']
                     data.append({"doc name": node['name'],
                            "url": node['url'],
                            'date': node['date']})
              df = pd.DataFrame(columns=['doc name', 'url', 'date'], data=data)
              st.write(df)


if query_selection == 'Pick an Entity and a date range, and return documents that mention them':
       data = ['Select Entity']
       ent_records = get_basic_nodes('Entity')
       for record in ent_records:
              node = record['n']
              data.append(node['name'])
       data = tuple(data)
       
       query_selection = st.selectbox(
       'Please select the Entity:', data
       )
       if query_selection != 'Select Entity':
              date1 = st.date_input("Show articles from:", datetime.date(1995, 3, 20))
              date2 = st.date_input("through:", datetime.date(2023, 7, 18))
              date1, date2 = str(date1), str(date2)
              docs = doc_in_date_range(query_selection, date1, date2)
              data = []
              for record in docs:
                     node = record['d']
                     data.append({"article name": node['name'],
                            "url": node['url'],
                            'date': node['date']})
              df = pd.DataFrame(columns=['article name', 'url', 'date'], data=data)
              st.write(df)



if query_selection == 'Pick an Entity and see what categories they have been related to':
       data = ['Select Entity']
       ent_records = get_basic_nodes('Entity')
       for record in ent_records:
              node = record['n']
              data.append(node['name'])
       data = tuple(data)
       
       query_selection = st.selectbox(
       'Please select the Entity:', data
       )
       if query_selection != 'Select Entity':
              docs = cat_by_entity(query_selection)
              data = []
              for record in docs:
                     node = record['c']
                     data.append({"category name": node['name']})
              df = pd.DataFrame(columns=['category name'], data=data)
              st.write(df)


if query_selection == 'Select a Document and see the Entities it mentions':
       data = ['Select Document']
       ent_records = get_basic_nodes('Document')
       for record in ent_records:
              node = record['n']
              data.append(node['name'])
       data = tuple(data)
       
       query_selection = st.selectbox(
       'Please select a Document:', data
       )
       if query_selection != 'Select Document':
              docs = entities_by_doc(query_selection)
              data = []
              for record in docs:
                     node = record['e']
                     data.append(node['name'])
              df = pd.DataFrame(columns=['Mentioned Entities'], data=data)
              st.write(df)
              