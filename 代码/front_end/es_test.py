# connect to entity catalog indexed with Lucene 
from elasticsearch import Elasticsearch
from urllib.parse import quote
import string

class IndexSearch:
    
    def __init__(self, index_name):
        # set up ES connection
        self.es = Elasticsearch("http://localhost:9200/")
        self.index = index_name
        self.type = 'terms'

    def match_label(self, string, top=2):
        return self.es.search(index=self.index,
                              body={"query": {"multi_match": {"query": string,
#                                                               "operator": "and",
                                                              "fields": ["label.snowball"],  # ["label.label", "label.ngrams"],  # , "label.ngrams" ,"label.snowball^50",  "label.snowball^20", "label.shingles",
                                                              }}},
                              size=top)['hits']['hits']

    def label_scores(self, string, top=100, verbose=False, threshold=1.0, scale=None, max_degree=None):
        matches = self.es.search(index=self.index,
                              body={"query": {"multi_match": {"query": string,
#                                                               "operator": "and",
                                                              "fields": ["label.ngrams", "label.snowball^20"],  # ["label.label", "label.ngrams"],  # , "label.ngrams" ,"label.snowball^50",  "label.snowball^20", "label.shingles",
                                                              }}},
                              size=top, doc_type=self.type)['hits']
        span_ids = {}
        for match in matches['hits']:
            _id = match['_source']['id']
            degree = int(match['_source']['count'])
            if max_degree and degree <= max_degree:
              score = match['_score'] / matches['max_score']
              if not threshold or score >= threshold:
                  if scale:
                    score *= scale
                  span_ids[_id] = score
                  if verbose:
                    print({match['_source']['uri']: score})

        return span_ids

    def look_up_by_uri(self, uri, top=1):
        uri = uri.replace("'", "")
        results = self.es.search(index=self.index,
                              body={"query": {"term": {"uri": uri}}},
                              size=top, doc_type=self.type)['hits']['hits']
        if not results:
            results = self.es.search(index=self.index,
                              body={"query": {"term": {"uri": uri.replace("–", "-")}}},
                              size=top, doc_type=self.type)['hits']['hits']
            if not results:
                results = self.es.search(index=self.index,
                                          body={"query": {"term": {"uri": quote(uri, safe=string.punctuation)}}},
                                          size=top, doc_type=self.type)['hits']['hits']
            
        return results

    def look_up_by_id(self, _id, top=1):
        results = self.es.search(index=self.index,
                              body={"query": {"term": {"id": _id}}},
                              size=top, doc_type=self.type)['hits']['hits']
        return results

    def look_up_by_label(self, _id):
        results = self.es.search(index=self.index,
                                 body={"query": {"term": {"label": _id}}},
                                )['hits']['hits']
        return results
    

# if __name__=="main":
e_index=IndexSearch("dbpedia201604e")
print(e_index.match_label("Obama")[0])