"""
This program will read the smoker temperatures and push the information to Rabbit MQ Server
Gabbs Albrecht
02/27/2023
"""


#imports at top of module
import requests as rq
import ast
import pika
import json
import time


#defing variables
host = 'localhost'
caster_list = ["Bard", "Cleric", "Druid", "Paladin", "Ranger",  "Sorcerer", "Warlock", "Wizard"]
base_URL = "https://www.dnd5eapi.co"
list_URL ="/api/spells"

#Getting the index of spells from the API
requestInfo =  rq.get(base_URL + list_URL)
#format returned by the api is funky so this transforms it into just a list of dictionaries so we can pull the whole spell block instead
spell_Dict = ast.literal_eval(requestInfo.text)
spell_List = spell_Dict['results']




#A quick function to clear out the queues of any previous messges
def clear_queues(host: str, queue_list: list):
  
    conn = pika.BlockingConnection(pika.ConnectionParameters(host))
    ch = conn.channel()
    for x in queue_list:
        ch.queue_delete(queue=x)

#This is the function that defines the behavior to send messages
def send_message(host: str, queue_name: str, message: str):
    
    #Attempts to connect to the host and push the message to the defined queue
    try: 
        conn = pika.BlockingConnection(pika.ConnectionParameters(host))
        ch = conn.channel()
        ch.queue_declare(queue=queue_name, durable = True)
        ch.basic_publish(exchange ="", routing_key = queue_name, body = message)
        print(f"[x] Sent {message}")
    
    #If the attempt fails, sends us this error message
    except pika.exceptions.AMQPConnectionError as e:
        print(f"Error: Connection to RabbitMQ server failed: {e}")
    
        #Closes our connection to the host
    finally:
        conn.close()



#main function to be called by module, clears our queues then 
def main():

    #clears the queues for each caster
    clear_queues(host, caster_list)

    #Cycles through the pulled list of spells and extracts the needed info from the api for each one
    for x in spell_List:
        #this block takes the spell from the list of spell and gives us the actual information on how it functions
        spell_index = spell_List.index(x)
        spell_acting = spell_List[spell_index]
        spell_dict_Index = spell_acting['url']
        spell_Info =  rq.get(base_URL + spell_dict_Index).text
       
        #Restructures the info into our message
        resultdict = json.loads(spell_Info)
        result_stripped = {"Name" : resultdict['name'], "Description" : str(resultdict['desc']),"Level" :  str(resultdict['level'])}
        spell_message = '::'.join(result_stripped[key] for key in result_stripped )

        #sends the message to a queue for every class able to cast the spell
        for x in resultdict['classes']:
           caster_queue = x['name']
           send_message(host, caster_queue, spell_message)

        time.sleep(5)
           

#Standard python idiom that let's us run our code as a script
if __name__ == "__main__":
    
    main()