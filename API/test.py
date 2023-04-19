import torch
from transformers import AutoModel, AutoTokenizer

model = AutoModel.from_pretrained("vinai/phobert-base")
tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base")

word = "xe hơi"
input_ids = torch.tensor([tokenizer.encode(word, add_special_tokens=True)])
with torch.no_grad():
    last_hidden_states = model(input_ids)[0]


similarities = torch.nn.functional.cosine_similarity(last_hidden_states, last_hidden_states)
similarities = similarities.squeeze().tolist()

similar_words = []

for i, similarity in enumerate(similarities):
    if similarity > 0.8 and tokenizer.decode([input_ids.tolist()[0][i]]) != word:
        similar_words.append(tokenizer.decode([input_ids.tolist()[0][i]]))
        
print(f"Từ đồng nghĩa của {word}:")
for word in similar_words:
    print(word)