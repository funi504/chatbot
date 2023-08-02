#implementing the training pipeline
# train.py
import numpy as np
import random
import json
import pickle
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

from nltk_utils import bag_of_words, tokenize, stem
from model import NeuralNet

def train(project_id):

  intent_file = project_id+".json"
  
  with open(intent_file,'r') as f:
    intents = json.load(f)

  all_words = []
  tags = []
  xy = []

  #loop through each sentence in our intents pattens
  for intent in intents['intents']:
    tag = intent['tag']
    #add tag to list
    tags.append(tag)
    for pattern in intent['patterns']:
      w = tokenize(pattern)

      all_words.extend(w)

      xy.append((w,tag))



  #stem and lower case each word
  ignore_words = ['?', '.', '!']
  all_words = [stem(w) for w in all_words if w not in ignore_words]

  # remove duplicates and sort
  all_words = sorted(set(all_words))
  tags = sorted(set(tags))

  #crate training data
  X_train = []
  y_train = []

  for (pattern_sentence, tag) in xy:
      # X: bag of words for each pattern_sentence
      bag = bag_of_words(pattern_sentence, all_words)
      X_train.append(bag)
      # y: PyTorch CrossEntropyLoss needs only class labels, not one-hot
      label = tags.index(tag)
      y_train.append(label)

  X_train = np.array(X_train)
  y_train = np.array(y_train)

  # Hyper-parameters
  num_epochs = 1000
  #made a change fro 8 to 3 to 1
  batch_size = 8
  learning_rate = 0.001
  input_size = len(X_train[0])
  hidden_size = 8
  output_size = len(tags)


  class ChatDataset(Dataset):

      def __init__(self):
          self.n_samples = len(X_train)
          self.x_data = X_train
          self.y_data = y_train

      # support indexing such that dataset[i] can be used to get i-th sample
      def __getitem__(self, index):
          return self.x_data[index], self.y_data[index]

      # we can call len(dataset) to return the size
      def __len__(self):
          return self.n_samples

  dataset = ChatDataset()
  #removed num_worker= 2
  train_loader = DataLoader(dataset=dataset,
                            batch_size=batch_size,
                            shuffle=True,
                            
                            )

  device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

  model = NeuralNet(input_size, hidden_size, output_size).to(device)

  # Loss and optimizer
  criterion = nn.CrossEntropyLoss()
  optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
  #made a change####
  #target = torch.empty(batch_size, dtype=torch.long).random_(output_size)
  #train the model
  for epoch in range(num_epochs):
    for (words, labels) in train_loader:
      words = words.to(device)
      labels = labels.to(device)

      #labels = torch.empty(batch_size, dtype=torch.long).random_(output_size)
      #foward pass
      outputs = model(words)
      # if y would be one-hot, we must apply
      #labels = torch.max(labels, 1)[1]
      #made a change####
      loss = criterion(outputs, labels.long())

      #backward and optimize
      optimizer.zero_grad()
      loss.backward()
      optimizer.step()

      if (epoch+1) % 100 == 0:
        print (f'Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}')

  print(f'final loss: {loss.item():.4f}')

  data = {
  "model_state": model.state_dict(),
  "input_size": input_size,
  "hidden_size": hidden_size,
  "output_size": output_size,
  "all_words": all_words,
  "tags": tags
  }
  FILE = project_id+".pth"
  torch.save(data, FILE)
