import requests
import pickle

OLLAMA_API = "http://127.0.0.1:11434/api/chat"

# Conversation history is stored here
conversation = []

def chat_with_ollama(user_input, model="gemma:2b"):
    global conversation
    
    # Add user input to conversation history
    conversation.append({"role": "user", "content": user_input})
    
    # Send to Ollama API
    response = requests.post(OLLAMA_API, json={
        "model": model,
        "messages": conversation
    }, stream=False)
    
    reply_text = ""
    for line in response.iter_lines():
        if line:
            data = line.decode("utf-8")
            if '"content":"' in data:  # Extract incremental content
                chunk = data.split('"content":"')[-1].rstrip('"}')
                reply_text += chunk
    
    # Add assistant reply to history
    conversation.append({"role": "assistant", "content": reply_text})
    return reply_text



def retrieve_memory(fname):
    robj=open(fname,'rb')
    memlist = []
    while True:
        try:
            memlist.append(pickle.load(robj))
        except EOFError:
            break
        except:
            print("Encountered error while retrieving memory.")
            return -1
    
    robj.close()
    return memlist

def write_to_memory(fname,text):
    wobj = open(fname,"ab")
    try:
        pickle.dump(text,wobj)
    except:
        print("Encountered error while saving the following memory:\n" + text)
        return -1
    wobj.close()

def generate_mem_message(meml):
    message = "Below is a list of memories which you asked for to be saved during our previous interactions.\n"
    for mem in meml:
        message+=mem
        message+='\n'
    message+='-----\nTo add more memories use memadd: [memory]\n Using that is your decision\nNOTE: When using command, use only the command, no other text.\n'
    return message

chat_with_ollama(generate_mem_message(retrieve_memory('mem_zippy')))

while True:
    user_inp=input("Enter text: ")
    response = chat_with_ollama(user_inp)
    print(response)
    mem_check = response.split('memadd: ')
    if len(mem_check) == 2:
        write_to_memory('mem_zippy',mem_check[1])
    else:
        print(response)
    
