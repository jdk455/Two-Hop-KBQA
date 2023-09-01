# Import the libraries
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Load the pre-trained model and tokenizer
model = AutoModelForSequenceClassification.from_pretrained("yseop/distilbert-base-financial-relation-extraction")
tokenizer = AutoTokenizer.from_pretrained("yseop/distilbert-base-financial-relation-extraction")

# Define the relation labels
labels = ["x", "has", "is in", "is", "are"]

# Define a sample sentence
sentence = "An A-B trust is a joint trust created by a married couple for the purpose of minimizing estate taxes."

# Tokenize the sentence and add special tokens
inputs = tokenizer(sentence, return_tensors="pt", add_special_tokens=True)

# Get the logits from the model
logits = model(**inputs).logits

# Get the predicted label index
pred_label_idx = torch.argmax(logits, dim=1).item()

# Get the predicted label name
pred_label = labels[pred_label_idx]

# Print the result
print(f"The predicted relation for the sentence '{sentence}' is: {pred_label}")
