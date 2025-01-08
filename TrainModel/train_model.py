import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import json
import random
import pickle
import os


class SimpleChatBotModel:
    def __init__(self, max_sequence_length=20):
        self.max_sequence_length = max_sequence_length
        self.tokenizer = Tokenizer(oov_token="<OOV>")
        self.model = None
        self.responses = {}
        self.labels = []

    def load_data(self, json_file):
        try:
            with open(json_file, 'r') as json_file:
                self.training_data = json.load(json_file)
            print("training data loaded")
            questions = []
            self.labels = []
            for intent in self.training_data['intents']:
                self.responses[intent['tag']] = intent['responses']

                for pattern in intent['patterns']:
                    questions.append(pattern)
                    self.labels.append(intent['tag'])

            self.tokenizer.fit_on_texts(questions)
            self.total_words = len(self.tokenizer.word_index) + 1

            sequences = self.tokenizer.texts_to_sequences(questions)
            self.padded_sequences = pad_sequences(sequences, maxlen=self.max_sequence_length, padding="post")

            self.label_tokenizer = Tokenizer()
            self.label_tokenizer.fit_on_texts(self.labels)
            self.label_sequences = np.array(self.label_tokenizer.texts_to_sequences(self.labels))
            self.num_classes = len(self.label_tokenizer.word_index) + 1

            print("Total words: {}".format(self.total_words))

        except FileNotFoundError:
            print("Training data not found. Please run train.py first.")

    def build_model(self):
        self.model = tf.keras.Sequential([
            tf.keras.layers.Embedding(self.total_words, 64,
                                      input_length=self.max_sequence_length),
            tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(32)),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dropout(0.5),
            tf.keras.layers.Dense(self.num_classes, activation='softmax')
        ])

        self.model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    def train(self, epochs=100):
        self.model.fit(
            self.padded_sequences,
            self.label_sequences - 1,
            epochs=epochs,
            verbose=1
        )

    def save_model(self, model_dir="chatbot_model"):
        from typing import cast, BinaryIO
        import pickle

        if not os.path.exists(model_dir):
            os.makedirs(model_dir)

        self.model.save(f'{model_dir}/chatbot_model.h5')

        with open(f'{model_dir}/tokenizer.pickle', 'wb') as file_token:
            pickle.dump(self.tokenizer, file_token, protocol=pickle.HIGHEST_PROTOCOL)

        with open(f'{model_dir}/label_tokenizer.pickle', 'wb') as file_token:
            pickle.dump(self.label_tokenizer, file_token, protocol=pickle.HIGHEST_PROTOCOL)

        with open(f'{model_dir}/responses.json', 'w') as responses:
            json.dump(self.responses, responses)

    def load_model(self, model_dir="chatbot_model"):
        self.model = tf.keras.models.load_model(f"{model_dir}/model.h5")

        with open(f'{model_dir}/tokenizer.pickle', 'rb') as file_token:
            self.tokenizer = pickle.load(file_token)

        with open(f'{model_dir}/label_tokenizer.pickle', 'rb') as file_token:
            self.label_tokenizer = pickle.load(file_token)

        with open(f'{model_dir}/responses.json', 'r') as responses:
            self.responses = json.load(responses)

        self.total_words = len(self.tokenizer.word_index) + 1
        self.num_classes = len(self.label_tokenizer.word_index) + 1

    def predict(self, text_to_predict):
        sequence = self.tokenizer.texts_to_sequences([text_to_predict])
        padded = pad_sequences(sequence, maxlen=self.max_sequence_length, padding="post")

        prediction = self.model.predict(padded)
        predicted_label = np.argmax(prediction) + 1

        for tag, index in self.label_tokenizer.word_index.items():
            if index == predicted_label:
                return random.choice(self.responses[tag])

        return "I'm not sure how to respond to that."


"""Adding the main function"""

if __name__ == "__main__":
    simple_chat_model = SimpleChatBotModel()
    train_model = input("Do you want to train a new model? (y/n): ").lower()

    if train_model == 'y':
        print("Training new model for you, be patient!\n")
        simple_chat_model.load_data("/Users/saber/PyProjects/AiProject/TrainModel/data_file.json")
        simple_chat_model.build_model()
        simple_chat_model.train(epochs=100)
        simple_chat_model.save_model()

    else:
        print("\nLoading Existing model for you, be patient!\n")
        simple_chat_model.load_model()

    print("\nChat with the bot (Type 'q' to exit):)")
    while True:
        user_input = input("> ")
        if user_input.lower() == 'q' or user_input.lower() == 'quit':
            break
        response = simple_chat_model.predict(user_input)
        print("BOT: {}".format(response))
