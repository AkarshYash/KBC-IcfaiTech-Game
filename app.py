import os
from flask import Flask, render_template, request, redirect, url_for, send_file
import pandas as pd
import random

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Function to read and categorize questions
def read_and_categorize_questions(files):
    questions = {'basic': [], 'intermediate': [], 'advanced': []}
    
    for file in files:
        df = pd.read_csv(file)
        for index, row in df.iterrows():
            difficulty = row['difficulty'].lower()
            domain = row['domain']
            question = row['question']

            if difficulty in ['basic', 'intermediate', 'advanced']:
                questions[difficulty].append({
                    'domain': domain,
                    'question': question
                })
    
    return questions

# Function to generate datasets of 15 questions
def generate_datasets(questions, num_sets=1):
    datasets = []
    
    for _ in range(num_sets):
        dataset = []
        for level in ['basic', 'intermediate', 'advanced']:
            selected = random.sample(questions[level], 5)
            dataset.extend(selected)
        datasets.append(dataset)
    
    return datasets

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files[]' not in request.files:
        return redirect(request.url)

    files = request.files.getlist('files[]')
    file_paths = []
    
    for file in files:
        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            file_paths.append(file_path)
    
    # Merge and categorize questions
    questions = read_and_categorize_questions(file_paths)
    
    # Generate dataset with 15 questions (5 basic, 5 intermediate, 5 advanced)
    datasets = generate_datasets(questions)
    
    # Save dataset to CSV
    output_file = 'dataset.csv'
    pd.DataFrame(datasets[0]).to_csv(output_file, index=False)
    
    return send_file(output_file, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
+