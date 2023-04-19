import mysql.connector as mysql
from constant import constant
from database.createDB import db, cursor
from crawl import crawler
from datetime import date

# Open database connection
mysql_db = mysql.connect(host=constant.LOCALHOST,
                     port=3306,
                     user=constant.USER,
                     password=constant.PASSWORD,
                     database = 'court')
# prepare a cursor object using cursor() method
mysql_cursor = mysql_db.cursor()

def loadRow(cursor):
    while True:
        rows = cursor.fetchall()
        if not rows:
            break
        for row in rows:
            yield row

def saveJudgment(jdg):
    date_issued = jdg['date_issued']
    date_upload = jdg['date_upload']


    case_uid = jdg['case_uid']

    court_uid = jdg['court_uid']


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
                                                file_download,
                                                corrections,
                                                count_vote,
                                                count_eyes,
                                                count_download,
                                                created) 
                      VALUES (UUID_TO_BIN(UUID()), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
    today = date.today()
    cursor.execute(
        insert_judgment,
        (judgment_number, judgment_name, type_document, judgment_level,
         court_uid, case_uid, judgment_content, judgment_text, date_issued,
         date_upload, url, file_download, corrections, count_vote, count_eyes,
         count_download, today))
    db.commit()

    # print("judgment saved " + str(cursor.lastrowid))

def loadJudgment():
    for i in range(1, 783):
        mysql_cursor.execute(
            "select * from `judgment` where case_show_uid = " + str(i) + " limit 1")

        for row in loadRow(mysql_cursor):
            try:
                judgment_number = row[1]
                date_issued = row[2]
                date_upload = row[3]

                type_document = "Bản án"
                if row[4] == 2: type_document = "Quyết định"

                judgment_name = row[5]

                judgment_level = "Sơ thẩm"
                if row[6] == 2: judgment_level = "Phúc thẩm"
                elif row[6] == 3: judgment_level = "Giám đốc thẩm"
                elif row[6] == 4: judgment_level = "Tái thẩm"

                case_uid = row[7]
                court_uid = row[8]

                corrections = row[10]

                judgment_content = row[11]

                count_vote = row[12]
                count_eyes = row[13]
                count_download = row[14]

                link_download = row[15]
                url = row[16]

                judgment_text = "do not have content"
                if link_download != "":
                    judgment_text = crawler.get_text_PDF(link_download)

                jdg = {
                    'uid': '',
                    'judgment_number': judgment_number,
                    'date_issued': date_issued,
                    'date_upload': date_upload,
                    'type_document': type_document,
                    'judgment_name': judgment_name,
                    'case_uid': case_uid,
                    'judgment_level': judgment_level,
                    'court_uid': court_uid,
                    'corrections': corrections,
                    'judgment_content': judgment_content,
                    'judgment_text': judgment_text,
                    'count_vote': count_vote,
                    'count_eyes': count_eyes,
                    'count_download': count_download,
                    'file_download': link_download,
                    'url': url
                }

                saveJudgment(jdg)
            except BaseException as e:
                print(e)
