import time
from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import pandas as pd
import numpy as np
from rank_bm25 import BM25Okapi
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import preprocess_documents, preprocess_string
from deep_translator import GoogleTranslator
from synonym import find_synonyms

app = Flask(__name__)
CORS(app)

pd.options.display.max_colwidth=160

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="conan1411",
    database="court"
)

mycursor = mydb.cursor(dictionary=True)

query = "SELECT j.uid, j.judgment_number, j.judgment_name, j.type_document, j.judgment_level, j.judgment_content, j.date_issued, j.date_upload, j.url, j.pdf_viewer, j.file_download, j.corrections, j.count_vote, j.count_eyes, j.count_download, jc.court_name, ja.case_name FROM court.judgment j  LEFT JOIN court.court jc ON j.court_uid = jc.uid LEFT JOIN court.case ja ON j.case_uid = ja.uid WHERE j.state = 1;"
mycursor.execute(query)
judgments = mycursor.fetchall()
number_judgment = len(judgments)   
judgment_tokens = []
for judgment in judgments:
    judgment_tokens.append(preprocess_string(judgment["judgment_content"]))
bm25_index = BM25Okapi(judgment_tokens)


def search(search_string, num_results):
    search_tokens = preprocess_string(search_string)
    scores = bm25_index.get_scores(search_tokens)
    top_indexes = np.argsort(scores)[::-1][:num_results]
    return top_indexes
    
def search_list(search_list, num_results):
    list_scores = []
    print("Bắt đầu tìm kiếm-----------")
    for search_string in search_list:
        print(search_string)
        search_tokens = preprocess_string(search_string)
        scores = bm25_index.get_scores(search_tokens)
        list_scores.extend(scores)
    print(np.sort(list_scores)[::-1][:num_results])   
    top_indexes = np.argsort(list_scores)[::-1][:num_results]
    print("Kết thúc tìm kiếm-----------")
    for i in range(len(top_indexes)):
        top_indexes[i] = top_indexes[i] % number_judgment
    print(top_indexes)
    return set(top_indexes)

@app.route('/recommendation', methods=['GET'])
def recommendation():   
    indexes = search(request.args.get('content', type=str), 10)
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
    # try:
        filter = request.get_json()
        # Dịch nội dung tìm kiếm sang tiếng Anh để tìm từ đồng nghĩa
        translatorEnToVi = GoogleTranslator(source='en', target='vi')
        translatorViToEn = GoogleTranslator(source='vi', target='en')
        content_filter = filter['judgment_content']
        time.sleep(0.01)
        content_filter_english = translatorViToEn.translate(content_filter)
        print(content_filter_english)

        new_sentences = find_synonyms(content_filter_english)
        new_sentences_trans = set()
        new_sentences_trans.add(content_filter)
        
        for new_sentence in new_sentences:
            sentence_trans = translatorEnToVi.translate(new_sentence)
            if sentence_trans != content_filter:
                new_sentences_trans.add(sentence_trans)
        for i in new_sentences_trans:
            print(i)    
        indexes = search_list(new_sentences_trans, 50)
        # indexes = search(content_filter, 50)
        
        data = []
        for index in indexes:
            check = True
            if  filter['court_level'] != None and filter['court_level'] != '' and judgments[index]['court_level'] != filter['court_level']:
                check = False
            if  filter['judgment_level'] != '' and filter['judgment_level'] != None and judgments[index]['judgment_level'] != filter['judgment_level']: 
                check = False
            if  filter['type_document'] != '' and filter['type_document'] != None and judgments[index]['type_document'] != filter['type_document']: 
                check = False
            if  filter['case_type'] != '' and filter['case_type'] != None and judgments[index]['case_type'] != filter['case_type']: 
                check = False
            if check:
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
    # except:
    #     print("An exception occurred")
    #     response = {
    #         "message": "error",
    #         "data": None,
    #         "status": 500,
    #         "error": None
    #     }
    #     return jsonify(response)
   
if __name__ == '__main__':
    # app.run(port=5000)
    from waitress import serve
    serve(app, host="127.0.0.1", port=5000)

