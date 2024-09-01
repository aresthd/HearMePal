import json
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder
from nltk_utils import tokenize, stem, bag_of_words
from model import create_model
import pickle

# Open file json
with open('../../data/intents.json', 'r') as f:
    intents = json.load(f)

# Define lists
all_words = []  # Words in the patterns
tags = []       # Tags of sentences
xy = []         # (Pattern sentence, Tag) pairs

# Process each intent
for intent in intents['intents']:
    tag = intent['tag']
    tags.append(tag)
    for pattern in intent['patterns']:
        w = tokenize(pattern)
        all_words.extend(w)
        xy.append((w, tag))

# Stemming
ignore_words = ['?', '!', '.', ',']
all_words = [stem(w) for w in all_words if w not in ignore_words]
all_words = sorted(set(all_words))
tags = sorted(set(tags))

# Create training data
x_train = []
y_train = []
for (pattern_sentence, tag) in xy:
    bag = bag_of_words(pattern_sentence, all_words)
    x_train.append(bag)
    y_train.append(tag)

# Convert to numpy arrays
x_train = np.array(x_train)
label_encoder = LabelEncoder()
y_train = label_encoder.fit_transform(y_train)
y_train = tf.keras.utils.to_categorical(y_train, num_classes=len(tags))

# Define hyperparameters
input_size = len(x_train[0])
hidden_size = 8
output_size = len(tags)
learning_rate = 0.001
num_epochs = 100
batch_size = 32

# Create the model
model = create_model(input_size, hidden_size, output_size)

# Compile the model
model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
              loss='categorical_crossentropy',
              metrics=['accuracy'])

# Train the model
model.fit(x_train, y_train, epochs=num_epochs, batch_size=batch_size, verbose=1)

# Save model and metadata
# model.save('tensorflow/chat_model.h5')
# metadata = {
#     'input_size': input_size,
#     'output_size': output_size,
#     'hidden_size': hidden_size,
#     'all_words': all_words,
#     'tags': tags,
#     'label_encoder_classes': label_encoder.classes_.tolist()
# }
# with open('tf_metadata.json', 'w') as f:
#     json.dump(metadata, f)
# print('Training complete. Model and metadata saved.')


# Save model and metadata
with open('tf_model_le.pkl', 'wb') as f:
    pickle.dump(model, f)
    
metadata = {
    'input_size': input_size,
    'output_size': output_size,
    'hidden_size': hidden_size,
    'all_words': all_words,
    'tags': tags,
    # 'vectorizer_vocabulary': vectorizer.vocabulary_,
    'label_encoder_classes': label_encoder.classes_.tolist()
}

with open('tf_metadata_le.json', 'w') as f:
    json.dump(metadata, f)
print('Training complete. Model and metadata saved.')

