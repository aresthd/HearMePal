import random
import json
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder
from nltk_utils import bag_of_words, tokenize
# from tensorflow.keras.models import load_model
from keras.models import load_model
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
import pickle

PATH_INTENTS = '../../data/intents.json'
PATH_MODEL = 'tf_model.pkl'
PATH_METADATA = 'tf_metadata_tf-idf.json'
PATH_VECTORIZER = 'tf_vectorizer.pkl'

# Load model and metadata (model .h5)
# model = load_model(PATH_MODEL)
# with open(PATH_METADATA, 'r') as f:
#     metadata = json.load(f)

# Load the model & metadata (.pkl)
with open(PATH_MODEL, 'rb') as f:
    model = pickle.load(f)
    
with open(PATH_METADATA, 'r') as f:
    metadata = json.load(f)

input_size = metadata['input_size']
all_words = metadata['all_words']
tags = metadata['tags']
label_encoder_classes = metadata['label_encoder_classes']
vectorizer_vocabulary = metadata['vectorizer_vocabulary']

# Initialize LabelEncoder
label_encoder = LabelEncoder()
label_encoder.classes_ = np.array(label_encoder_classes)

# Recreate the TfidfVectorizer and set its vocabulary
# vectorizer = TfidfVectorizer(tokenizer=tokenize, vocabulary=vectorizer_vocabulary)
# vectorizer = TfidfVectorizer(tokenizer=tokenize,
#                              min_df = 5,
#                              max_df = 0.8,
#                              sublinear_tf = True,
#                              use_idf = True,
#                              vocabulary=vectorizer_vocabulary)
# Load the TF-IDF vectorizer
vectorizer = joblib.load(PATH_VECTORIZER)

# Open file json
with open(PATH_INTENTS, 'r') as f:
    intents = json.load(f)

# Chatbot loop
bot_name = '(X) Tensor-TFIDF'
print("Let's chat! Type 'quit' to exit")

while True:
    sentence = input('You: ')
    if sentence == 'quit':
        break
    
    
    # Different -----------------
    
    # sentence = tokenize(sentence)
    # x = bag_of_words(sentence, all_words)
    # x = np.expand_dims(x, axis=0)
    
    x = vectorizer.transform([sentence]).toarray()
    
    
    output = model.predict(x)
    predicted = np.argmax(output, axis=1)
    tag = label_encoder.inverse_transform(predicted)[0]
    
    probs = tf.nn.softmax(output[0])
    prob = probs[predicted[0]]
    
    
    threshold = 0.25
    print(f'prob : {prob}')
    if prob > threshold:
        for intent in intents['intents']:
            if tag == intent['tag']:
                response = random.choice(intent['responses'])
                print(f"{bot_name}: {response}\n")
    else:
        print(f"{bot_name}: I do not understand...\n")
