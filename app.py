from flask import Flask, request, render_template, send_file
import pdfplumber
import pandas as pd
import os

app = Flask(__name__)

@app.route('/')
def upload_file():
    return render_template('upload.html')

@app.route('/uploader', methods=['POST'])
def uploader():
    pdf_directory = 'uploaded_pdfs'
    output_file = 'extracted_tables.xlsx'
    os.makedirs(pdf_directory, exist_ok=True)

    # Save uploaded files
    files = request.files.getlist('files[]')
    for file in files:
        file.save(os.path.join(pdf_directory, file.filename))
    
    all_tables = []

    def extract_tables(pdf_path):
        tables = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                for table in page.extract_tables():
                    tables.append(table)
        return tables

    with pd.ExcelWriter(output_file) as writer:
        for pdf_file in os.listdir(pdf_directory):
            if pdf_file.endswith('.pdf'):
                pdf_path = os.path.join(pdf_directory, pdf_file)
                tables = extract_tables(pdf_path)
                for i, table in enumerate(tables):
                    df = pd.DataFrame(table[1:], columns=table[0])
                    df.to_excel(writer, sheet_name=f"{pdf_file}_Page_{i+1}", index=False)

    return f'Extraction complete! Download the file <a href="/download/{output_file}">here</a>'

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

