import requests

def generate_sparql_query(entity1_id: str, entity2_id: str, relation_id: str) -> str:
    sparql_query = f"""
        SELECT ?entity1 ?entity1Label ?entity2 ?entity2Label ?relation ?relationLabel
        WHERE {{
            wd:{entity1_id} ?relation wd:{entity2_id} .
            wd:{relation_id} wikibase:directClaim ?relation .
            SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
            BIND(wd:{entity1_id} AS ?entity1)
            BIND(wd:{entity2_id} AS ?entity2)
        }}
    """
    return sparql_query

def run_sparql_query(sparql_query: str) -> dict:
    url = "https://query.wikidata.org/sparql"
    headers = {"Accept": "application/sparql-results+json"}
    response = requests.get(url, headers=headers, params={"query": sparql_query})

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Query failed with status code {response.status_code}")

# Example usage:
entity1_id = "d"  # Douglas Adams
entity2_id = "Q146"  # Cat
relation_id = "Q14623681"  # Has pet

sparql_query = generate_sparql_query(entity1_id, entity2_id, relation_id)
result = run_sparql_query(sparql_query)
print(result)