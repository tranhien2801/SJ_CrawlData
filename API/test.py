import math
from pyvi import ViTokenizer
import mysql.connector


mydb = mysql.connector.connect(
    host ="localhost",
    user="root",
    password="conan1411",
    database="search_judgment"
)

mycursor = mydb.cursor(dictionary=True)

query = "SELECT j.uid, j.judgment_number, j.judgment_name, j.type_document, j.judgment_level, j.judgment_content, j.date_issued, j.date_upload, j.url, j.pdf_viewer, j.file_download, j.corrections, j.count_vote, j.count_eyes, j.count_download, jc.court_name, ja.case_name, ja.case_type, jc.court_level FROM search_judgment.judgment j  LEFT JOIN search_judgment.court jc ON j.court_uid = jc.uid LEFT JOIN search_judgment.case ja ON j.case_uid = ja.uid WHERE j.state = 1;"
mycursor.execute(query)
judgments = mycursor.fetchall()
number_judgment = len(judgments)   
judgment_tokens = []
for judgment in judgments:
    judgment_tokens.append((judgment["judgment_content"]))

def calculate_bm25(word, sentence, corpus, k=1.2, b=0.75):
    """
    Tính trọng số của từ trong câu dựa trên thuật toán BM25

    Args:
        word (str): Từ cần tính trọng số
        sentence (str): Câu chứa từ cần tính trọng số
        corpus (list): Danh sách các câu trong văn bản đầu vào
        k (float, optional): Tham số k trong thuật toán BM25 (mặc định là 1.2)
        b (float, optional): Tham số b trong thuật toán BM25 (mặc định là 0.75)

    Returns:
        float: Trọng số của từ trong câu
    """
    # Sử dụng thư viện ViTokenizer để phân tích cú pháp và tách từ trong câu
    sentence_tokens = ViTokenizer.tokenize(sentence).lower().split(" ")
    
    # Tính số lần xuất hiện của từ trong câu
    word_freq = sentence_tokens.count(word.lower())
    
    # Tính IDF (inverse document frequency)
    N = len(corpus)
    n_word = sum([1 for sentence in corpus if word.lower() in ViTokenizer.tokenize(sentence).lower()])
    idf = math.log(1 + (N - n_word + 0.5) / (n_word + 0.5))
    
    # Tính trọng số của từ trong câu
    avg_sentence_len = sum([len(ViTokenizer.tokenize(sentence).lower().split(" ")) for sentence in corpus]) / N
    sentence_len = len(sentence_tokens)
    bm25 = idf * ((word_freq * (k + 1)) / (word_freq + k * (1 - b + b * (sentence_len / avg_sentence_len))))
    
    return bm25

# Ví dụ về cách sử dụng
corpus = judgment_tokens
word = "vụ việc"
sentence = "vụ việc ly hôn "
bm25_score = calculate_bm25(word, sentence, corpus)
print(f"Trọng số của từ '{word}' trong câu '{sentence}' là: {bm25_score}")