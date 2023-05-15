from crawl import performCrawl
from API import search, summarization
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# if __name__ == '__main__':
#     performCrawl.funcMain("01/11/2022", "30/11/2022")

@app.route('/crawler', methods=['POST'])
def crawlJudgments():
    # try:
        filter = request.get_json()
        print(filter)
        date_from = datetime.strptime(filter['date_from'], '%Y-%d-%m').strftime('%d/%m/%Y')
        date_to = datetime.strptime(filter['date_to'], '%Y-%d-%m').strftime('%d/%m/%Y')
        totalCrawl = performCrawl.funcMain(date_from, date_to)
        response = {
            "message": "Tổng bản ghi đã crawl: " + str(totalCrawl),
            "data": {
                "number_crawled": totalCrawl,
                "date_crawled": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            },
            "status": 200,
        }
        return jsonify(response) 
    # except:
    #     response = {
    #         "message": "error",
    #         "data": "",
    #         "status": 500,
    #     }
    #     return jsonify(response)

@app.route('/recommendation', methods=['GET'])
def recommendation():
    data = search.recommendation()
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

@app.route('/judgment/bm25', methods=['POST'])
def searchJudgments():
    data = search.search_judgments()
    if data != None:
        response = {
                "message": "OK",
                "data": data,
                "status": 200,
                "total_page": 1,
                "size": 10,
                "total": len(data),
                "page": 1
            }
    else:
        response = {
                "message": "OK",
                "data": data,
                "status": 200,
                "total_page": 1,
                "size": 10,
                "total": 0,
                "page": 1
            }
        
    return jsonify(response)

@app.route('/summarization', methods=['GET'])
def summarizeJudgment():
    output = summarization.summarize()
    response = {
        "message": "OK",
        "data": output,
        "status": 200,
    }
    return jsonify(response)

if __name__ == '__main__':
    from waitress import serve
    serve(app, host="127.0.0.1", port=5000)