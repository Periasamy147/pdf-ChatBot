import nltk
import PyPDF2
from flask import Flask, request, jsonify, render_template
import os

nltk.download('punkt_tab')

UPLOAD_FOLDER = 'uploads'  # Folder to store uploaded files
ALLOWED_EXTENSIONS = {'pdf', 'txt'}  # Allowed file extensions

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

knowledge_base = None  # Initialize knowledge_base as None

class KnowledgeBaseModel:

    def __init__(self, filepath):
        """
        Initializes the KnowledgeBaseModel by reading and processing the text file.

        Args:
            filepath (str): The path to the text file or PDF containing the knowledge base.
        """
        self.sentences = []
        if filepath.lower().endswith(".pdf"):
            self.load_pdf(filepath)
        else:
            self.load_text(filepath)

    def load_text(self, filepath):
        """Loads knowledge base from a text file."""
        with open(filepath, 'r') as file:
            text = file.read()
        self.sentences.extend(nltk.sent_tokenize(text))

    def load_pdf(self, filepath):
        """Loads knowledge base from a PDF file."""
        with open(filepath, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                text = reader.pages[page_num].extract_text()
                self.sentences.extend(nltk.sent_tokenize(text))

    def find_best_match(self, query):
        """
        Finds the sentence in the knowledge base that best matches the given query.

        Args:
            query (str): The user's query.

        Returns:
            str: The sentence from the knowledge base that best matches the query,
                 or None if no relevant sentence is found.
        """
        best_match = None
        max_similarity = 0

        for sentence in self.sentences:
            similarity = nltk.edit_distance(query.lower(), sentence.lower())
            if similarity < max_similarity or max_similarity == 0:
                max_similarity = similarity
                best_match = sentence

        return best_match

    def answer_query(self, query):
        """
        Answers a user's query based on the knowledge base.

        Args:
            query (str): The user's query.

        Returns:
            str: The answer to the query, or a message indicating that the answer
                 cannot be found in the knowledge base.
        """
        best_match = self.find_best_match(query)
        if best_match:
            return best_match
        else:
            return "I'm sorry, I don't have an answer to that question in my knowledge base."

def allowed_file(filename):
    """Checks if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index2.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handles file uploads and creates the knowledge base."""
    global knowledge_base  # Access the global knowledge_base variable

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        knowledge_base = KnowledgeBaseModel(filepath)  # Create knowledge base
        return jsonify({'message': 'File uploaded successfully!'}), 200
    else:
        return jsonify({'error': 'Allowed file types are pdf and txt'}), 400

@app.route('/api/ask', methods=['POST'])
def ask_question():
    global knowledge_base  # Access the global knowledge_base variable

    data = request.get_json()
    query = data.get('query')
    if not query:
        return jsonify({'error': 'Missing query parameter'}), 400

    if knowledge_base:
        answer = knowledge_base.answer_query(query)
        return jsonify({'answer': answer})
    else:
        return jsonify({'error': 'No knowledge base uploaded yet!'}), 400

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
