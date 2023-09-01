import tkinter as tk
import openai
from neo4j import GraphDatabase
import json

# Replace FINE_TUNED_MODEL with the name of your fine-tuned model

#超参设置
model_name = "davinci:ft-personal-2023-04-15-07-38-00"
openai.api_key="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"
neo4j_URI = "neo4j://localhost"
neo4j_AUTH = ("neo4j", "neo4jkyrie")
relation_translate={"Expert":"recommand_expert",
                    "Pesticide":"recommand_pesticide",
                    "Gov_subsidies":"has_subsidies",
                    "Classification":"disease_classification",
                    "Symptom":"has_symptom",
                    "Check":"need_check"}
#全局变量
# event_type=set()
# schema=dict()

#读取schema
def read_schema():
    event_type=[]
    event_set=set()
    schema=dict()
    with open(r"built_graph\dataset\EE\DuEE_1_0\event_schema.json", "r", encoding="utf-8") as f:
        for i in f.readlines():
            t=json.loads(i)
            if t["event_type"] in event_set:
                continue
            event_type.append(t["event_type"])
            event_set.add(t["event_type"])
            schema[t["event_type"]]=[i["role"] for i in t["role_list"]]
    return event_type,schema



def NER_Stage1(question_body,schema):
    # global question_body,entity_extraction,property_extraction
    print(question_body)
    print("--------------------stage1")
    event_type=[]
    for i in schema:
        event_type.append(i)
        
    print("event_type",event_type)
    stage1_question_head='请在下面一段话提取出现的实体类型，并以列表形式返回。其中实体类型有['+",".join(event_type)+']，你只能从上述列表中提取若干个返回，例如返回['+event_type[0]+']，如果没有实体类型，请返回[]。\n'
    stage1_question=stage1_question_head+question_body
    print("stage_1_ques",stage1_question)
    response=openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role":"user","content":stage1_question}],
    temperature=0.1
    )
    res=response["choices"][0]["message"]["content"]
    print("NER_stage1_response",res)
    
    res=res[res.find("["):res.find("]")+1]
    res=res[1:len(res)-1].split(",")
    print("processed_NER_stage1_response",res)
    return res
    # print(res)
    # entity_extraction=json.loads(res)
    # print(entity_extraction)
    # return res,entity_extraction["Disease"]
    
    
#测试Stage1
# print(Stage1("今日，，张晋发布视频，通告蔡少芬喜怀三胎！",event_type,schema))

def NER_Stage2(ques,avai_event,schema):
    print("--------------------stage2")
    res_dict=dict()
    for i in avai_event:
        i=i.strip()
        res_dict[i]=(NER_Stage2_onestep(ques,i,schema))
    return res_dict

def NER_Stage2_onestep(question_body,one_event,schema):
    # global question_body,entity_extraction,property_extraction
    stage2_question_head='请在下面一段话提取出"'+one_event+'"的论元及对应名称，并以json格式返回。其中论元列表有['+",".join(schema[one_event])+']，当论元不存在在句子时，对应填"无"，例如当论元列表为[时间，地点，人物]时，一种可能的返回为{"时间":"2017年",地点:"台湾",人物:"无"}。问题："'
    stage2_question=stage2_question_head+question_body+'"'
    
    response=openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role":"user","content":stage2_question}],
    temperature=0.1
    )
    res=response["choices"][0]["message"]["content"].replace(",\n}","\n}")
    print("Stage2回答：",one_event,"所获得的论元为：",res)
    res_json=json.loads(res)
    return res_json

#测试Stage2
# ques="今日，，张晋发布视频，通告蔡少芬喜怀三胎！"
# avai_event=Stage1(ques,event_type,schema)
# Stage2(ques,avai_event,schema)

def cypher_exec(tx,query):
    result = tx.run(query)
    records = list(result)  # a list of Record objects
    summary = result.consume()
    # Summary information
    print("The query `{query}` returned {records_count} records in {time} ms.".format(
        query=summary.query, records_count=len(records),
        time=summary.result_available_after
    ))
    res=json.dumps(records,ensure_ascii=False)

#  # Loop through results and do something with them
    for i in records:
        print(i.data())  # obtain record as dict
    return res

def NER_build_graph(entity_extraction):
    match_cypher="MATCH "
    return_cypher="\nRETURN "
    # URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"
    URI = "neo4j://localhost"
    AUTH = ("neo4j", "neo4jkyrie")
    with GraphDatabase.driver(URI, auth=AUTH) as driver: 
            driver.verify_connectivity() 
    print("--------------------build_graph-----------------------")
    with driver.session() as session:
        for one_extraction in entity_extraction:
            one_extraction_dict=json.loads(one_extraction)
            #build entity node
            for i,j in one_extraction_dict.items():
                if j!="无" and j!="不明确" and j!="不明" and j!="none":
                        match_cypher=match_cypher+"("+i+":"+i+"{name:'"+j+"'}"+"),"
                        return_cypher=return_cypher+i+","
                        cypher_exec(driver.session(database="neo4j"),"merge (n:"+i+"{name:'"+j+"'})")
    all_cypher=match_cypher[:len(match_cypher)-1]+return_cypher[:len(return_cypher)-1]
    return all_cypher
                
    # #build relation
    # for i,j in entity_extraction.items():
    #     if j!="无" and j!="不明确" and j!="不明" and j!="none"and i!="Disease":
    #         with driver.session() as session:
    #             cypher_exec(driver.session(database="neo4j"),"match (n:Disease{name:'"+entity_extraction["Disease"]+"'}),(m:"+i+"{name:'"+j+"'}) merge (n)-[:"+relation_translate[i]+"]->(m)")
        
    # #build property           
    # for i,j in property_extraction.items():
    #     if j!="无" and j!="不明确" and j!="不明" and j!="none":
    #         with driver.session() as session:
    #             cypher_exec(driver.session(database="neo4j"),"match (n:Disease{name:'"+entity_extraction["Disease"]+"'}) set n."+i+"='"+j+"'")
            
    return "success"



##########测试模型#############
def loadData():
    with open(r"built_graph\dataset\EE\DuEE_1_0\train.json",encoding="utf-8") as f:
        all_event=[]
        for i in f.readlines():
            t=json.loads(i)
            one_entity_events=[t["text"]]
            event_set=set()
            event_name=[]
            event_args=[]
            for i in t["event_list"]:
                if i["event_type"] in event_set:
                    continue
                event_set.add(i["event_type"])
                event_name.append(i["event_type"])
                one_event_args=dict()
                for j in i["arguments"]:
                    one_event_args[j["role"]]=j["argument"]
                event_args.append(one_event_args)
            one_entity_events.append(event_name)
            one_entity_events.append(event_args)
            all_event.append(one_entity_events)       
    return all_event
                
                
                 
             


def test(now_event):
    # event_type,schema=read_schema()
    event_type=["农业"]
    schema=dict()
    schema["农业"]=["Disease","Pesticide","Check","Classification","Expert","Symptom","Gov_subsidies"]
    success=0
    gpt不听话=0
    try:
        avai_events=NER_Stage1(now_event,event_type,schema)
        print("Stage1回答：",avai_events)
        avai_args=NER_Stage2(now_event,avai_events,schema)
    except:
        gpt不听话+=1
        print("gpt不听话")
        avai_args="fuck"
    return avai_args
        
    
        
# a=test('''黄瓜炭疽病是由葫芦科刺盘孢等引起的，发生在黄瓜上的一种病害。黄瓜炭疽病苗期到成株期均可发病，幼苗发病，多在子叶边缘出现半椭圆形淡褐色病斑，上生橙黄色点状胶质物，重者幼苗近地面茎基部变黄褐色，逐渐细缩，致幼苗折倒。 [1]  [3] 
# 黄瓜炭疽病在中国以内都有发生，但以中国南方比较普遍，有发展的趋势。除露地黄瓜上发病外，中国北方保护地黄瓜发病严重，损失10％-20％以上。 [5]  [7] 
# 黄瓜炭疽病的防治方法主要有农业防治和化学防治两大类。''')
# print("")

    
    



