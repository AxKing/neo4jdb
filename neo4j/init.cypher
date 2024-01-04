// Creating constraints for the data before the nodes
CREATE CONSTRAINT entity_name IF NOT EXISTS
FOR (entity:Entity) REQUIRE entity.name IS UNIQUE
;

CREATE CONSTRAINT document_name IF NOT EXISTS
FOR (doc:Document) REQUIRE doc.name IS UNIQUE
;

CREATE CONSTRAINT document_url IF NOT EXISTS
FOR (addy:Document) REQUIRE addy.url IS UNIQUE
;

CREATE CONSTRAINT esg_cat IF NOT EXISTS
FOR (cat:Category) REQUIRE cat.name IS UNIQUE
;



MATCH (n) DETACH DELETE n
;
LOAD CSV with headers  FROM  'file:///esg_document_test_data_demo.csv' AS line 
MERGE (doc_node:Document {name: line.document_name, url: line.document_url, date: date(line.document_date)})
MERGE (ent_node:Entity {name: line.entity_name})
MERGE (cat_node:Category {name: line.esg_category})
CREATE (snip_node:Snippet {text: line.esg_object})
CREATE (snip_node)-[:was_found_in]->(doc_node)
CREATE (snip_node)-[:mentions]->(ent_node)
CREATE (snip_node)-[:relates_to {predicate:line.esg_predicate}]->(cat_node)
;
