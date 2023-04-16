from flask import Flask, request, jsonify
import mysql.connector
import pandas as pd
import numpy as np
from rank_bm25 import BM25Okapi
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import preprocess_documents, preprocess_string

app = Flask(__name__)

pd.options.display.max_colwidth=160

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="conan1411",
    database="court"
)

mycursor = mydb.cursor(dictionary=True)

@app.route('/recommendation', methods=['GET'])
def recommendation():    
    query = "SELECT j.uid, j.judgment_number, j.judgment_name, j.type_document, j.judgment_level, j.judgment_content, j.date_issued, j.date_upload, j.url, j.pdf_viewer, j.file_download, j.corrections, j.count_vote, j.count_eyes, j.count_download, jc.court_name, ja.case_name FROM court.judgment j  LEFT JOIN court.court jc ON j.court_uid = jc.uid LEFT JOIN court.case ja ON j.case_uid = ja.uid WHERE j.state = 1;"
        
    mycursor.execute(query)
    judgments = mycursor.fetchall()
    
    judgment_tokens = []
    for judgment in judgments:
        judgment_tokens.append(preprocess_string(judgment["judgment_content"]))
    bm25_index = BM25Okapi(judgment_tokens)

    def search(search_string, num_results=10):
        search_tokens = preprocess_string(search_string)
        scores = bm25_index.get_scores(search_tokens)
        top_indexes = np.argsort(scores)[::-1][:num_results]
        return top_indexes
    indexes = search(request.args.get('content', type=str))
    print(indexes)

    data = []
    for index in indexes:
        data.append(judgments[index])
        
    response = {
        "message": "OK",
        "data": data,
        "status": 200,
        "total_page": 1,
        "size": 10,
        "total": len(data),
        "page": 1
    }
    return jsonify(response) 

@app.route('/judgment/list', methods=['POST'])
def search_judgments():
    filter = request.get_json()    
    
    query = "SELECT j.uid, j.judgment_number, j.judgment_name, j.type_document, j.judgment_level, j.judgment_content, j.date_issued, j.date_upload, j.url, j.pdf_viewer, j.file_download, j.corrections, j.count_vote, j.count_eyes, j.count_download, jc.court_name, ja.case_name FROM court.judgment j  LEFT JOIN court.court jc ON j.court_uid = jc.uid LEFT JOIN court.case ja ON j.case_uid = ja.uid WHERE j.state = 1 "
    if  filter['court_level'] != None and filter['court_level'] != '':
        query += " AND jc.court_level LIKE \"" + filter['court_level'] + "\""
    if  filter['judgment_level'] != '' and filter['judgment_level'] != None: 
        query += " AND j.judgment_level LIKE \"" + filter['judgment_level'] + "\""  
    if  filter['type_document'] != '' and filter['type_document'] != None: 
        query += " AND j.type_document LIKE \"" + filter['type_document'] + "\""       
    if  filter['case_type'] != '' and filter['case_type'] != None: 
        query += " AND ja.case_type LIKE \"" + filter['case_type'] + "\""  
    query += ";"    
        
    mycursor.execute(query)
    judgments = mycursor.fetchall()
    
    judgment_tokens = []
    for judgment in judgments:
        judgment_tokens.append(preprocess_string(judgment["judgment_content"]))
    bm25_index = BM25Okapi(judgment_tokens)

    def search(search_string, num_results=10):
        search_tokens = preprocess_string(search_string)
        scores = bm25_index.get_scores(search_tokens)
        top_indexes = np.argsort(scores)[::-1][:num_results]
        return top_indexes
    
    # Dịch nội dung tìm kiếm sang tiếng Anh để tìm từ đồng nghĩa
    content = filter['judgment_content']
    

    
    indexes = search(content)
    print(indexes)

    data = []
    for index in indexes:
        data.append(judgments[index])
        
    response = {
        "message": "OK",
        "data": data,
        "status": 200,
        "total_page": 1,
        "size": 10,
        "total": len(data),
        "page": 1
    }
    
    return jsonify(response)

   
if __name__ == '__main__':
    app.run(port=5000)

