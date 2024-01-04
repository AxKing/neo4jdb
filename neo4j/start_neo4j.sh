docker run \
    --name testneo4j \
    -p7474:7474 -p7687:7687 \
    -d \
    -v $HOME/neo4j/data:/data \
    -v $HOME/neo4j/logs:/logs \
    -v $PWD/import:/var/lib/neo4j/import \
    -v $HOME/neo4j/plugins:/plugins \
    -v $PWD:/src \
    --env NEO4J_AUTH=neo4j/password \
    --rm \
    neo4j:latest