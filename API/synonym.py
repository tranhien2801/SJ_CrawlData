from nltk.tokenize import word_tokenize
from nltk import pos_tag
from nltk.corpus import wordnet
import nltk

nltk.download('wordnet')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

def find_synonyms(text, num_results=10):
  tokens = word_tokenize(text)
  pos_tags = pos_tag(tokens)
  print(pos_tags)

  new_sentences = []

  for word, tag in pos_tags:
      if tag.startswith('NN'):
        synonyms = []
        print(word)
        for synset in wordnet.synsets(word):
          for lemma in synset.lemmas():
            if lemma.synset().pos() == 'n' and lemma.name() != word:
              synonyms.append(lemma.name())
              new_text = text
              new_sentences.append(new_text.replace(word, lemma.name().replace("_", " ")))
        print(set(synonyms))
  return set(new_sentences[:num_results])
      

