import openai
import ast, copy, random
from openai import OpenAI
import common.utils 
from common.enums import ChatbotType
from common.config import Config
import time

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="..." 
)

def escapeString(s):
    s = s.replace('1', '\"1\"')
    s = s.replace(' 1', ' \"1\"')    
    s = s.replace('[1', '[\"1\"')
    s = s.replace('2', '\"2\"')
    s = s.replace('[2', '[\"2\"')
    s = s.replace(' 2', ' \"2\"')    
    s = s.replace('3', '\"3\"')
    s = s.replace('[3', '[\"3\"')
    s = s.replace(' 3', ' \"3\"')
    s = s.replace('4', '\"4\"')    
    s = s.replace(' 4', ' \"4\"')    
    s = s.replace('[4', '[\"4\"')
    s = s.replace('5', '\"5\"')    
    s = s.replace(' 5', ' \"5\"')    
    s = s.replace('[5', '[\"5\"')
    s = s.replace('6', '\"6\"')    
    s = s.replace(' 6', ' \"6\"')    
    s = s.replace('[6', '[\"6\"')
    s = s.replace('7', '\"7\"')    
    s = s.replace(' 7', ' \"7\"')    
    s = s.replace('[7', '[\"7\"')
    s = s.replace('8', '\"8\"')
    s = s.replace(' 8', ' \"8\"')    
    s = s.replace('[8', '[\"')
    s = s.replace('9', '\"9\"')    
    s = s.replace(' 9', ' \"9\"')
    s = s.replace('[9', '[\"9\"')
    s = s.replace('*', '\"*\"')
    s = s.replace(' *', '\"*\"')    
    s = s.replace('[*', '[\"*\"')                        
    return s

def firstTimeReply(msgs):
    s = msgs[0]['content']
    i = s.find("please solve this 4x4 sudoku puzzle")
    if i < 0:
        return ""
    start = s.find("[[",i)
    end = s.find("]]",start)
    return '{"rows": '+ escapeString(s[start:end+2]) + '}'


def call_loop(llm_model,msgs,temp=1.0):
    response = ''
    while not(response):
        try:
            response = client.chat.completions.create(model = llm_model, messages=msgs,temperature=temp,max_tokens=800).choices[0].message.content
        except:
            response = ''
            random_seconds = random.randint(5,25)            
            print("LLM call exception occurred, will sleep for " + str(random_seconds) + " seconds.", flush=True)
            time.sleep(random_seconds)
    return response

def llm4(msgs,msg='',temp=1.0) -> str:
    first_time_reply = ""
    llm = 'openai/gpt-3.5-turbo'
    # For other choices: 
    #llm = 'openai/gpt-4'
    
    #print("About to call this LLM: " + llm,flush=True)
    if msg:
        msgs = [{"role": "user", "content": msg}]
        return call_loop(llm,msgs,temp=temp)
    else:
        first_time_reply = firstTimeReply(msgs)
    if first_time_reply:
        print("First time, will return this reply: " + first_time_reply)
        return firstTimeReply(msgs)
    return call_loop(llm,msgs,temp=temp)
        
class LLMAgent(object):

    def __init__(self, config) -> None:
        self.config = config
        self.chatbot = self._initialize_chatbot(config.chatbot_type)
    
    def compose_messages(self, roles, msg_content_list) -> object:
        if not (len(roles) == len(msg_content_list)):
            raise "Failed to compose messages"
        msgs = [{"role" : roles[i], "content" : msg_content_list[i]} for i in range(len(roles))]
        return msgs
    
    def get_reply(self, messages, temperature = None, max_tokens = None) -> str:
        return self.chatbot.get_reply(messages, temperature, max_tokens)

    def _initialize_chatbot(self, chatbot_type):
        if chatbot_type == ChatbotType.OpenAI:
            return OpenAIChatbot(self.config.openai_model, self.config.openai_api_key)
        else:
            raise "Not supported for now!"

class ChatbotBase(object):

    def __init__(self) -> None:
        pass

    def get_reply(self, messages, temperature = None, max_tokens = None) -> str:
        return ""
    
class OpenAIChatbot(ChatbotBase):

    def __init__(self, openai_model, openai_api_key) -> None:
        super().__init__()
        self.model = openai_model
        openai.api_key = openai_api_key

    def get_reply(self, messages, temperature = None, max_tokens = None) -> str:
        print("LLM Query:", messages)
        try:
            reply = llm4(messages)
            print("LLM Reply: [[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[\n", reply,flush=True)
            print("\n]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]\n\n",flush=True)
            return reply
        except:
            reply = "Failed to get LLM reply"
            print(reply,flush=True)
            return reply
