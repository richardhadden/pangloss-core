docker run --name neo4j-test \
    -p 7474:7474 -p 7687:7687 \
    -v $PWD/neo4j-docker/data:/data -v $PWD/neo4j-docker/plugins:/plugins \
    -e NEO4J_apoc_export_file_enabled=true \
    -e NEO4J_apoc_import_file_enabled=true \
    -e NEO4J_apoc_import_file_use__neo4j__config=true \
    -e NEO4J_PLUGINS=\[\"apoc\"\] \
    -e NEO4J_dbms_security_procedures_unrestricted=apoc.\\\* \
    neo4j:latest