import matplotlib.pyplot as plt

bleu_scores = [8,12,11,12,11]
epochs = [1, 2, 3, 4, 5]

plt.plot(epochs, bleu_scores, marker='o')
plt.title('BLEU Score over Epochs')
plt.xlabel('Epoch') 
plt.ylabel('BLEU Score')
plt.xticks(epochs)
plt.show()
