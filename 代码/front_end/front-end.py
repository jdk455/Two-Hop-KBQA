from flask import *
from flask_bootstrap import Bootstrap
from NER_Stage12 import *
from RE_Stage12 import *
from global_pickle import *
from QA_stage import *
from NER_BERT  import *
from BERTRelationExtraction.main_task import infer_one_sentence

app = Flask(__name__, template_folder="template",static_folder='static', static_url_path='')




@app.route('/', methods=['GET', 'POST'])
def welcome():
    return render_template("welcome.html",name = "nb")


#-------------------------schema-------------------------
@app.route('/schema_show', methods=['GET', 'POST'])
def schema_show():
    schema=fetch_global_NER_schema()
    relation=fetch_global_RE_schema()
    return render_template("schema_show.html",ner_list=schema,re_list=relation)

@app.route('/NER_delete_type', methods=['GET', 'POST'])
def NER_delete_one_type():
    type=request.args.get("type")
    ner_list=fetch_global_NER_schema()
    del ner_list[type]
    save_global_NER_schema(ner_list)
    return type

@app.route('/NER_add_type', methods=['GET', 'POST'])
def NER_add_one_type():
    type=request.args.get("type")
    entity=request.args.get("entity")
    ner_list=fetch_global_NER_schema()
    if ner_list.get(type)==None:
        ner_list[type]=[entity]
    save_global_NER_schema(ner_list)
    
    return type+" "+entity

@app.route('/NER_delete_entity', methods=['GET', 'POST'])
def NER_delete_one_entity():
    key=request.args.get("key")
    value=request.args.get("value")
    ner_list=fetch_global_NER_schema()
    del ner_list[key][ner_list[key].index(value)]
    save_global_NER_schema(ner_list)
    return key+"  "+value

@app.route('/NER_add_entity', methods=['GET', 'POST'])
def NER_add_one_entity():
    key=request.args.get("key")
    value=request.args.get("value")
    ner_list=fetch_global_NER_schema()
    ner_list[key].append(value)
    save_global_NER_schema(ner_list)
    return key+"  "+value



@app.route('/RE_delete_type', methods=['GET', 'POST'])
def RE_delete_one_type():
    type=request.args.get("type")
    re_list=fetch_global_RE_schema()
    del re_list[type]
    save_global_RE_schema(re_list)
    return type

@app.route('/RE_add_type', methods=['GET', 'POST'])
def RE_add_one_type():
    type=request.args.get("type")
    entity=request.args.get("entity")
    re_list=fetch_global_RE_schema()
    if re_list.get(type)==None:
        re_list[type]=[entity]
    save_global_RE_schema(re_list)
    
    return type+" "+entity

@app.route('/RE_delete_entity', methods=['GET', 'POST'])
def RE_delete_one_entity():
    key=request.args.get("key")
    value=request.args.get("value")
    print('RE_delete_entity',key,value)
    re_list=fetch_global_RE_schema()
    del re_list[key][re_list[key].index(value)]
    save_global_RE_schema(re_list)
    return key+"  "+value

@app.route('/RE_add_entity', methods=['GET', 'POST'])
def RE_add_one_entity():
    key=request.args.get("key")
    value=request.args.get("value")
    re_list=fetch_global_RE_schema()
    re_list[key].append(value)
    save_global_RE_schema(re_list)
    return key+"  "+value

#-------------------------NER-------------------------

@app.route('/NER_show', methods=['GET', 'POST'])
def NER_show():
    schema=fetch_global_NER_schema()
    schema_key=[]
    for key in schema:
        schema_key.append(key)
    return render_template("NER_show.html",name = "nb",ner_list_key=schema_key,ner_list=schema)

@app.route('/NER_BertBased', methods=['GET', 'POST'])
def NER_BertBased():
    raw_text = request.args.get("rawtext")
    res=NER_Bert(raw_text)
    return res

@app.route('/NER_stage1', methods=['GET', 'POST'])
def NER_stage1():
    schema=fetch_global_NER_schema()
    raw_text = request.args.get("rawtext")
    res_list=NER_Stage1(raw_text,schema)
    print("NER_stage1_args","&&&".join(res_list))
    return [res_list,"&&&".join(res_list)]
    

@app.route('/NER_stage2', methods=['GET', 'POST'])
def NER_stage2():
    schema=fetch_global_NER_schema()
    raw_text = request.args.get("rawtext")
    event_list = request.args.get("event_list").split("&&&")
    print("NER_stage2_args",raw_text,event_list,schema)
    res_dict=NER_Stage2(raw_text,event_list,schema)
    print("NER_stage2_result",res_dict)
    res_str=""
    for i,j in res_dict.items():
        res_str+="schema:"+i+"\n"
        for q,t in j.items():
            t=t.replace("无","none")
            res_str+="----"+q+" : "+t+"\n"
    json_str_list=""
    for i in res_dict:
        json_str_list+=json.dumps(res_dict[i])+"&&&"
    print("json_str_list",json_str_list)
    return [res_str,res_dict["农业"]["Disease"],json_str_list]

@app.route('/NER_build_graph', methods=['GET', 'POST'])
def NER_build():
    entity_extract= str(request.args.get("entity_extraction")).split("&&&")
    entity_extract=entity_extract[:len(entity_extract)-1]
    res=NER_build_graph(entity_extract)
    return res

#-------------------------RE-------------------------
@app.route('/RE_show', methods=['GET', 'POST'])
def RE_show():
    schema=fetch_global_RE_schema()
    schema_key=[]
    for key in schema:
        schema_key.append(key)
    return render_template("RE_show.html",name = "nb",re_list_key=schema_key,re_list=schema)

@app.route('/RE_stage1', methods=['GET', 'POST'])
def RE_stage1():
    schema=fetch_global_RE_schema()
    raw_text = request.args.get("rawtext")
    res_list=RE_Stage1(raw_text,schema)
    print("RE_stage1_args","&&&".join(res_list))
    return [res_list,"&&&".join(res_list)]
    

@app.route('/RE_stage2', methods=['GET', 'POST'])
def RE_stage2():
    schema=fetch_global_RE_schema()
    raw_text = request.args.get("rawtext")
    event_list = request.args.get("event_list").split("&&&")
    print("RE_stage2_args",raw_text,event_list,schema)
    res_dict=RE_Stage2(raw_text,event_list,schema)
    print("RE_stage2_result",res_dict)
    res_str=""
    for i,j in res_dict.items():
        res_str+="schema:"+i+"\n"
        for q,t in j.items():
            if type(t)==list and len(t)==2:
                res_str+="----"+q+" : ("+",".join(t)+")\n"
    json_str_list=""
    for i in res_dict:
        json_str_list+=json.dumps(res_dict[i])+"&&&"
    print("json_str_list",json_str_list)
    return [res_str,"1",json_str_list]

@app.route('/RE_build_graph', methods=['GET', 'POST'])
def RE_build():
    entity_extract= str(request.args.get("entity_extraction")).split("&&&")
    entity_extract=entity_extract[:len(entity_extract)-1]
    res=RE_build_graph(entity_extract)
    return res

@app.route('/RE_BertBased', methods=['GET', 'POST'])
def RE_infer_sentence():
    return infer_one_sentence(request.args.get("rawtext"))


#-------------------------QA-------------------------
@app.route('/QA_show', methods=['GET', 'POST'])
def QA_show():
    return render_template("QA_show.html",name = "nb")

@app.route('/QA_cypher', methods=['GET', 'POST'])
def QA_cypher():
    # return "MATCH (n:Disease)-[:has_symptom]->(m:Symtom) WHERE n.name = '玉米大斑病' RETURN m"
    cypher_text=request.args.get("rawtext")
    print("QA_cypher_args",cypher_text)
    return QA_Stage(cypher_text)

# @app.route('/QA_stage1', methods=['GET', 'POST'])



bootstrap = Bootstrap(app)
app.run("0.0.0.0", port=5000, debug=True)



