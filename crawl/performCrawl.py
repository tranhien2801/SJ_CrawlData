from constant import constant
from database import saveDB
from crawl import crawler
from datetime import date, datetime, timedelta
from threading import Thread
import time, calendar
import requests
from bs4 import BeautifulSoup

global list_url_judgment
new_judgment = []
THREAD_FLAG = True

def runCrawl(start, total_page, date_from, date_to, view_state):
    # function crawl and save to list
    def loadJudgment(url_detail_judgment):
        global new_judgment

        jdg = crawler.crawl_judgment(url_detail_judgment)

        if jdg == None:
            return
        else:
            new_judgment.append(jdg)

    # function load all page of search result
    def loadPage(page):
        form_data = {
          'ctl00$Content_home_Public$ctl00$Rad_DATE_TO': date_to,
          'ctl00$Content_home_Public$ctl00$Rad_DATE_FROM': date_from,
          'ctl00$Content_home_Public$ctl00$DropPages': page,
          '__VIEWSTATE': view_state
          }
        response = None
        Flag_time_out = True

        while Flag_time_out == True:
            try:
                response = requests.post(constant.URL_SEARCH, data=form_data, timeout=120, verify=False)
                if response.status_code == constant.SUCCESSFUL_RESPONSE:
                    Flag_time_out = False
            except:
                with open(constant.ABSOLUTEPATH+'exception.txt', 'a', encoding="utf-8") as wf:
                    wf.write(str(datetime.now()) + " sleeping..." + "\n")
                    wf.write(str(page)+"\n"+str(total_page)+"\n"+str(date_from)+"\n"+str(date_to))
                    wf.close()
                time.sleep(constant.CALL_BACK_WAIT_TIME_FOR_1_PAGE)

        soup = BeautifulSoup(response.content, 'html.parser')

        records = soup.find_all('div', class_='list-group-item')
        # print(len(records))
        global list_url_judgment

        for record in records:
            detail_judgment = record.find('a', class_='echo_id_pub')
            url_detail_judgment = "https://congbobanan.toaan.gov.vn" + detail_judgment['href']

            if url_detail_judgment in list_url_judgment:
                print("haved in db " + url_detail_judgment)
                continue
            else:
                loadJudgment(url_detail_judgment)


    #function catch Exception and stop thread
    def load(page):
        global THREAD_FLAG
        st = time.time()
        try:
            loadPage(page)
            with open(constant.ABSOLUTEPATH+'log.txt', 'w', encoding="utf-8") as wf:
                wf.write(str(datetime.now())+"\n"+str(page)+"\n"+str(total_page)+"\n"+str(date_from)+"\n"+str(date_to))
                wf.close()
        except BaseException as e:
            print("Error: " + str(e))
            with open(constant.ABSOLUTEPATH+'exception.txt', 'a', encoding="utf-8") as wf:
                wf.write(str(datetime.now()) + " Error: " + str(e) + "\n")
                wf.write(str(page)+"\n"+str(total_page)+"\n"+str(date_from)+"\n"+str(date_to))
                wf.close()
            # THREAD_FLAG = False

        fn = time.time()
        print("done: " + str(page) + ": " + str(fn-st) + "--" + str(THREAD_FLAG))

    #function start threads
    def doingThread():
        page = start
        global new_judgment
        while page <= total_page and THREAD_FLAG==True:
            threads = []
            new_judgment.clear()

            st = time.time()

            for t in range(constant.NUMBER_THREAD):
                if page <= total_page:
                    th = Thread(target=load, args=(page,))
                    page+=1
                    th.start()
                    threads.append(th)

            #wait fo all thread done
            for t in threads:
                t.join()

            fn = time.time()

            print(len(new_judgment), fn-st)

            for jdg in new_judgment:
                try:
                    saveDB.save_judgment(jdg)

                    d = datetime.strptime(jdg['date_issued'], '%d/%m/%Y').date().year
                    if d<2000 or d>datetime.today().year:
                        with open(constant.ABSOLUTEPATH+'exception.txt', 'a', encoding="utf-8") as wf:
                            wf.write(jdg['url'] + " --- " + "error date_issued" + "\n")
                            wf.close()

                except BaseException as e:
                    print(str(e) + jdg['url'])
                    with open(constant.ABSOLUTEPATH+'exception.txt', 'a', encoding="utf-8") as wf:
                        wf.write(jdg['url'] + " --- " + str(e) + "\n")
                        wf.close()

    #main handle
    def mainHandle():
        global list_url_judgment
        list_url_judgment= set(saveDB.get_all_URL_judgment())
        doingThread()

    mainHandle()


# function run for a period of time
def funcMain(date_from, date_to):
    result = crawler.getSearchResult(constant.URL_SEARCH, date_from, date_to)
    page_start = 1
    total_page = result['max_page']
    view_state = result['view_state']
    print(page_start, total_page, date_from, date_to)
    runCrawl(page_start, total_page, date_from, date_to, view_state)

#function restart for a period of time
def funcRestart(page_start, total_page, date_from, date_to):
    result = crawler.getSearchResult(constant.URL_SEARCH, date_from, date_to)
    total_page = result['max_page']
    view_state = result['view_state']

    runCrawl(page_start, total_page, date_from, date_to, view_state)

#function run for 1 year
def funcRunOverYearS(s_month, t_year):
    for t_month in range(s_month, 13):
        date_from = date(t_year, t_month, 1).strftime("%d/%m/%Y")
        date_to = date(t_year, t_month, calendar.monthrange(t_year, t_month)[1]).strftime("%d/%m/%Y")

        funcMain(date_from, date_to)

#function restart for 1 year
def funcRestartOverYear(page_start, total_page, date_from, date_to):
    funcRestart(page_start, total_page, date_from, date_to)

    s_month = datetime.strptime(date_from, '%d/%m/%Y').date().month
    t_year = datetime.strptime(date_from, '%d/%m/%Y').date().year

    funcOverYear(s_month+1, t_year)
