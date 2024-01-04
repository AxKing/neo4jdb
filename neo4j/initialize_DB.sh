#!/bin/bash

# Neo4j database credentials
NEO4J_USER="neo4j"
NEO4J_PASSWORD="password"

# Path to your Cypher script
CYPHER_SCRIPT="/src/init.cypher"

# Cypher-shell command to execute the script
cypher-shell -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" -f "$CYPHER_SCRIPT"