"""
This program will read the smoker temperatures and push the information to Rabbit MQ Server
Gabbs Albrecht
02/27/2023
"""

#imports listed at head of module
import pika
import sys
import time
from collections import deque

#Defining Variables at head of the module
host = "localhost"
caster_list = ["Bard", "Cleric", "Druid", "Paladin", "Ranger",  "Sorcerer", "Warlock", "Wizard"]
spell_deque = deque([],maxlen = 10)


#Callback function to handle the incoming messages
def callback(ch, method, properties, body):
    
    #Sends confirmation of message received
    message = body.decode()
    print(f" [x] Received {message}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

    #reads the spell level

    spell_level = int(message.split("::")[2])
   
    
    #this section looks at our deque and attempts to find the higet level of spell recorded within it
    #if the deque is empty prints out that we are adding the first spell
    try:
        spell_max = max(spell_deque)

    except Exception as e:
        spell_max = 10
        print("This is the first spell!")

    if (spell_level > spell_max):
         print("This is the most powerful spell in recent memory!")
    
    spell_deque.append(spell_level)






#Continuously listens for messages on a queue, smoker queue is the default.
def main(hn: str = "localhost", qn: str = "defaultqueue"):
    
    #Attempts to connect to the host
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=hn))

    #Throws this eror message if the connection cannot be established
    except Exception as e:
        print()
        print("ERROR: connection to RabbitMQ server failed.")
        print(f"Verify the server is running on host={hn}.")
        print(f"The error says: {e}")
        print()
        sys.exit(1)

    #Declares and connects to proper queue, defines our callback function for handling messages on it, and starts consuming messages
    try:
        channel = connection.channel()
        channel.queue_declare(queue=qn, durable = True)
        channel.basic_qos(prefetch_count=1) 
        channel.basic_consume( queue=qn, on_message_callback=callback)
        print(" [*] Ready for work. To exit press CTRL+C")
        channel.start_consuming()

    #Message thrown in case of error
    except Exception as e:
        print()
        print("ERROR: something went wrong.")
        print(f"The error says: {e}")
        sys.exit(1)

    #Allows user to interupt process
    except KeyboardInterrupt:
        print()
        print(" User interrupted continuous listening process.")
        sys.exit(0)

    #Closes the connection
    finally:
        print("\nClosing connection. Goodbye.\n")
        connection.close()

#Standard python idiom that let's us run our code as a script
if __name__ == "__main__":
    
    #Done this way allows for one python module to act as all 8 our producers
    print("Choose yor class form the following:\n 0 = bard, 1 = cleric, 2 = druid, 3 = paladin, 4 = ranger,  5 = sorcerer, 6 = warlock, 7 = wizard")
    caster_number = int(input())
    
    main(host, caster_list[caster_number])