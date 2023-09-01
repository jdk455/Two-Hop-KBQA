import torch
import torch.nn as nn
import torch.optim as optim
from torchtext.datasets import CoNLL2003
from torchtext.data import Field, NestedField, BucketIterator
from torchtext.vocab import Vocab
from collections import Counter

def prepare_data():
    WORD = Field(lower=True)
    NER = Field(unk_token=None, is_target=True)
    CHAR = NestedField(Field(tokenize=list), tokenize=list)
    fields = (("word", WORD), ("char", CHAR), ("ner", NER))

    train_data, valid_data, test_data = CoNLL2003.splits(fields=fields)

    WORD.build_vocab(train_data.word, min_freq=3)
    CHAR.build_vocab(train_data.char)
    NER.build_vocab(train_data.ner)

    return train_data, valid_data, test_data, WORD, CHAR, NER

class BiLSTM_CRF(nn.Module):
    def __init__(self, vocab_size, char_vocab_size, tag_vocab_size, embedding_dim, char_embedding_dim, hidden_dim, char_hidden_dim):
        super(BiLSTM_CRF, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.char_embedding = nn.Embedding(char_vocab_size, char_embedding_dim)
        self.char_lstm = nn.LSTM(char_embedding_dim, char_hidden_dim, bidirectional=True, num_layers=1)
        self.lstm = nn.LSTM(embedding_dim + char_hidden_dim * 2, hidden_dim // 2, bidirectional=True, num_layers=1)
        self.hidden2tag = nn.Linear(hidden_dim, tag_vocab_size)
        self.crf = CRF(tag_vocab_size)

    def forward(self, words, chars, tags):
        words_emb = self.embedding(words)
        char_emb = self.char_embedding(chars)
        char_emb, _ = self.char_lstm(char_emb)
        char_emb = char_emb[:, -1]
        emb = torch.cat((words_emb, char_emb), -1)
        lstm_out, _ = self.lstm(emb)
        emissions = self.hidden2tag(lstm_out)
        loss = -self.crf(emissions, tags)
        return loss

    def predict(self, words, chars):
        words_emb = self.embedding(words)
        char_emb = self.char_embedding(chars)
        char_emb, _ = self.char_lstm(char_emb)
        char_emb = char_emb[:, -1]
        emb = torch.cat((words_emb, char_emb), -1)
        lstm_out, _ = self.lstm(emb)
        emissions = self.hidden2tag(lstm_out)
        return self.crf.decode(emissions)

def train(model, iterator, optimizer, device):
    model.train()
    total_loss = 0

    for batch in iterator:
        words, chars, tags = batch.word.to(device), batch.char.to(device), batch.ner.to(device)
        optimizer.zero_grad()
        loss = model(words, chars, tags)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()

    return total_loss / len(iterator)

def evaluate(model, iterator, device):
    model.eval()
    total_loss = 0

    with torch.no_grad():
        for batch in iterator:
            words, chars, tags = batch.word.to(device), batch.char.to(device), batch.ner.to(device)
            loss = model(words, chars, tags)
            total_loss += loss.item()

    return total_loss / len(iterator)

def main():
    # 参数设置
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    EMBEDDING_DIM = 100
    CHAR_EMBEDDING_DIM = 30
    HIDDEN_DIM = 200
    CHAR_HIDDEN_DIM = 50
    BATCH_SIZE = 32
    N_EPOCHS = 5

    # 数据准备
    train_data, valid_data, test_data, WORD, CHAR, NER = prepare_data()
    train_iter, valid_iter, test_iter = BucketIterator.splits((train_data, valid_data, test_data), batch_size=BATCH_SIZE, device=device)

    # 模型初始化
    model = BiLSTM_CRF(len(WORD.vocab), len(CHAR.vocab), len(NER.vocab), EMBEDDING_DIM, CHAR_EMBEDDING_DIM, HIDDEN_DIM, CHAR_HIDDEN_DIM).to(device)
    optimizer = optim.Adam(model.parameters())

    # 训练和评估
    best_valid_loss = float("inf")
    for epoch in range(N_EPOCHS):
        train_loss = train(model, train_iter, optimizer, device)
        valid_loss = evaluate(model, valid_iter, device)

        if valid_loss < best_valid_loss:
            best_valid_loss = valid_loss
            torch.save(model.state_dict(), "ner_bilstm_crf_best.pt")

        print(f"Epoch: {epoch+1} | Train Loss: {train_loss:.3f} | Valid Loss: {valid_loss:.3f}")

    # 测试
    model.load_state_dict(torch.load("ner_bilstm_crf_best.pt"))
    test_loss = evaluate(model, test_iter, device)
    print(f"Test Loss: {test_loss:.3f}")
    # 加载模型
    model.load_state_dict(torch.load("ner_bilstm_crf_best.pt"))
    # 输入句子并预测
    sentence = "Larry Page is the co-founder of Google."
    sentence_tags = predict_sentence(model, sentence, WORD, CHAR, NER, device)
    entities = extract_entities(sentence_tags)
    print(f"Entities: {entities}")


def process_sentence(sentence, word_field, char_field, device):
    words = word_field.preprocess(sentence)
    chars = char_field.preprocess(words)
    word_tensor = word_field.process([words]).to(device)
    char_tensor = char_field.process([chars]).to(device)
    return word_tensor, char_tensor

def predict_sentence(model, sentence, word_field, char_field, tag_field, device):
    model.eval()
    word_tensor, char_tensor = process_sentence(sentence, word_field, char_field, device)
    with torch.no_grad():
        pred_tags = model.predict(word_tensor, char_tensor)[0]
    pred_tags = [tag_field.vocab.itos[tag] for tag in pred_tags]
    return list(zip(sentence.split(), pred_tags))

def extract_entities(sentence_tags):
    entities = {}
    current_entity = []
    current_tag = None

    for word, tag in sentence_tags:
        if tag.startswith("B-"):
            if current_entity:
                entities[" ".join(current_entity)] = current_tag
            current_entity = [word]
            current_tag = tag[2:]
        elif tag.startswith("I-"):
            if current_tag == tag[2:]:
                current_entity.append(word)
            else:
                if current_entity:
                    entities[" ".join(current_entity)] = current_tag
                current_entity = [word]
                current_tag = tag[2:]
        else:
            if current_entity:
                entities[" ".join(current_entity)] = current_tag
                current_entity = []
                current_tag = None

    if current_entity:
        entities[" ".join(current_entity)] = current_tag

    return entities


if __name__ == "__main__":
    main()