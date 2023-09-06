import pickle
import spacy

# Load spaCy's English tokenizer and language model
nlp = spacy.load("en_core_web_sm")

# Load the trained classifier and vectorizer
# Specify the paths to the model and vectorizer files
model_path = '/workspaces/eva-connect/task_model/file/eva_born_model.pkl'
vectorizer_path = '/workspaces/eva-connect/task_model/file/tfidf_vectorizer.pkl'

# Load the trained classifier and vectorizer
def load_models():
    # Access the paths from the global variables
    global model_path, vectorizer_path

    # Load the trained classifier and vectorizer
    with open(model_path, 'rb') as model_file:
        classifier = pickle.load(model_file)

    with open(vectorizer_path, 'rb') as vectorizer_file:
        vectorizer = pickle.load(vectorizer_file)

    return classifier, vectorizer

# Preprocess text data
def preprocess_text(text):
    doc = nlp(text)
    tokens = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
    return " ".join(tokens)

def predict_intent(text):
    # Preprocess the input text
    processed_text = preprocess_text(text)

    # Load the classifier and vectorizer
    classifier, vectorizer = load_models()

    # Vectorize the preprocessed text
    text_vec = vectorizer.transform([processed_text])

    # Predict the intent
    intent = classifier.predict(text_vec)[0]

    return intent