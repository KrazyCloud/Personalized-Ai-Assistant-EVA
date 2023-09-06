import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report

data = pd.read_csv(r'C:\Practice\Chatbot Project\MyEVA\files\arthimatic\arithmatic_dataset.csv')
data.head()

data.drop_duplicates(inplace=True)

data.duplicated().value_counts()

# Split the data into training and testing sets
train_data, test_data = train_test_split(data, test_size=0.2, random_state=42)

# Extract messages and intents
train_messages = train_data['Message']
train_intents = train_data['Intent']
test_messages = test_data['Message']
test_intents = test_data['Intent']

# Tokenize messages
tokenizer = tf.keras.preprocessing.text.Tokenizer()
tokenizer.fit_on_texts(train_messages)

train_sequences = tokenizer.texts_to_sequences(train_messages)
test_sequences = tokenizer.texts_to_sequences(test_messages)

vocab_size = len(tokenizer.word_index) + 1

# Encode intents using LabelEncoder
encoder = LabelEncoder()
train_labels = encoder.fit_transform(train_intents)
test_labels = encoder.transform(test_intents)

# Pad sequences
max_seq_length = max(map(len, train_sequences))
train_sequences = tf.keras.preprocessing.sequence.pad_sequences(train_sequences, maxlen=max_seq_length)
test_sequences = tf.keras.preprocessing.sequence.pad_sequences(test_sequences, maxlen=max_seq_length)

# Build the model
model = tf.keras.Sequential([
    tf.keras.layers.Embedding(input_dim=vocab_size, output_dim=64, input_length=max_seq_length),
    tf.keras.layers.GlobalAveragePooling1D(),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(len(encoder.classes_), activation='softmax')
])

model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
print(model.summary())

# Train the model
model.fit(train_sequences, train_labels, epochs=50, batch_size=32, validation_split=0.1)

# Evaluate the model
loss, accuracy = model.evaluate(test_sequences, test_labels)
print(f"Test accuracy: {accuracy:.4f}")

# Make predictions
predicted_probabilities = model.predict(test_sequences)
predicted_labels = predicted_probabilities.argmax(axis=1)
class_names = encoder.classes_
classification_rep = classification_report(test_labels, predicted_labels, target_names=class_names)
print(classification_rep)

# After training the model
model.save('arthimatic_model.h5')


import tensorflow as tf

def test_intent_recognition_model(model_filename, tokenizer, encoder):
    # Load the saved model
    loaded_model = tf.keras.models.load_model(model_filename)

    while True:
        # Get user input
        user_input = input("Enter an arithmetic problem message (or 'exit' to quit): ")
        if user_input.lower() in ['exit', 'quit']:
            print("Exiting...")
            break

        # Tokenize and pad user input
        user_sequence = tokenizer.texts_to_sequences([user_input])
        user_sequence = tf.keras.preprocessing.sequence.pad_sequences(user_sequence, maxlen=max_seq_length)

        # Predict intent
        predicted_probability = loaded_model.predict(user_sequence)
        predicted_label = predicted_probability.argmax()
        predicted_intent = encoder.inverse_transform([predicted_label])[0]

        print(f"Predicted Intent: {predicted_intent}")

if __name__ == "__main__":
    # Load tokenizer and encoder
    tokenizer = tf.keras.preprocessing.text.Tokenizer()
    tokenizer.fit_on_texts(train_messages)
    max_seq_length = max(map(len, train_sequences))

    encoder = LabelEncoder()
    train_labels = encoder.fit_transform(train_intents)

    # Load the trained model in .h5 format and test using the function
    model_filename = r'C:\Practice\Chatbot Project\MyEVA\files\arthimatic\arthimatic_model.h5'
    test_intent_recognition_model(model_filename, tokenizer, encoder)
