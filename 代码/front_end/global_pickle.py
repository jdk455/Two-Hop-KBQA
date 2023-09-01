import pickle
import os
schema_dir=r"D:\Code\KBQA_LEARN\front_end\schema"
def init_global():
    ner_schema=dict()
    ner_schema["conll2003-en"]=["Person(人物)","Location(地点)","Organization(组织)","Miscellaneous(其他)"]
    re_schema=dict()
    re_schema["农业"]=["recommand_expert",
            "recommand_pesticide",
            "has_subsidies",
            "disease_classification",
            "has_symptom",
            "need_check"]
    pickle.dump(ner_schema,open(schema_dir+"/ner_schema.pkl","wb"))
    pickle.dump(re_schema,open(schema_dir+"/re_schema.pkl","wb"))

def save_global_NER_schema(schema):
    pickle.dump(schema,open(schema_dir+"/ner_schema.pkl","wb"))
        
    
def save_global_RE_schema(relation):
    pickle.dump(relation,open(schema_dir+"/re_schema.pkl","wb"))

def fetch_global_NER_schema():
    return pickle.load(open(schema_dir+"/ner_schema.pkl","rb"))

def fetch_global_RE_schema():
    return pickle.load(open(schema_dir+"/re_schema.pkl","rb"))

if __name__=="__main__":
    init_global()


