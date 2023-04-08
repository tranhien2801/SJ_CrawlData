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

@app.route('/judgment/list', methods=['POST'])
def search_judgments():
    data = request.get_json()
    
    query = "SELECT * FROM court.judgment j  LEFT JOIN court.court jc ON j.court_uid = jc.uid LEFT JOIN court.case ja ON j.case_uid = ja.uid WHERE j.state = 1 "
    if  data['court_level'] != None and data['court_level'] != '':
        query += " AND jc.court_level LIKE \"" + data['court_level'] + "\""
    if  data['judgment_level'] != '' and data['judgment_level'] != None: 
        query += " AND j.judgment_level LIKE \"" + data['judgment_level'] + "\""  
    if  data['type_document'] != '' and data['type_document'] != None: 
        query += " AND j.type_document LIKE \"" + data['type_document'] + "\""       
    if  data['case_type'] != '' and data['case_type'] != None: 
        query += " AND ja.case_type LIKE \"" + data['case_type'] + "\""  
    query += ";"    
        
    mycursor.execute(query)
    judgments = mycursor.fetchall()
    i = 0
    judgment_tokens = []
    for judgment in judgments:
        judgment_tokens.append(preprocess_string(judgment["judgment_content"]))
    bm25_index = BM25Okapi(judgment_tokens)

    def search(search_string, num_results=10):
        search_tokens = preprocess_string(search_string)
        scores = bm25_index.get_scores(search_tokens)
        top_indexes = np.argsort(scores)[::-1][:num_results]
        return top_indexes
    
    indexes = search(data['judgment_content'])
    print(indexes)

    response = []
    for index in indexes:
        response.append(judgments[index])
    
    return jsonify(response)
  
   
if __name__ == '__main__':
    app.run(port=5000)

