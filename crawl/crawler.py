from tokenize import String
import requests, time, os, re
from bs4 import BeautifulSoup
from database import saveDB
from constant import constant
from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams
import calendar
import fitz, textract, pikepdf

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Call api to search data from date_from to date_to
def getSearchResult(url_search, date_from, date_to):
    form_data = {
        '__VIEWSTATE':"",
        'ctl00$Content_home_Public$ctl00$Rad_DATE_TO_top': date_to ,
        'ctl00$Content_home_Public$ctl00$Rad_DATE_FROM_top' : date_from,
        'ctl00$Content_home_Public$ctl00$cmd_search_banner':'Tìm kiếm'}

    response = requests.post(constant.URL_SEARCH, data=form_data, verify=False).content
    soup = BeautifulSoup(response, 'html.parser')

    min_page = 1
    max_page = int(soup.find('div', class_='Page_Number').find('span', id='ctl00_Content_home_Public_ctl00_LbShowtotal').text)
    view_state = soup.find('input', id='__VIEWSTATE')['value']

    result = {
      "min_page": min_page,
      "max_page": max_page,
      "view_state": view_state
    }
    return result


# Function download and get text from file PDF
def get_text_PDF(link_download):
    r = requests.get(link_download, timeout=120, verify=False)
    id = link_download[34:None].replace('/', '-').replace('?', '-').replace(
        '<', '-').replace('>', '-').replace('|', '-').replace('*', '-')
    file = constant.ABSOLUTEPATH + id
    with open(file, 'wb') as w:
        w.write(r.content)
        w.close()
    text = ""
    try:
        with fitz.open(file) as pdf:
            for page in range(pdf.page_count):
                text += pdf.load_page(page).get_text()
    except BaseException as e:
        text = "secured, can not extract text"

    os.remove(file) #delete file
    return text


# Function crawl judgment
def crawl_judgment(url):
    res = None
    Flag_time_out = True
    while Flag_time_out == True:
        try:
            res = requests.get(url, timeout=120, verify=False)
            if res.status_code == constant.SUCCESSFUL_RESPONSE or res.status_code == constant.INTERNAL_SERVER_RESPONSE:
                Flag_time_out = False
        except:
            time.sleep(constant.CALL_BACK_WAIT_TIME_FOR_1_JUDGMENT)
            print("waiting for {} seconds".format(String(constant.CALL_BACK_WAIT_TIME_FOR_1_JUDGMENT)), url)

    s = BeautifulSoup(res.content, 'html.parser')

    if s.find('div', class_='search_left_pub details_pub') == None:
        return None

    judgment_pdf = s.find('iframe')['src']
    judgment_pdf = constant.BASE_URL + judgment_pdf

    judgment = s.find('div', class_='search_left_pub details_pub')

    judgment_header = judgment.find(
        'div', class_='panel-heading').find('span').text.strip()
    cut = judgment_header.rfind('ngày')
    judgment_number = judgment_header[0:cut]  #số hiệu
    judgment_number = judgment_number[judgment_number.find(':') +
                                      1:judgment_number.find('ngày')].strip()
    date_issued = judgment_header[cut + 5:None].strip()  #ngày ban hành

    document = judgment.find(
        'div', class_='panel-heading').find('label').text.strip()
    document = document[0:len(document) - 4]  # bản án / quyết định

    count_pub = judgment.find('ul', class_='list_count_pub').find_all('li')
    for li in count_pub:
        if li.find('i', class_='fa fa-eye'):
            if li.get_text() == ' ':
                count_eye = 0  #lượt xem
            else:
                count_eye = int(li.get_text())
        else:
            if li.get_text() == ' ':
                count_download = 0  #lượt tải
            else:
                count_download = int(li.get_text())

    list_group = judgment.find('ul', class_="list-group").find_all('li')
    for li in list_group:
        if li.find('label') != None and li.find('label').text.strip().find(
                'Tên') != -1:
            try:
                date_upload = li.find('span').find(
                    'time').get_text().strip()  #ngày upload
                date_upload = date_upload[1:len(date_upload) - 1]  #bỏ 2 dấu ()
            except:
                date_upload = date.today().strftime("%d.%m.%Y")

            judgment_name = li.find('span').get_text().strip()
            judgment_name = judgment_name[None:len(judgment_name) -
                                          12]  #tên bản án
        elif li.find('label') != None and li.find('label').text.strip().find(
                'Quan hệ pháp luật') != -1:
            case_name = li.find('span').get_text().strip()  #quan hệ pháp luật
        elif li.find('label') != None and li.find('label').text.strip().find(
                'Đối tượng khởi kiện') != -1:
            case_name = li.find(
                'span').get_text().strip()  #Đối tượng khởi kiện
        elif li.find('label') != None and li.find('label').text.strip().find(
                'Đối tượng bị yêu cầu') != -1:
            case_name = li.find(
                'span').get_text().strip()  #Đối tượng bị yêu cầu
        elif li.find('label') != None and li.find('label').text.strip().find(
                'Biện pháp xử lý') != -1:
            case_name = li.find(
                'span').get_text().strip()  #Biện pháp xử lý hành chính
        elif li.find('label') != None and li.find('label').text.strip().find(
                'Cấp xét xử') != -1:
            judgment_level = li.find('span').get_text().strip()  #cấp xét xử
        elif li.find('label') != None and li.find('label').text.strip().find(
                'Loại') != -1:
            case_type = li.find('span').get_text().strip()  #loại vụ việc
        elif li.find('label') != None and li.find('label').text.strip().find(
                'Tòa án xét xử') != -1:
            court = li.find('span').get_text().strip()  #tòa án xét xử
        elif li.find('label') != None and li.find('label').text.strip().find(
                'Áp dụng án lệ') != -1:
            precedent = li.find('span').get_text().strip()  #áp dụng án lệ
            if precedent.find('Không') != -1:
                precedent = 0
            else:
                precedent = 1
                print(precedent)

        elif li.find('label') != None and li.find('label').text.strip().find(
                'Đính chính') != -1:
            corrections = int(li.find('span').get_text().strip())  #đính chính
        elif li.find('label') != None and li.find('label').text.strip().find(
                'Thông tin') != -1:
            judgment_content = li.find(
                'span').get_text().strip()  #thông tin sự việc
        else:
            count_vote = int(
                li.find('span').find('strong').text.strip().split(': ')
                [1])  # bÌnh chọn phát triển

    if case_type == "Hình sự":
        case_name = judgment_name[judgment_name.rfind('-') +
                                  1:None].strip()  #phạm tội
        if case_name.find('phạm tội') != -1:
            case_name = "Tội " + case_name[case_name.find('phạm tội') +
                                           9:None].strip(
                                           )  # xử lí cho 1 vài ngoại lệ
        else:
            case_name = "Tội " + case_name[case_name.find('tội') +
                                           4:None].strip()
        judgment_name = judgment_name[None:judgment_name.rfind('-') -
                                      1].strip()

    judgment_text = ""
    link_download = ""
    if s.find('div', class_='tab-pane', id='2b').find(
            'div', class_='btn_set_color') != None:
        file_download = s.find('div', class_='tab-pane', id='2b').find(
            'div', class_='btn_set_color').find('a')['href']  #link download
        if file_download != None:
            link_download = "https://congbobanan.toaan.gov.vn" + file_download
            judgment_text = get_text_PDF(link_download)
        else:
            judgment_text = "do not have content"

    jdg = {
        'judgment_number': judgment_number,
        'date_issued': date_issued,
        'date_upload': date_upload,
        'type_document': document,
        'judgment_name': judgment_name,
        'case_name': case_name,
        'judgment_level': judgment_level,
        'case_type': case_type,
        'court': court,
        'corrections': corrections,
        'judgment_content': judgment_content,
        'judgment_text': judgment_text,
        'count_vote': count_vote,
        'count_eyes': count_eye,
        'count_download': count_download,
        'file_download': link_download,
        'precedent': precedent,
        'url': url,
        'pdf_viewer': judgment_pdf
    }
    return jdg
