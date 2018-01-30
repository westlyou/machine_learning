# -*- coding: utf-8 -*-

import nltk
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()

import numpy as np
import tflearn
import tensorflow as tf
import random

import pickle
data = pickle.load(open( "training_data", "rb" ))
words = data['words']
classes = data['classes']
train_x = data['train_x']
train_y = data['train_y']

import json
with open('intents.json') as json_data:
    intents = json.load(json_data)
# print ">>> intents", intents

net = tflearn.input_data(shape=[None, len(train_x[0])])
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, len(train_y[0]), activation='softmax')
net = tflearn.regression(net, optimizer='adam', loss='categorical_crossentropy')

model = tflearn.DNN(net, tensorboard_dir='tflearn_logs')
print ">>> model", model


def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)

    sentence_words = [stemmer.stem(word.lower()) for word in sentence_words]
    return sentence_words


# bag of words
def bow(sentence, words, show_details=False):
    sentence_words = clean_up_sentence(sentence)

    # bag of words
    bag = [0]*len(words)  

    for s in sentence_words:
        for i,w in enumerate(words):
            # print "i,w", i, w
            if w == s: 
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)
    return(np.array(bag))

# print bow('I want to special food', words)

# load model
model.load('./model.tflearn')

# data structure to hold user context
context = {}

ERROR_THRESHOLD = 0.25
def classify(sentence):
    results = model.predict([bow(sentence, words)])[0]
    results = [[i,r] for i,r in enumerate(results) if r>ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append((classes[r[0]], r[1]))
    return return_list

def response(sentence, userID='1', show_details=False):
    results = classify(sentence)
    if results:
        while results:
            for i in intents['intents']:
                if i['tag'] == results[0][0]:
                    print "if i['tag'] == results[0][0]:"
                    if 'context_set' in i:
                        print "if 'context_set' in i:"
                        if show_details:
                            print ('context:', i['context_set'])
                            context[userID] = i['context_set']
                    if not 'context_filter' in i or \
                            (userID in context and 'context_filter' in i and i['context_filter'] == context[userID]):
                        print "if not 'context_filter' in i or "
                        if show_details:
                            print ('tag:', i['tag'])
                            print random.choice(i['responses'])
                            return (random.choice(i['responses']))
            results.pop(0)

print classify('is your shop open today?')

response('is your shop open today?', '1', True)
response('do you take cash?', '1', True)
response('Goodbye, see you later', '1', True)
response('I want to special food', '1', True)
response('Hi, have any waiter', '1', True)
response('thankyou, I want beefsteack and 2 glass of water', '1', True)