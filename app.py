from flask import Flask, render_template, request, jsonify
import random
import json
import torch
from model import NeuralNet
from nltk_utils import bag_of_words, tokenize

# Create the Flask application
app = Flask(__name__)
# Load the model and data
FILE = "data.pth"
data = torch.load(FILE)
initial_message_shown = False

# Rest of the code for loading model and data
# Define the route and view function
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    global initial_message_shown  # Add this line to access the global variable

    # Get the user input from the web form
    user_input = request.form['user_input']

    # Perform the chatbot logic
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    with open('intents.json', 'r') as json_data:
        intents = json.load(json_data)
    input_size = data["input_size"]
    hidden_size = data["hidden_size"]
    output_size = data["output_size"]
    all_words = data['all_words']
    tags = data['tags']
    model_state = data["model_state"]

    model = NeuralNet(input_size, hidden_size, output_size).to(device)
    model.load_state_dict(model_state)
    model.eval()

    bot_name = ""
    bot_response = ""

    # Rest of the code for chatbot logic
    sentence = user_input
    sentence = tokenize(sentence)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)

    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]
    if prob.item() > 0.75:
        for intent in intents['intents']:
            if tag == intent["tag"]:
                bot_response = f"{bot_name} {random.choice(intent['responses'])}"
    else:
        bot_response = f"{bot_name} I do not understand..."

    return jsonify({'response': bot_response})

if __name__ == '__main__':
    app.run()