

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
# print(e_index.match_label("Obama")[0])
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
translate_ner_bert_dict={"B-LOC":"地点",
                "B-ORG":"组织",
                "B-PER":"人物",
                "B-MISC":"其他",
                "I-LOC":"地点",
                "I-ORG":"组织",
                "I-PER":"人物",
                "I-MISC":"其他"}


def NER_Bert(question:str):
    tokenizer = AutoTokenizer.from_pretrained("dslim/bert-base-NER")
    model = AutoModelForTokenClassification.from_pretrained("dslim/bert-base-NER")
    nlp = pipeline("ner", model=model, tokenizer=tokenizer)
    # location (LOC), organizations (ORG), person (PER) and Miscellaneous (MISC)
    # question="Who is the son of Barack Obama?"
    ner_results = nlp(question)
    print("NER_Bert result",ner_results)
    count=0
    result=[]
    while(True):
        if count>=len(ner_results):
            break
        i=ner_results[count]
        type1=translate_ner_bert_dict[i["entity"]] 
        new_word=i["word"]
        count+=1
        while(count<len(ner_results) and ner_results[count]["entity"][0]=='I'):
            new_word+=" "+ner_results[count]["word"]
            count+=1
        uri=e_index.match_label(new_word,top=1)[0]["_source"]["uri"]            
        result.append({"entity":type1,"word":new_word,"uri":uri})
        
        
    return result
# #entity score word start end


if __name__ == "__main__":
    question="Who is the wife of Barack Obama?"
    results=NER_Bert(question)
    print(results)

# print(ner_results)

# from datasets import load_dataset
# dataset = load_dataset("conll2012_ontonotesv5","english_v4")
# print("")
# # 

# from transformers import AutoTokenizer, AutoModelForTokenClassification
# from transformers import pipeline

# tokenizer = AutoTokenizer.from_pretrained("dslim/bert-base-NER")
# model = AutoModelForTokenClassification.from_pretrained("dslim/bert-base-NER")

# nlp = pipeline("ner", model=model, tokenizer=tokenizer)
# example = "My name is Wolfgang and I live in Berlin"

# ner_results = nlp(example)
# print(ner_results)