#implement the nlt utils
import numpy as np
import nltk
#nltk.download('punkt')
#nltk.download('punkt')
#nltk.download('wordnet')
#nltk.download('omw-1.4')

from nltk.stem.porter import PorterStemmer
stemmer =PorterStemmer()

def tokenize(sentence):
  #split sentence into array of words/tokens

  return nltk.word_tokenize(sentence)

def stem(word):
  #find the roots form of the word
  #eg working worked becomes work

  return stemmer.stem(word.lower())


def bag_of_words(tokenized_sentence, words):

  #return bag of words array:
  #1 for each known word that exists in the sentence, 0 otherwise
  #example:
  #sentence = ["hello", "how", "are", "you"]
  #words = ["hi", "hello", "I", "you", "bye", "thank", "cool"]
  #bog   = [  0 ,    1 ,    0 ,   1 ,    0 ,    0 ,      0]

  #call the stem function to stem all words
  sentence_words = [stem(word) for word in tokenized_sentence]
  #initialize bag with 0 for each word
  bag = np.zeros(len(words), dtype=np.float32)
  for idx, w in enumerate(words):
    if w in sentence_words:
      bag[idx] = 1

  return bag

