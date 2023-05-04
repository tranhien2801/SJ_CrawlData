from transformers import T5ForConditionalGeneration, T5Tokenizer
import torch
from flask import request
from database.createDB import cursor, db

cursor = db.cursor(dictionary=True)

# --------------------------------------------Phần xử lý tóm tắt bản án------------------------------------
if torch.cuda.is_available():       
    device = torch.device("cuda")
    print('There are %d GPU(s) available.' % torch.cuda.device_count())
    print('We will use the GPU:', torch.cuda.get_device_name(0))
else:
    print('No GPU available, using the CPU instead.')
    device = torch.device("cpu")
    
model = T5ForConditionalGeneration.from_pretrained("NlpHUST/t5-small-vi-summarization")
tokenizer = T5Tokenizer.from_pretrained("NlpHUST/t5-small-vi-summarization")
model.to(device)

print("Start summarize...")

def summarize():
    uid = request.args.get('uid', type=str)
    query = "SELECT judgment_text FROM court.judgment WHERE uid = %s"
    cursor.execute(query, (uid,))
    judgment = cursor.fetchall()
    src = judgment[0]['judgment_text']
    
    start = src.find("NỘI DUNG VỤ ÁN")
    end = src.find("NHẬN ĐỊNH CỦA TÒA ÁN")
    if start == -1:
        start = src.find("XÉT THẤY")
        end = src.find("QUYẾT ĐỊNH:")
        print(start)
    if start != -1 and end != -1:
        text = src[start:end]
    else: text = src[1000:10000]
    
    tokenized_text = tokenizer.encode(text, return_tensors="pt").to(device)
    model.eval()
    summary_ids = model.generate(tokenized_text,
                    max_length=512, 
                    num_beams=10,
                    repetition_penalty=2.5, 
                    length_penalty=2.0, 
                    early_stopping=True
                    )
    output = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    query = "UPDATE court.judgment SET judgment_summarization = %s WHERE uid = %s;"
    cursor.execute(query, (output, uid))
    db.commit()
    print("Lưu tóm tắt vào DB....")
       
    return output

   