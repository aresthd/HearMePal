import random
import json
import torch
# from model import NeuralNet
from nltk_utils import bag_of_words, tokenize
import pickle


PATH_INTENTS = '../../data/intents.json'
# PATH_MODEL = 'model_torch.h5'
# PATH_METADATA = 'metadata_torch.json'
# PATH_DATA = 'code/try_yt_torch/data_torch.pth'
PATH_MODEL = 'torch_model.pkl'
PATH_METADATA = 'torch_metadata.json'
PATH_MODEL_PTH = 'torch_model.pth'


# Checking cuda
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Open file intents json
with open(PATH_INTENTS, 'r') as f:
    intents = json.load(f)
print("\n Load data intents done-----")

# # Load file data of result training
# data = torch.load(PATH_DATA)

# # Taking the parameter from data
# input_size = data['input_size']
# hidden_size = data['hidden_size']
# output_size = data['output_size']
# all_words = data['all_words']
# tags = data['tags']
# model_state = data['model_state']
# # print(model_state)

# # Create model
# model = NeuralNet(input_size, hidden_size, output_size).to(device)

# # Load model
print("\n Start load model-----")
# model.load_state_dict(model_state)
# model.eval()

# Load model (.pth)
model = torch.load(PATH_MODEL_PTH)
print("\n Success load model-----")


# Load the model (.pkl) and metadata (.json)
# with open(PATH_MODEL, 'rb') as f:
#     model = pickle.load(f)
# model = torch.load(PATH_MODEL)
# model.eval()
print("\n Load model done-----")

with open(PATH_METADATA, 'r') as f:
    metadata = json.load(f)
print("\n Load metadata done-----")

# Taking the parameter from metadata
# input_size = metadata['input_size']
# hidden_size = metadata['hidden_size']
# output_size = metadata['output_size']
all_words = metadata['all_words']
tags = metadata['tags']

# Create chat bot
bot_name = '(X) Torch'
print("Let's chat! Type 'quit' to exit")

# Loop the chat bot
while True:
    # Get setence of input user
    setence = input('You: ')
    # Break loop if quit
    if setence == 'quit':
        break
    
    
    # Different -----------------
    # Tokenizing the setence
    setence = tokenize(setence)
    
    x = bag_of_words(setence, all_words)
    x = x.reshape(1, x.shape[0])    # 1 -> row; x.shape[0] -> column
    
    x = torch.from_numpy(x)
    
    # Predict data
    output = model(x)
    
    # Getting the result of predict
    _, predicted = torch.max(output, dim=1)
    tag = tags[predicted.item()]
    
    # Calculate the probablity of predict
    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]
    
    
    
    # Checking the probability to threshold
    threshold = 0.25
    print(f'prob : {prob}')
    print(f'prob.items() : {prob.item()}')
    if prob.item() > threshold:    
        # Getting response from tag
        for intent in intents['intents']:
            if tag == intent['tag']:
                # Pick random response from intent
                response = random.choice(intent['responses'])
                
                # Print the response
                print(f"{bot_name} : {response}\n")
    # If not >= threshold
    else:
        print(f"{bot_name} : I do not understand....\n")
