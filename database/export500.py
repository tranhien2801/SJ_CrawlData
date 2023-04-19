import mysql.connector as mariadb
from constant import constant
import requests
from database.createDB import db, cursor
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from datetime import date

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from bs4 import BeautifulSoup

# Open database connection
db_export = mariadb.connect(host=constant.LOCALHOST,
                     port=constant.PORT,
                     user=constant.USER,
                     password=constant.PASSWORD)
# prepare a cursor object using cursor() method
cursor_export = db_export.cursor()

try:
    cursor_export.execute("USE {}".format("court_e500"))
except mariadb.Error as e:
    cursor_export.execute("CREATE DATABASE {}".format("court_e500"))
    db_export.database = "court_e500"


def ifTableNotHaveData(table_name):
    cursor_export.execute("SELECT * FROM {} ".format(table_name))
    record = cursor_export.fetchall()
    if not record:
        return True
    else:
        return False


def createTableCourt():
    create_table_court = """CREATE TABLE IF NOT EXISTS `court` (
                        `uid` int auto_increment primary key comment 'id tòa án',
                        `court_name` varchar(255) not null comment 'tên tòa án', 
                        `court_level` varchar(255) not null comment 'cấp tòa án: cấp tỉnh, cấp huyện, cấp cao, tối cao',
                        `address` varchar(255) comment 'địa chỉ tòa án, tạm chưa có nguồn để crawl')"""
    cursor_export.execute(create_table_court)
    db_export.commit()

    #crawl data for court
    if ifTableNotHaveData("`court`"):
        list = {
            'TAND tối cao': 'TW',
            'TAND cấp cao': 'CW',
            'TAND cấp tỉnh': 'T',
            'TAND cấp huyện': 'H'
        }
        for level in list:
            form_data = {
                '__VIEWSTATE':
                '/wEPDwUINTY1NjQ1NjMPFgIeE1ZhbGlkYXRlUmVxdWVzdE1vZGUCARYCZg9kFgYCAw8WAh4EVGV4dAXHAjxsaSBjbGFzcz0nJz48YSBocmVmPScvJz48c3Ryb25nPlRyYW5nIGNo4bunPC9zdHJvbmc+PC9hPjwvbGk+PGxpIGNsYXNzPScnPjxhIGhyZWY9Jy8xdGF0Y3ZuL2dpb2ktdGhpZXUnPjxzdHJvbmc+R2nhu5tpIHRoaeG7h3U8L3N0cm9uZz48L2E+PC9saT48bGkgY2xhc3M9Jyc+PGEgaHJlZj0nLzB0YXQxY3ZuL2Jhbi1hbi1xdXlldC1kaW5oJz48c3Ryb25nPkLhuqNuIMOhbiAtIHF1eeG6v3QgxJHhu4tuaDwvc3Ryb25nPjwvYT48L2xpPjxsaSBjbGFzcz0nJz48YSBocmVmPScvNnRhdGN2bi9UaG9uZy1rZSc+PHN0cm9uZz5UaOG7kW5nIGvDqjwvc3Ryb25nPjwvYT48L2xpPmQCBQ9kFgICBQ9kFgICAQ9kFgJmD2QWAmYPZBYCZg9kFgQCAw8WAh4Fc3R5bGUFDmRpc3BsYXk6YmxvY2s7FhQCAw8QZGQWAWZkAgUPEA8WAh4LXyFEYXRhQm91bmRnZBAVARAtLS0tLWNo4buNbi0tLS0tFQEAFCsDAWcWAWZkAgcPEGRkFgBkAgkPEGRkFgFmZAILDxAPFgIfA2dkEBUJEC0tLS0tY2jhu41uLS0tLS0KSMOsbmggc+G7sQlEw6JuIHPhu7EZSMO0biBuaMOibiB2w6AgZ2lhIMSRw6xuaBlLaW5oIGRvYW5oIHRoxrDGoW5nIG3huqFpDEjDoG5oIGNow61uaAtMYW8gxJHhu5luZyZRdXnhur90IMSR4buLbmggdHV5w6puIGLhu5EgcGjDoSBz4bqjbj1RdXnhur90IMSR4buLbmggw6FwIGThu6VuZyBiaeG7h24gcGjDoXAgeOG7rSBsw70gaMOgbmggY2jDrW5oFQkAAjUwATABMQEyATQBMwE1AjExFCsDCWdnZ2dnZ2dnZxYBZmQCDQ8QZGQWAGQCDw8PFgIeCU1heExlbmd0aGZkZAITDxYIHgxEaXNwbGF5TW9uZXkLKX9BamF4Q29udHJvbFRvb2xraXQuTWFza2VkRWRpdFNob3dTeW1ib2wsIEFqYXhDb250cm9sVG9vbGtpdCwgVmVyc2lvbj0yMC4xLjAuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj0yOGYwMWIwZTg0YjZkNTNlAB4OQWNjZXB0TmVnYXRpdmULKwQAHg5JbnB1dERpcmVjdGlvbgspgwFBamF4Q29udHJvbFRvb2xraXQuTWFza2VkRWRpdElucHV0RGlyZWN0aW9uLCBBamF4Q29udHJvbFRvb2xraXQsIFZlcnNpb249MjAuMS4wLjAsIEN1bHR1cmU9bmV1dHJhbCwgUHVibGljS2V5VG9rZW49MjhmMDFiMGU4NGI2ZDUzZQAeCkFjY2VwdEFtUG1oZAIVDw8WAh8EZmRkAhkPFggfBQsrBAAfBgsrBAAfBwsrBQAfCGhkAgUPFgIfAgUNZGlzcGxheTpub25lOxYWAgMPEGRkFgFmZAIFDxAPFgIfA2dkEBUBEC0tLS0tY2jhu41uLS0tLS0VAQAUKwMBZxYBZmQCBw8QZGQWAGQCCQ8QZGQWAWZkAgsPEA8WAh8DZ2QQFQkQLS0tLS1jaOG7jW4tLS0tLQpIw6xuaCBz4buxCUTDom4gc+G7sRlIw7RuIG5ow6JuIHbDoCBnaWEgxJHDrG5oGUtpbmggZG9hbmggdGjGsMahbmcgbeG6oWkMSMOgbmggY2jDrW5oC0xhbyDEkeG7mW5nJlF1eeG6v3QgxJHhu4tuaCB0dXnDqm4gYuG7kSBwaMOhIHPhuqNuPVF1eeG6v3QgxJHhu4tuaCDDoXAgZOG7pW5nIGJp4buHbiBwaMOhcCB44butIGzDvSBow6BuaCBjaMOtbmgVCQACNTABMAExATIBNAEzATUCMTEUKwMJZ2dnZ2dnZ2dnFgFmZAIPDw8WAh8EZmRkAhMPFggfBQsrBAAfBgsrBAAfBwsrBQAfCGhkAhUPDxYCHwRmZGQCGQ8WCB8FCysEAB8GCysEAB8HCysFAB8IaGQCJQ8WAh8BZWQCLQ8QZGQWAWZkAgcPZBYGAgEPFgIfAQVRPGgyIGNsYXNzPSd0aW1lciBjb3VudC10aXRsZSBjb3VudC1udW1iZXInIGRhdGEtdG89JzY5NzYnIGRhdGEtc3BlZWQ9JzE1MDAnPjwvaDI+ZAIDDxYCHwEFUjxoMiBjbGFzcz0ndGltZXIgY291bnQtdGl0bGUgY291bnQtbnVtYmVyJyBkYXRhLXRvPSc0MDcwMycgZGF0YS1zcGVlZD0nMTUwMCc+PC9oMj5kAgUPFgIfAQVWPGgyIGNsYXNzPSd0aW1lciBjb3VudC10aXRsZSBjb3VudC1udW1iZXInIGRhdGEtdG89JzE1NDI3MjExNCcgZGF0YS1zcGVlZD0nMTUwMCc+PC9oMj5kGAEFHl9fQ29udHJvbHNSZXF1aXJlUG9zdEJhY2tLZXlfXxYEBS5jdGwwMCRDb250ZW50X2hvbWVfUHVibGljJGN0bDAwJGNoZWNrX2FubGVfdG9wBTRjdGwwMCRDb250ZW50X2hvbWVfUHVibGljJGN0bDAwJGNoZWNrX2FubGVfdm90ZWRfdG9wBSpjdGwwMCRDb250ZW50X2hvbWVfUHVibGljJGN0bDAwJGNoZWNrX2FubGUFMGN0bDAwJENvbnRlbnRfaG9tZV9QdWJsaWMkY3RsMDAkY2hlY2tfYW5sZV92b3RlZB3HS2dlt+y+OtzkAA3zAagRyR0kA++1qnStzle6Ielk',
                'ctl00$Content_home_Public$ctl00$Drop_Levels_top': list[level]
            }
            response = requests.post(constant.URL_SEARCH,
                                     data=form_data,
                                     verify=False).content
            bs = BeautifulSoup(response, 'html.parser')
            list_court = bs.find(
                'select',
                id='ctl00_Content_home_Public_ctl00_Ra_Drop_Courts_top'
            ).find_all('option')
            
            today = date.today()
            for c in list_court:
                court = c.get_text().strip()
                if court != "-----chọn-----":
                    insert_court = "INSERT INTO `court` (uid, court_name, court_level, created) VALUES (UUID_TO_BIN(UUID()),%s, %s, %s)"
                    cursor_export.execute(insert_court, (court, level, today))
                    db_export.commit()

    print("create table court")


def createTableCase():
    create_table_case = """CREATE TABLE IF NOT EXISTS `case` (
                        `uid` int auto_increment primary key comment 'id vụ việc',
                        `case_name` varchar(555) not null comment 'tên vụ việc: tội danh,quan hệ pháp luật,...',
                        `case_type` varchar(255) not null comment 'loại vụ việc: hình sự, dân sự,...',
                        `num_article` varchar(10) comment 'điều thứ mấy trong bộ luật hình sự, chỉ có ở bộ luật hình sự' ) """
    cursor_export.execute(create_table_case)
    db_export.commit()

    #crawl data for case
    if ifTableNotHaveData("`case`"):
        list = {
            "Hình sự": 50,
            "Dân sự": 0,
            "Hôn nhân và gia đình": 1,
            "Kinh doanh thương mại": 2,
            "Hành chính": 4,
            "Lao động": 3,
            "Quyết định tuyên bố phá sản": 5,
            "Quyết định áp dụng biện pháp xử lý hành chính": 11
        }
        for case in list:
            form_data = {
                '__VIEWSTATE':
                '/wEPDwUINTY1NjQ1NjMPFgIeE1ZhbGlkYXRlUmVxdWVzdE1vZGUCARYCZg9kFgYCAw8WAh4EVGV4dAXHAjxsaSBjbGFzcz0nJz48YSBocmVmPScvJz48c3Ryb25nPlRyYW5nIGNo4bunPC9zdHJvbmc+PC9hPjwvbGk+PGxpIGNsYXNzPScnPjxhIGhyZWY9Jy8xdGF0Y3ZuL2dpb2ktdGhpZXUnPjxzdHJvbmc+R2nhu5tpIHRoaeG7h3U8L3N0cm9uZz48L2E+PC9saT48bGkgY2xhc3M9Jyc+PGEgaHJlZj0nLzB0YXQxY3ZuL2Jhbi1hbi1xdXlldC1kaW5oJz48c3Ryb25nPkLhuqNuIMOhbiAtIHF1eeG6v3QgxJHhu4tuaDwvc3Ryb25nPjwvYT48L2xpPjxsaSBjbGFzcz0nJz48YSBocmVmPScvNnRhdGN2bi9UaG9uZy1rZSc+PHN0cm9uZz5UaOG7kW5nIGvDqjwvc3Ryb25nPjwvYT48L2xpPmQCBQ9kFgICBQ9kFgICAQ9kFgJmD2QWAmYPZBYCZg9kFgQCAw8WAh4Fc3R5bGUFDmRpc3BsYXk6YmxvY2s7FhQCAw8QZGQWAWZkAgUPEA8WAh4LXyFEYXRhQm91bmRnZBAVARAtLS0tLWNo4buNbi0tLS0tFQEAFCsDAWcWAWZkAgcPEGRkFgBkAgkPEGRkFgFmZAILDxAPFgIfA2dkEBUJEC0tLS0tY2jhu41uLS0tLS0KSMOsbmggc+G7sQlEw6JuIHPhu7EZSMO0biBuaMOibiB2w6AgZ2lhIMSRw6xuaBlLaW5oIGRvYW5oIHRoxrDGoW5nIG3huqFpDEjDoG5oIGNow61uaAtMYW8gxJHhu5luZyZRdXnhur90IMSR4buLbmggdHV5w6puIGLhu5EgcGjDoSBz4bqjbj1RdXnhur90IMSR4buLbmggw6FwIGThu6VuZyBiaeG7h24gcGjDoXAgeOG7rSBsw70gaMOgbmggY2jDrW5oFQkAAjUwATABMQEyATQBMwE1AjExFCsDCWdnZ2dnZ2dnZxYBZmQCDQ8QZGQWAGQCDw8PFgIeCU1heExlbmd0aGZkZAITDxYIHgxEaXNwbGF5TW9uZXkLKX9BamF4Q29udHJvbFRvb2xraXQuTWFza2VkRWRpdFNob3dTeW1ib2wsIEFqYXhDb250cm9sVG9vbGtpdCwgVmVyc2lvbj0yMC4xLjAuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj0yOGYwMWIwZTg0YjZkNTNlAB4OQWNjZXB0TmVnYXRpdmULKwQAHg5JbnB1dERpcmVjdGlvbgspgwFBamF4Q29udHJvbFRvb2xraXQuTWFza2VkRWRpdElucHV0RGlyZWN0aW9uLCBBamF4Q29udHJvbFRvb2xraXQsIFZlcnNpb249MjAuMS4wLjAsIEN1bHR1cmU9bmV1dHJhbCwgUHVibGljS2V5VG9rZW49MjhmMDFiMGU4NGI2ZDUzZQAeCkFjY2VwdEFtUG1oZAIVDw8WAh8EZmRkAhkPFggfBQsrBAAfBgsrBAAfBwsrBQAfCGhkAgUPFgIfAgUNZGlzcGxheTpub25lOxYWAgMPEGRkFgFmZAIFDxAPFgIfA2dkEBUBEC0tLS0tY2jhu41uLS0tLS0VAQAUKwMBZxYBZmQCBw8QZGQWAGQCCQ8QZGQWAWZkAgsPEA8WAh8DZ2QQFQkQLS0tLS1jaOG7jW4tLS0tLQpIw6xuaCBz4buxCUTDom4gc+G7sRlIw7RuIG5ow6JuIHbDoCBnaWEgxJHDrG5oGUtpbmggZG9hbmggdGjGsMahbmcgbeG6oWkMSMOgbmggY2jDrW5oC0xhbyDEkeG7mW5nJlF1eeG6v3QgxJHhu4tuaCB0dXnDqm4gYuG7kSBwaMOhIHPhuqNuPVF1eeG6v3QgxJHhu4tuaCDDoXAgZOG7pW5nIGJp4buHbiBwaMOhcCB44butIGzDvSBow6BuaCBjaMOtbmgVCQACNTABMAExATIBNAEzATUCMTEUKwMJZ2dnZ2dnZ2dnFgFmZAIPDw8WAh8EZmRkAhMPFggfBQsrBAAfBgsrBAAfBwsrBQAfCGhkAhUPDxYCHwRmZGQCGQ8WCB8FCysEAB8GCysEAB8HCysFAB8IaGQCJQ8WAh8BZWQCLQ8QZGQWAWZkAgcPZBYGAgEPFgIfAQVRPGgyIGNsYXNzPSd0aW1lciBjb3VudC10aXRsZSBjb3VudC1udW1iZXInIGRhdGEtdG89JzY5NzYnIGRhdGEtc3BlZWQ9JzE1MDAnPjwvaDI+ZAIDDxYCHwEFUjxoMiBjbGFzcz0ndGltZXIgY291bnQtdGl0bGUgY291bnQtbnVtYmVyJyBkYXRhLXRvPSc0MDcwMycgZGF0YS1zcGVlZD0nMTUwMCc+PC9oMj5kAgUPFgIfAQVWPGgyIGNsYXNzPSd0aW1lciBjb3VudC10aXRsZSBjb3VudC1udW1iZXInIGRhdGEtdG89JzE1NDI3MjExNCcgZGF0YS1zcGVlZD0nMTUwMCc+PC9oMj5kGAEFHl9fQ29udHJvbHNSZXF1aXJlUG9zdEJhY2tLZXlfXxYEBS5jdGwwMCRDb250ZW50X2hvbWVfUHVibGljJGN0bDAwJGNoZWNrX2FubGVfdG9wBTRjdGwwMCRDb250ZW50X2hvbWVfUHVibGljJGN0bDAwJGNoZWNrX2FubGVfdm90ZWRfdG9wBSpjdGwwMCRDb250ZW50X2hvbWVfUHVibGljJGN0bDAwJGNoZWNrX2FubGUFMGN0bDAwJENvbnRlbnRfaG9tZV9QdWJsaWMkY3RsMDAkY2hlY2tfYW5sZV92b3RlZB3HS2dlt+y+OtzkAA3zAagRyR0kA++1qnStzle6Ielk',
                'ctl00$Content_home_Public$ctl00$Drop_CASES_STYLES_SEARCH_top':
                list[case]
            }
            response = requests.post(constant.URL_SEARCH,
                                     data=form_data,
                                     verify=False).content
            bs = BeautifulSoup(response, 'html.parser')
            list_case_show = bs.find(
                'select',
                id='ctl00_Content_home_Public_ctl00_Ra_Case_shows_search_top'
            ).find_all('option')

            for cs in list_case_show:
                case_show = cs.get_text()
                today = date.today()
                if case_show != "-----chọn-----":
                    if case == "Hình sự":
                        article = case_show[None:case_show.find(".")].strip()
                        case_show = case_show[case_show.find(".") +
                                              1:None].strip()
                    if article != None:
                        insert_case_show = "INSERT INTO `case` (uid, case_name, case_type, num_article, created) VALUES (UUID_TO_BIN(UUID()), %s, %s, %s, %s)"
                        cursor_export.execute(insert_case_show,
                                       (case_show, case, article, today))
                        db_export.commit()
                    else:
                        insert_case = "INSERT INTO `case` (uid, case_name, case_type, created) VALUES (UUID_TO_BIN(UUID()), %s, %s, %s)"
                        cursor_export.execute(insert_case, (case_show, case, today))
                        db_export.commit()

    print("create table case")


def createTableJudgment():
    create_table_judgment = """CREATE TABLE IF NOT EXISTS `judgment` (
                            `uid` int auto_increment primary key comment 'id bản án',
                            `judgment_number` varchar(255) not null comment 'số hiệu bản án',
                            `judgment_name` TEXT(500) not null comment 'tên bản án',
                            `type_document` varchar(255) not null comment 'loại văn bản: bản án/quyết định',
                            `judgment_level` varchar(255) not null comment 'cấp xét xử: ',
                            `court_uid` int not null comment 'id tòa án',
                            `case_uid` int not null comment 'id vụ việc',
                            `judgment_content` LONGTEXT not null comment 'nội dung tóm tắt bản án',
                            `judgment_text` LONGTEXT not null comment 'toàn bộ nội dung bản án từ pdf',
                            `date_issued` date not null comment 'ngày công bố',
                            `date_upload` date not null comment 'ngày đăng lên hệ thống',
                            `url` varchar(255) not null comment 'link bản án',
                            `file_download` varchar(255) not null comment 'link download bản án',
                            `corrections` int comment 'số lượng đính chính',
                            `count_vote` int comment 'số lượng bầu chọn',
                            `count_eyes` int comment'số lượng đã xem',
                            `count_download` int comment 'số lượng tải')"""
    cursor_export.execute(create_table_judgment)
    db_export.commit()
    print("create table judgment")


def loadRow(cursor):
    while True:
        rows = cursor.fetchall()
        if not rows:
            break
        for row in rows:
            yield row
def export():
    for i in range(1, 783):
        cursor.execute("select * from judgment where case_uid = " + str(i) + " limit 1")
        for row in loadRow(cursor):
            try:
                date_issued = row[9]
                date_upload = row[10]
                case_uid = row[6]
                court_uid = row[5]
                judgment_number = row[1]
                judgment_name = row[2]
                type_document = row[3]
                corrections = row[13]
                judgment_content = row[7]
                judgment_text = row[8]
                judgment_level = row[4]
                count_vote = row[14]
                count_eyes = row[15]
                count_download = row[16]
                file_download = row[12]
                url = row[11]

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

                cursor_export.execute(
                    insert_judgment,
                    (judgment_number, judgment_name, type_document, judgment_level,
                    court_uid, case_uid, judgment_content, judgment_text, date_issued,
                    date_upload, url, file_download, corrections, count_vote, count_eyes,
                    count_download, today))
                db_export.commit()

                # print("judgment saved " + str(cursor.lastrowid))
            except BaseException as e:
                print(e)

createTableCourt()
createTableCase()
createTableJudgment()
export()