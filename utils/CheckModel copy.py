import json
import joblib
import torch
import pickle
import random
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder
# from utils.nltk_utils import bag_of_words, tokenize
from .nltk_utils import bag_of_words, tokenize

# if self.type == "NN_Pytorch":
#     pass
# elif self.type == "NN_Tensorflow":
#     pass
# elif self.type == "NN_Tensorflow_Tf-idf":
#     pass
# else:
#     pass

class CheckModel():
    def __init__(self, type, path_model, path_metadata, path_data='data/intents_3.json', path_vectorizer=None):
        self.type = type
        self.path_vectorizer = path_vectorizer
        # Checking cuda
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        self.load_intents(path_data)
        self.load_model(path_model)
        self.load_metadata(path_metadata)
        
    def check_nltk_utils(self):
        # Periksa impor nltk_utils
        try:
            from utils.nltk_utils import bag_of_words, tokenize
            print(f"\n Module ada------- \n")
        except ModuleNotFoundError as e:
            print(f"ModuleNotFoundError: {e}")
            print("Ensure 'nltk_utils.py' is located in the 'utils' directory or adjust PYTHONPATH.")
            raise
    
    def load_intents(self, path_data):
        with open(path_data, 'r') as f:
            self.intents = json.load(f)

    def load_model(self, path_model):
        print("\n Start load model-----")
        print(f"type : {self.type}-----")
        if self.type == "NN_Pytorch":
            self.model = torch.load(path_model)
            print(f"\n Load model {self.type} done-----")
        elif self.type == "NN_Tensorflow" or self.type == "NN_Tensorflow_Tf-idf":
            with open(path_model, 'rb') as f:
                self.model = pickle.load(f)
            print(f"\n Load model {self.type} done-----")
        else:
            self.model = None
            print("\n Load model {self.type} FAILED-----")
    
    def load_vectorizer(self, path_vectorizer):
        try:
            print(f"\n Starting load the vectorizer......")
            self.vectorizer = joblib.load(path_vectorizer)
            # with open(path_vectorizer, 'rb') as f:
            #     self.vectorizer = pickle.load(f)
            print("\n Load vectorizer done-----")
        except Exception as e:
            self.vectorizer = None
            print("\n Error | Failed load the vectorizer -----")
            print(f"An error occurred: {e} \n")
    
    def load_metadata(self, path_metadata):
        print(f"\n Starting load the metadata......")

        with open(path_metadata, 'r') as f:
            metadata = json.load(f)

        # self.input_size = metadata.get('input_size', None)
        # self.hidden_size = metadata.get('hidden_size', None)
        # self.output_size = metadata.get('output_size', None)
        
        self.all_words = metadata.get('all_words', None)
        self.tags = metadata.get('tags', None)
        
        self.label_encoder_classes = metadata.get('label_encoder_classes', None)
        self.vectorizer_vocabulary = metadata.get('vectorizer_vocabulary', None)
        
        
        # Need to there
        if self.all_words == None or self.tags == None:
            print("\n Error: | Load metadata failed------")
            print(f"self.all_words : {self.all_words}")
            print(f"self.tags : {self.tags}")
        
        if self.type == "NN_Tensorflow":
            if self.label_encoder_classes == None:
                print("\n Error: | Load metadata failed------")
                print(f"self.type : {self.type}")
                print(f"self.label_encoder_classes : {self.label_encoder_classes}")
            else:
                self.initialize_labelEncoder()
    
        elif self.type == "NN_Tensorflow_Tf-idf":
            if self.label_encoder_classes == None or self.vectorizer_vocabulary == None:
                print("\n Error: | Load metadata failed------")
                print(f"self.type : {self.type}")
                print(f"self.label_encoder_classes : {self.label_encoder_classes}")
                print(f"self.vectorizer_vocabulary : {self.vectorizer_vocabulary}")
            
            if self.label_encoder_classes != None:
                self.initialize_labelEncoder()
            
            if self.path_vectorizer != None:
                print(f"\n self.path_vectorizer : {self.path_vectorizer} \n")
                self.load_vectorizer(self.path_vectorizer)
            else: 
                print(f"\n Error | Load vectorizer Failed")
                print(f"\n path_vectorizer : {self.path_vectorizer} \n")
            
        print("\n Load metadata done-----")

    def initialize_labelEncoder(self):
        # Initialize LabelEncoder
        print(f"\n Starting Initialize LabelEncoder......\n")
        self.label_encoder = LabelEncoder()
        self.label_encoder.classes_ = np.array(self.label_encoder_classes)
        print(f"\n Done Initialize LabelEncoder......\n")


    def test_model(self):
        print("\n Start test model-----")
        sentence = "Hi"
        print(f"\n type : {self.type}-----")
        if self.type == "NN_Pytorch":
            try:
                x = bag_of_words(sentence, self.all_words)
                x = x.reshape(1, x.shape[0])    # 1 -> row; x.shape[0] -> column
                x = torch.from_numpy(x)
                
                output = self.model(x)
                _, predicted = torch.max(output, dim=1)
                self.tag = self.tags[predicted.item()]
                
                probs = torch.softmax(output, dim=1)
                self.prob = probs[0][predicted.item()]
            except Exception as e:
                print("\n Error | Test model failed -----")
                print("An error occurred:", e)


        elif self.type == "NN_Tensorflow":
            try:
                sentence = tokenize(sentence)
                x = bag_of_words(sentence, self.all_words)
                x = np.expand_dims(x, axis=0)
                
                output = self.model.predict(x)
                predicted = np.argmax(output, axis=1)
                self.tag = self.label_encoder.inverse_transform(predicted)[0]
                
                probs = tf.nn.softmax(output[0])
                self.prob = probs[predicted[0]]
            except Exception as e:
                print("\n Error | Test model failed -----")
                print("An error occurred:", e)

            
        elif self.type == "NN_Tensorflow_Tf-idf":
            try:
                x = self.vectorizer.transform([sentence]).toarray()
        
                output = self.model.predict(x)
                predicted = np.argmax(output, axis=1)
                self.tag = self.label_encoder.inverse_transform(predicted)[0]
                
                probs = tf.nn.softmax(output[0])
                self.prob = probs[predicted[0]]
            except Exception as e:
                print("\n Error | Test model failed -----")
                print("An error occurred:", e)
            
        else:
            print("\n Error | Please regist the type first -----")

        threshold = 0.5
        print(f'self.tag : {self.tag}')
        print(f'self.prob : {self.prob}')
        if self.prob > threshold:    
            # Getting response from self.tag
            for intent in self.intents['intents']:
                if self.tag == intent['tag']:
                    # Pick random response from intent
                    response = random.choice(intent['responses'])
                    # return response
                    print("\n Response : {response} -----")
        # If not >= threshold
        else:
            # return "I do not understand...."
            print("\n Response : I do not understand.... -----")
        
        print("\n\n Success | Test model done -----")
        
        