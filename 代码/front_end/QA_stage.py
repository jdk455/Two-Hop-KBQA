import tkinter as tk
import openai


# Replace FINE_TUNED_MODEL with the name of your fine-tuned model

#超参设置
model_name = "davinci:ft-personal-2023-04-15-07-38-00"
openai.api_key="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"
neo4j_URI = "neo4j://localhost"
neo4j_AUTH = ("neo4j", "neo4jkyrie")



def QA_Stage(question_body):
    question_head="用cypher代码查询如上问题该使用什么代码（请不要输出多余的话),其中节点类型有[Disease,Pesticide,Check,Classification,Expert,Symtom]，关系有[recommand_expert,recommand_pesticide,has_subsidies,disease_classification,has_symptom,need_check],节点Disease的属性表为：[get_way, get_prob, cost_money, acompany, cause, desc, name, cured_prob, prevent, cure_way, cure_lasttime]。问题："
    question=question_head+question_body
    # Make the completion request
    print("QA_Stage_ques",question)
    completion = openai.Completion.create(model=model_name, prompt=question,max_tokens=100,stop=[ "###"])
    # Get the completion text from the first choice in the choices list
    text = completion.choices[0]["text"]
    print("QA_Stage",text)
    return text
    

    
    


    
    



