To start the Neo4j database
- run `./start_neo4j.sh`
- wait for it to accept connections
    To visit the Neo4j UI: `http://localhost:7474`

To populate the DB with the test data
- run `docker exec -it testneo4j /src/initialize_DB.sh`

To start the UI
- run `streamlit run gui/ui.py`