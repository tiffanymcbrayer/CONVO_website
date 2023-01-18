import re
from flask import Flask
from flask import render_template
from flask import Response, request, jsonify
from flask import Flask, request, render_template, g, redirect, Response, url_for
import openai
import ipywidgets as widgets
import re 
from pprint import pprint

# need a valid api key from open ai to run on your own machine
openai.api_key = ""

app = Flask(__name__)

conversation = None


# ROUTES


@app.route('/')
def main():
    global conversation
    conversation = None
    return render_template('main.html')   

@app.route('/clear', methods=['GET', 'POST'])
def clear():
    global conversation
    language = request.form['language']
    topic = request.form['topic']
    l, prompt, results = discussingTopicPhrasesWithGPT(language, topic)
    conversation = results
    return render_template('practice.html', language = language, topic = topic, results = results)   

@app.route('/generate', methods=['GET', 'POST'])
def generate():
  
    language = request.form['language']
    topic = request.form['topic']
    options = request.form.get("gridRadios") 
    
    global conversation

    # generate
    if options=="option1":
        l, prompt, results = topicConversations(language, topic)
        # print(results)
        return render_template('generate.html', language = language, topic = topic,  results = results)

    # practice
    elif options=="option2":
        userInput = request.form.get("userInput") 
        if conversation == None: #and userInput == None:    
            l, prompt, results = discussingTopicPhrasesWithGPT(language, topic)
            conversation = results

        else:
            if userInput == "" or userInput == None:
                l, prompt, r, c = keepConvGoing(language, conversation)
                results = c
                conversation = results
            else:
                l, prompt, r, c  = keepConvGoingUserInput(language, conversation, userInput)
                results = c
                conversation = results

        return render_template('practice.html', language = language, topic = topic, results = results)   

      
      
# FUNCTIONS

def print_results_lists(user_input_label, user_input, prompt, results):
  print(user_input_label+ ": " +user_input)
  print("prompt: " +prompt)
  pprint(results)
  return

def topicConversations(language, topic):
  prompt = f"Create a simple conversation that two people would have in {language} about {topic}. Answer template: Portuguese phrase - English translation."
  completion = openai.Completion.create(engine = 'text-davinci-002', max_tokens = 256, prompt= prompt)
  #results = re.split('\n', completion.choices[0].text.strip())
  results = completion.choices[0].text.strip()
  return language, prompt, results

# start a conversation in {language} discussing this topic: {topic} 
def discussingTopicPhrasesWithGPT(language, topic): 
  prompt = f"A question in {language} someone would ask me while I am {topic}."
  completion = openai.Completion.create(engine = 'text-davinci-002', max_tokens = 256, prompt= prompt)
  results = re.split('\n', completion.choices[0].text.strip())
  if isEnglish(results[0]) == 1:
    results = translate(language, results)
  return language, prompt, results

 
# keep conversation going with user input
def keepConvGoingUserInput(language, conversation, userInput):
  conversation.append(userInput)
  convString = coversationToString(conversation)
  prompt = f"What could be a following response in {language} to this conversation:\n '{convString}'"
  completion = openai.Completion.create(engine = 'text-davinci-002', max_tokens = 256, prompt= prompt)
  results = re.split('\n', completion.choices[0].text.strip())
  newResults = []
  newResults.append(results[0])
  results = newResults
  if isEnglish(results[0]) == 1:
    results = translate(language, results)
  conversation1 = appendResultToConv(conversation, results)
  return language, prompt, results, conversation1

# keep conversation going no user input
def keepConvGoing(language, conversation):
  convString = coversationToString(conversation)
  prompt = f"What could be a following response in {language} to this conversation:\n '{convString}'"
  completion = openai.Completion.create(engine = 'text-davinci-002', max_tokens = 256, prompt= prompt)
  results = re.split('\n', completion.choices[0].text.strip())
  newResults = []
  newResults.append(results[0])
  results = newResults
  if isEnglish(results[0]) == 1:
    results = translate(language, results)

  conversation = appendResultToConv(conversation, results)
  return language, prompt, results, conversation

def coversationToString(conversation):
  c = 0
  convString = ""
  for i in conversation:
    if c % 2 == 0:
      convString += f"A: {i}\n" 
    else:
      convString += f"B: {i}\n" 
    c+=1
  return convString

def coversationToStringUserInput(conversation, userInput):
  c = 0
  convString = ""
  conversation.append(userInput)
  for i in conversation:
    if c % 2 == 0:
      convString += f"A: {i}\n" 
    else:
      convString += f"B: {i}\n" 
    c+=1
  return convString

def appendResultToConv(conversation, results):
  if ':' in results[0]:
    [i,j] = results[0].split(":")
    results = j[1:]
  conversation.append(results)
  return conversation


def isEnglish(phrase):
  prompt = f"What language is this: {phrase}?"
  completion = openai.Completion.create(engine = 'text-davinci-002', max_tokens = 256, prompt= prompt)
  results = re.split('\n', completion.choices[0].text.strip())
  if "English" in results[0] or "english" in results[0]:
    return 1
  return 0

def translate(language, phrase):
  prompt = f"Translate the following phrase to {language}: {phrase}"
  completion = openai.Completion.create(engine = 'text-davinci-002', max_tokens = 256, prompt= prompt)
  results = re.split('\n', completion.choices[0].text.strip())
  return results


if __name__ == '__main__':
   app.run(debug = True)
