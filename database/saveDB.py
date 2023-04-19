from database.createDB import cursor, db
import re
from datetime import datetime
from datetime import date
import uuid

def get_all_URL_judgment():
    list_url_jdg = []
    cursor.execute("SELECT url FROM judgment")
    record = cursor.fetchall()
    if not record:
        return list_url_jdg
    else:
        for i in record:
            list_url_jdg.append(i[0])
    return list_url_jdg


def check_jdg_inDB(jdg_url):
    cursor.execute("SELECT * FROM judgment WHERE url LIKE " + '"%' +
                   jdg_url + '%"')
    record = cursor.fetchall()
    if not record: return 0
    else: return record[0][0]


def save_judgment(jdg):
    date_issued = datetime.strptime(jdg['date_issued'], '%d/%m/%Y').date()
    date_upload = datetime.strptime(jdg['date_upload'], '%d.%m.%Y').date()

    select_case = "SELECT * FROM `case` WHERE case_name LIKE " + "'%" + jdg['case_name'] + "%'"
    if jdg['case_type'] == 'Hình sự':
        s = re.findall('[0-9]+', jdg['case_name'][jdg['case_name'].rfind('('):None])
        select_case = "SELECT * FROM `case` WHERE case_name LIKE " + "'%" + s[1] + "%' AND num_article LIKE" + "'" + s[0] + "'"
    cursor.execute(select_case)
    record = cursor.fetchall()
    case_uid = record[0][0]

    foc = jdg['court']
    poc = ""
    if foc.find(",") != -1:
        poc = foc.split(",")[1].strip()
        foc = foc.split(",")[0].strip()
    select_court = "SELECT * FROM `court` WHERE court_name LIKE " + '"%' + foc + '%' + poc + '%"'
    cursor.execute(select_court)
    record = cursor.fetchall()
    court_uid = record[0][0]

    judgment_number = jdg['judgment_number']
    judgment_name = jdg['judgment_name']
    type_document = jdg['type_document']
    corrections = jdg['corrections']
    judgment_content = jdg['judgment_content']
    judgment_text = jdg['judgment_text']
    judgment_level = jdg['judgment_level']
    count_vote = jdg['count_vote']
    count_eyes = jdg['count_eyes']
    count_download = jdg['count_download']
    file_download = jdg['file_download']
    url = jdg['url']
    pdf_viewer = jdg['pdf_viewer']
    precedent = jdg['precedent']
    uid = str(uuid.uuid4()).replace("-", "")

    insert_judgment = '''INSERT INTO `judgment` (uid,
                                                judgment_number, 
                                                judgment_name,
                                                type_document,
                                                judgment_level,
                                                court_uid,
                                                case_uid,
                                                judgment_content,
                                                judgment_text,
                                                date_issued,
                                                date_upload,
                                                url,
                                                pdf_viewer,
                                                file_download,
                                                corrections,
                                                count_vote,
                                                count_eyes,
                                                count_download,
                                                precedent,
                                                created) 
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
    today = date.today()
    cursor.execute(
        insert_judgment,
        (uid, judgment_number, judgment_name, type_document, judgment_level,
         court_uid, case_uid, judgment_content, judgment_text, date_issued,
         date_upload, url, pdf_viewer, file_download, corrections, count_vote, count_eyes, count_download, precedent, today))
    db.commit()

    # print("judgment saved " + str(cursor.lastrowid))
