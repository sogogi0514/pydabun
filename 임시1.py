import os.path

import bs4
import requests
import json
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd
from bs4 import BeautifulSoup

# https://n.news.naver.com/article/025/0003400318?ntype=RANKING
# "YTN : num_ = '0001644604' # 2021 12 29 NEW'0001668339'
num_ = "3843147"
# num_에 해당하는 기사를 기준으로 과거에 생성된 기사들을 수집!
news_company = "023"  # 한경 ㅣ 015 매경 : 009 YTN : 052
target_num = int(num_)
reply_all_l = []
reply_all_index_l = []
title_l = []
gender_male_l = []
gender_female_l = []
ages_group_10_l = []
ages_group_20_l = []
ages_group_30_l = []
ages_group_40_l = []
ages_group_50_l = []
ages_group_60_l = []
crawl_time_l = []
reply_cnt_l = []
news_id_l = []
mode = 0


def gogo_reply(url_ori, referer, news_id):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15',
        'Referer': referer}

    req = requests.get(referer, headers=headers)
    soup = BeautifulSoup(req.text, 'html.parser')
    title = soup.find('title').text
    

    url_news = url_ori
    req = requests.get(url_news, headers=headers)
    reply_json = json.loads(req.text[req.text.find('{'):-2])

    ## 성별 통계정보 가져오기
    gender_male = reply_json['result']['graph']['gender']['male']
    gender_female = reply_json['result']['graph']['gender']['female']

    ## 연령 통게정보 가져오기
    ages_group_10 = reply_json['result']['graph']['old'][0]['value']
    ages_group_20 = reply_json['result']['graph']['old'][1]['value']
    ages_group_30 = reply_json['result']['graph']['old'][2]['value']
    ages_group_40 = reply_json['result']['graph']['old'][3]['value']
    ages_group_50 = reply_json['result']['graph']['old'][4]['value']
    ages_group_60 = reply_json['result']['graph']['old'][5]['value']
    global a, b, c, d, e, f
    a = ages_group_10
    b = ages_group_20
    c = ages_group_30
    d = ages_group_40
    e = ages_group_50
    f = ages_group_60

    ## 모든 댓글을 쌓을 reply_l 리스트 만들기
    reply_l = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15',
        'Referer': url_news}
    return gender_male, gender_female, ages_group_10, ages_group_20, ages_group_30, ages_group_40, ages_group_50, ages_group_60, reply_l, title


## 이번 코드는 2만개의 댓그이 모일때 까지 수집을 진행합니다.
i = 0


def make100():
    global a, b, c, d, e, f  # 전역 변수 사용을 선언합니다.

    # 변수들의 값과 변수명을 튜플로 묶어 리스트를 생성
    values = [('a', a + b), ('b', b), ('c', c), ('d', d), ('e', e)]

    # 가장 큰 값을 가진 튜플을 찾음
    max_var, max_value = max(values, key=lambda x: x[1])
    if (a + b + c + d + e + f == 101):
        # 가장 큰 값을 가진 변수를 1 감소시킴
        if max_var == 'a':
            a -= 1
        elif max_var == 'c':
            c -= 1
        elif max_var == 'd':
            d -= 1
        elif max_var == 'e':
            e -= 1
        elif max_var == 'f':
            f -= 1;
    elif (a + b + c + d + e + f == 99):
        if max_var == 'a':
            a += 1
        elif max_var == 'c':
            c += 1
        elif max_var == 'd':
            d += 1
        elif max_var == 'e':
            e += 1
        elif max_var == 'f':
            f += 1;
        else:
            print("100");


def filesave_decision():
    global a, b, c, d, e, f
    if (a + b >= 40):
        return "1020"
    elif (c >= 40):
        return "30"
    elif (d >= 40):
        return "40"
    elif (e >= 40):
        return "50"
    elif (f >= 40):
        return "60"
    else:
        return "etc"


def getAge():
    global num_
    global target_num;
    global mode
    global ages_group_10, ages_group_20, ages_group_30, ages_group_40, ages_group_50, ages_group_60
    global news_company
    global url
    # Naver 서버에 부하를 줄이기 위해 0.1초씩 쉬어가기
    time.sleep(0.1)
    print('.')

    ## gogo_reply에 넣을 인자 만들기
    num_ = '0' * (10 - len(str(target_num))) + str(target_num)
    news_id = "news" + news_company + "," + num_
    # https://n.news.naver.com/article/comment/015/0005056755

    referer = "https://news.naver.com/main/read.naver?oid=" + news_company + "&aid=" + num_
    url_ori = 'https://apis.naver.com/commentBox/cbox/web_naver_list_jsonp.json?ticket=news&templateId=view_society&pool=cbox5&_wr&_callback=jQuery11240673401066245984_1638166575411&lang=ko&country=KR&objectId=' + news_id + '&categoryId=&pageSize=10&indexSize=10&groupId=&listType=OBJECT&pageType=more&page=1&initialize=true&userType=&useAltSort=true&replyPageSize=20&sort=favorite&includeAllStatus=true&_=1638166575413'
    # https://n.news.naver.com/article/366/0001031072?cds=news_media_pc
    ## 통계정보가 생성되지 않을경우에는 skip되며
    ## try: 에 에러가 안난경우는 통계정보가 생성된(댓글이 일정수준 이상 달린) 댓글입니다
    if (mode == 0):
        print("모드 선택, A:자동, M:수동으로 url넣기")
        mode_selection = input()
        if (mode_selection == "A"):
            print("자동")
            mode = 1
            try:

                ## 함수에서 나온 값을 받아 list에 추가
                gender_male, gender_female, ages_group_10, ages_group_20, ages_group_30, ages_group_40, ages_group_50, ages_group_60, reply_l, title = gogo_reply(
                    url_ori, referer, news_id)
                title_l.append(title)
                gender_male_l.append(gender_male)
                gender_female_l.append(gender_female)
                ages_group_10_l.append(ages_group_10)
                ages_group_20_l.append(ages_group_20)
                ages_group_30_l.append(ages_group_30)
                ages_group_40_l.append(ages_group_40)
                ages_group_50_l.append(ages_group_50)
                ages_group_60_l.append(ages_group_60)
                reply_all_l.append(reply_l)
                crawl_time_l.append(datetime.now().strftime("%Y%m%d-%H%m"))
                reply_cnt_l.append(len(reply_l))
                news_id_l.append(news_id)

                # 변수 List로 dataFrame만들고 저장!
                df = pd.DataFrame()
                df['news_id'] = news_id_l
                df['title'] = title_l
                df['gender_male'] = gender_male_l
                df['gender_female'] = gender_female_l
                df['ages_group_10'] = ages_group_10_l
                df['ages_group_20'] = ages_group_20_l
                df['ages_group_30'] = ages_group_30_l
                df['ages_group_40'] = ages_group_40_l
                df['ages_group_50'] = ages_group_50_l
                df['ages_group_60'] = ages_group_60_l
                df['reply_cnt'] = reply_cnt_l
                df['reply_all'] = reply_all_l
                df['crawl_time'] = crawl_time_l
                ## 저장해주기!!
                df.to_pickle('naver11_')

                # if(mode==1):
                print(len(df), ' ', title, ' Reply num : ', len(reply_l))
                url = 'https://n.news.naver.com/article/comment/' + news_company + '/' + num_
                # https://n.news.naver.com/article/comment/025/0003400318
                print(url);
                print(ages_group_10, ages_group_20, ages_group_30, ages_group_40, ages_group_50, ages_group_60);
                target_num = int(num_) - 1
                num_ = '0' * (10 - len(str(target_num))) + str(target_num)
                print(type(url))
                return url

            # 이만 개의 댓글이 모였다면! 끝!!

            ## 통계정보가 생성되지 않은 뉴스는 pass!
            except KeyError:
                print(num_, news_id, 'pass')
                target_num -= 1;
                num_ = '0' * (10 - len(str(target_num))) + str(target_num);
                return getAge();
        elif (mode_selection == "M"):
            mode = 2
            print("수동 URL 입력:")
            url = input()
            spt_url = url.split('/')
            news_company = spt_url[5]
            num_ = spt_url[6]
            news_id = "news" + news_company + "," + num_

            referer = "https://news.naver.com/main/read.naver?oid=" + news_company + "&aid=" + num_
            url_ori = 'https://apis.naver.com/commentBox/cbox/web_naver_list_jsonp.json?ticket=news&templateId=view_society&pool=cbox5&_wr&_callback=jQuery11240673401066245984_1638166575411&lang=ko&country=KR&objectId=' + news_id + '&categoryId=&pageSize=10&indexSize=10&groupId=&listType=OBJECT&pageType=more&page=1&initialize=true&userType=&useAltSort=true&replyPageSize=20&sort=favorite&includeAllStatus=true&_=1638166575413'
            gender_male, gender_female, ages_group_10, ages_group_20, ages_group_30, ages_group_40, ages_group_50, ages_group_60, reply_l, title = gogo_reply(
                url_ori, referer, news_id)
            title_l.append(title)
            gender_male_l.append(gender_male)
            gender_female_l.append(gender_female)
            ages_group_10_l.append(ages_group_10)
            ages_group_20_l.append(ages_group_20)
            ages_group_30_l.append(ages_group_30)
            ages_group_40_l.append(ages_group_40)
            ages_group_50_l.append(ages_group_50)
            ages_group_60_l.append(ages_group_60)
            reply_all_l.append(reply_l)
            crawl_time_l.append(datetime.now().strftime("%Y%m%d-%H%m"))
            reply_cnt_l.append(len(reply_l))
            news_id_l.append(news_id)

            # 변수 List로 dataFrame만들고 저장!
            df = pd.DataFrame()
            df['news_id'] = news_id_l
            df['title'] = title_l
            df['gender_male'] = gender_male_l
            df['gender_female'] = gender_female_l
            df['ages_group_10'] = ages_group_10_l
            df['ages_group_20'] = ages_group_20_l
            df['ages_group_30'] = ages_group_30_l
            df['ages_group_40'] = ages_group_40_l
            df['ages_group_50'] = ages_group_50_l
            df['ages_group_60'] = ages_group_60_l
            df['reply_cnt'] = reply_cnt_l
            df['reply_all'] = reply_all_l
            df['crawl_time'] = crawl_time_l
            ## 저장해주기!!
            df.to_pickle('naver11_')
            print(type(url))
            return url
    elif (mode == 1):
        try:

            ## 함수에서 나온 값을 받아 list에 추가
            gender_male, gender_female, ages_group_10, ages_group_20, ages_group_30, ages_group_40, ages_group_50, ages_group_60, reply_l, title = gogo_reply(
                url_ori, referer, news_id)
            title_l.append(title)
            gender_male_l.append(gender_male)
            gender_female_l.append(gender_female)
            ages_group_10_l.append(ages_group_10)
            ages_group_20_l.append(ages_group_20)
            ages_group_30_l.append(ages_group_30)
            ages_group_40_l.append(ages_group_40)
            ages_group_50_l.append(ages_group_50)
            ages_group_60_l.append(ages_group_60)
            reply_all_l.append(reply_l)
            crawl_time_l.append(datetime.now().strftime("%Y%m%d-%H%m"))
            reply_cnt_l.append(len(reply_l))
            news_id_l.append(news_id)

            # 변수 List로 dataFrame만들고 저장!
            df = pd.DataFrame()
            df['news_id'] = news_id_l
            df['title'] = title_l
            df['gender_male'] = gender_male_l
            df['gender_female'] = gender_female_l
            df['ages_group_10'] = ages_group_10_l
            df['ages_group_20'] = ages_group_20_l
            df['ages_group_30'] = ages_group_30_l
            df['ages_group_40'] = ages_group_40_l
            df['ages_group_50'] = ages_group_50_l
            df['ages_group_60'] = ages_group_60_l
            df['reply_cnt'] = reply_cnt_l
            df['reply_all'] = reply_all_l
            df['crawl_time'] = crawl_time_l
            ## 저장해주기!!
            df.to_pickle('naver11_')

            # if(mode==1):
            print(len(df), ' ', title, ' Reply num : ', len(reply_l))
            url = 'https://n.news.naver.com/mnews/ranking/article/comment/' + news_company + '/' + num_
            print(url);
            print(ages_group_10, ages_group_20, ages_group_30, ages_group_40, ages_group_50, ages_group_60);
            target_num = int(num_) - 1
            num_ = '0' * (10 - len(str(target_num))) + str(target_num)
            print(type(url))
            return url

            # 이만 개의 댓글이 모였다면! 끝!!

            ## 통계정보가 생성되지 않은 뉴스는 pass!
        except KeyError:
            print(num_, news_id, 'pass')
            target_num -= 1;
            num_ = '0' * (10 - len(str(target_num))) + str(target_num);
            return getAge();
    elif (mode == 2):
        print("수동 URL 입력:")
        url = input()
        spt_url = url.split('/')
        news_company = spt_url[5]
        num_ = spt_url[6]
        news_id = "news" + news_company + "," + num_

        referer = "https://news.naver.com/main/read.naver?oid=" + news_company + "&aid=" + num_
        url_ori = 'https://apis.naver.com/commentBox/cbox/web_naver_list_jsonp.json?ticket=news&templateId=view_society&pool=cbox5&_wr&_callback=jQuery11240673401066245984_1638166575411&lang=ko&country=KR&objectId=' + news_id + '&categoryId=&pageSize=10&indexSize=10&groupId=&listType=OBJECT&pageType=more&page=1&initialize=true&userType=&useAltSort=true&replyPageSize=20&sort=favorite&includeAllStatus=true&_=1638166575413'
        gender_male, gender_female, ages_group_10, ages_group_20, ages_group_30, ages_group_40, ages_group_50, ages_group_60, reply_l, title = gogo_reply(
            url_ori, referer, news_id)
        title_l.append(title)
        gender_male_l.append(gender_male)
        gender_female_l.append(gender_female)
        ages_group_10_l.append(ages_group_10)
        ages_group_20_l.append(ages_group_20)
        ages_group_30_l.append(ages_group_30)
        ages_group_40_l.append(ages_group_40)
        ages_group_50_l.append(ages_group_50)
        ages_group_60_l.append(ages_group_60)
        reply_all_l.append(reply_l)
        crawl_time_l.append(datetime.now().strftime("%Y%m%d-%H%m"))
        reply_cnt_l.append(len(reply_l))
        news_id_l.append(news_id)

        # 변수 List로 dataFrame만들고 저장!
        df = pd.DataFrame()
        df['news_id'] = news_id_l
        df['title'] = title_l
        df['gender_male'] = gender_male_l
        df['gender_female'] = gender_female_l
        df['ages_group_10'] = ages_group_10_l
        df['ages_group_20'] = ages_group_20_l
        df['ages_group_30'] = ages_group_30_l
        df['ages_group_40'] = ages_group_40_l
        df['ages_group_50'] = ages_group_50_l
        df['ages_group_60'] = ages_group_60_l
        df['reply_cnt'] = reply_cnt_l
        df['reply_all'] = reply_all_l
        df['crawl_time'] = crawl_time_l
        ## 저장해주기!!
        df.to_pickle('naver11_')
        print(type(url))
        return url
    else:
        print("a")


def get_naver_news_comments(url, wait_time=10, delay_time=0.1):
    # 크롬 드라이버로 해당 url에 접속
    driver = webdriver.Chrome()

    # (크롬)드라이버가 요소를 찾는데에 최대 wait_time 초까지 기다림 (함수 사용 시 설정 가능하며 기본값은 5초)
    driver.implicitly_wait(wait_time)

    # 인자로 입력받은 url 주소를 가져와서 접속
    driver.get(url)

    # 더보기가 안뜰 때 까지 계속 클릭 (모든 댓글의 html을 얻기 위함)
    while True:

        # 예외처리 구문 - 더보기 광클하다가 없어서 에러 뜨면 while문을 나감(break)
        try:
            more = driver.find_element(By.CLASS_NAME, 'u_cbox_btn_more')
            more.click()
            time.sleep(delay_time)

        except:
            break

    # 본격적인 크롤링 타임

    # selenium으로 페이지 전체의 html 문서 받기
    html = driver.page_source

    # 위에서 받은 html 문서를 bs4 패키지로 parsing
    soup = BeautifulSoup(html, 'lxml')

    # 1)작성자
    nicknames = soup.select('span.u_cbox_nick')
    list_nicknames = [nickname.text for nickname in nicknames]

    # 2)댓글 시간
    datetimes = soup.select('span.u_cbox_date')
    list_datetimes = [datetime.text for datetime in datetimes]

    # 3)댓글 내용
    contents = soup.select('span.u_cbox_contents')
    list_contents = [content.text for content in contents]

    # 4)작성자, 댓글 시간, 내용을 셋트로 취합
    list_sum = list(zip(list_nicknames, list_datetimes, list_contents))

    # 드라이버 종료
    driver.quit()

    # 함수를 종료하며 list_sum을 결과물로 제출
    return list_sum


# step3. 실제 함수 실행 및 엑셀로 저장
if __name__ == '__main__':  # 설명하자면 매우 길어져서 그냥 이렇게 사용하는 것을 권장
    i = 0;
    # 원하는 기사 url 입력
    # getAge() #url까지 나옴
    while (i < 200):
        # url=getAge()
        # 함수 실행
        comments = get_naver_news_comments(getAge())

        # 엑셀의 첫줄에 들어갈 컬럼명
        col = ['작성자', '시간', '내용']

        # pandas 데이터 프레임 형태로 가공
        df = pd.DataFrame(comments, columns=col)

        # 데이터 프레임을 엑셀로 저장 (파일명은 'news.xlsx', 시트명은 '뉴스 기사 제목')

        make100()
        age1020 = a + b;
        fileName = str(age1020) + " " + str(c) + " " + str(d) + " " + str(e) + " " + str(f) + ".xlsx"
        sameFileNameCounter = 1;
        while os.path.exists(fileName):
            print(f"경로에 {fileName}이 존재함");
            fileName = str(age1020) + " " + str(c) + " " + str(d) + " " + str(e) + " " + str(f)+ str(sameFileNameCounter) + ".xlsx"

        # df.to_excel('/Users/jeongseonghyeon/untitled2/%s/%d %d %d %d %d.xlsx'%(filesave_decision(),a+b,c,d,e,f) , sheet_name='뉴스 기사 제목')
        #df.to_excel('/Users/jeongseonghyeon/untitled2/newsList/%d %d %d %d %d.xlsx' % (a + b, c, d, e, f),sheet_name='뉴스 기사 제목')
        df.to_excel('/Users/jeongseonghyeon/untitled2/newsList/%s' % (fileName),sheet_name='뉴스 기사 제목')
        i += 1;
