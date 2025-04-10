import urllib.request
from urllib.parse import urlparse,parse_qs
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
#
# 사용자 에이전트 정의
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
}


# 뉴스 URL 수집 함수
def news_url(query):
    page = 1
    url_list = []
    title_list = []

    while page <= 151:
        #url에 대해
        url = (
                "https://m.search.naver.com/search.naver?where=m_news&sm=tab_pge&query="
                + query +
                "&sort=0&photo=0&field=0&pd=1&ds=&de=&cluster_rank=129&mynews=0&office_type=0"
                "&office_section_code=0&news_office_checked=&nso=so:r,p:1w,a:all&start=" + str(page) #start은 최소 1 최대 1000임
        )
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'referer':url
        }

        response = requests.get(url, headers=headers)
        html = response.text
        soup = BeautifulSoup(html, "lxml")
        atags = soup.select('.news_tit')


        for i in atags:
            if "https://n.news.naver.com/" in i['href']:
                url_list.append(i['href'])
                news_title_name=get_title_name(i)
                title_list.append(news_title_name)

        if len(atags) < 15:
            break

        page += 15
        time.sleep(0.5)  # 너무 빠르게 요청하지 않도록 sleep

    return url_list ,title_list # -> zip으로 묶거나 받는 변수를 2개 나 튜플로 해야함




# 뉴스 연령대 데이터가 필요하면 여기서 더 추가해서 사용 가능함
# def getAge(url_list,headers,url_list_num,oid_1,oid_2):
#     print("asd")
#     getAge_url=url_list[url_list_num]
#     response = requests.get(getAge_url, headers=headers)
#     html=response.text
#     soup = BeautifulSoup(html, "lxml")
#     news_id=f'news{oid_2},{oid_1}'
#     url_api= 'https://apis.naver.com/commentBox/cbox/web_naver_list_jsonp.json?ticket=news&templateId=view_society&pool=cbox5&_wr&_callback=jQuery11240673401066245984_1638166575411&lang=ko&country=KR&objectId=' + news_id + '&categoryId=&pageSize=10&indexSize=10&groupId=&listType=OBJECT&pageType=more&page=1&initialize=true&userType=&useAltSort=true&replyPageSize=20&sort=favorite&includeAllStatus=true&_=1638166575413'
#     getAge_req=requests.get(url_api,headers=headers)
#     getAge_json= json.loads(getAge_req.text[getAge_req.text.find('{'):-2])
#
#     gender_male = getAge_json['result']['graph']['gender']['male']
#     gender_female = getAge_json['result']['graph']['gender']['female']
#
#     ## 연령 통게정보 가져오기
#     ages_group_10 = getAge_json['result']['graph']['old'][0]['value']
#     ages_group_20 = getAge_json['result']['graph']['old'][1]['value']
#     ages_group_30 = getAge_json['result']['graph']['old'][2]['value']
#     ages_group_40 = getAge_json['result']['graph']['old'][3]['value']
#     ages_group_50 = getAge_json['result']['graph']['old'][4]['value']
#     ages_group_60 = getAge_json['result']['graph']['old'][5]['value']
#     return gender_male, gender_female, ages_group_10, ages_group_20, ages_group_30, ages_group_40, ages_group_50, ages_group_60

#oid_2를 매개변수로 넣으면 언론사 이름이 string으로 return되는 함수입니다.


#언론사 id(oid_2)를 언론사 이름으로 바꾸는 함수  ex) "023" -> "연합뉴스"
# html요청 없이 따로 딕셔너리 형태로 만들어서 사용하면  더 빨라지는데 언론사 수가 생각보다 많아서 그냥 이렇게 했습니다.
def get_press_name(press_id):
    url_company='https://news.naver.com/main/officeList.naver'
    html_company = urllib.request.urlopen(url_company).read()
    soup_company = BeautifulSoup(html_company, "lxml")
    title_company=soup_company.find_all(class_='list_press nclicks(\'rig.renws2pname\')')
    for i in title_company:
        parts= urlparse(i.attrs['href'])
        if parse_qs(parts.query)['officeId'][0]==press_id:
            news_name = i.text.strip()
            return news_name


# 뉴스 이름을 html에서 가져오는 함수- news_url 함수 안에서 사용해서 별도의 html요청 없이 링크를 가져오려고 하는 html에서 추출
def get_title_name(atag):
    news_title_name=atag.find('div').text.strip()
    print(news_title_name) #가져 오는 뉴스 이름 확인용
    return news_title_name



# 댓글 수집 함수
def comment(url_list,news_title_list):
    total_comment = []
    url_list_num=0
    news_title_list_num=0
    for url_ex in url_list:
        url = url_ex.split('?')[0]
        oid_1 = url.split('/')[-1]
        oid_2 = url.split('/')[-2]
        i = 1
        url_list_num+=1


        # getAge(url_list,headers,url_list_num,oid_1,oid_2)


        while True:
            params = {
                'ticket': 'news',
                'templateId': 'default_society',
                'pool': 'cbox5',
                'lang': 'ko',
                'country': 'KR',
                'objectId': f'news{oid_2},{oid_1}',
                'pageSize': '100',
                'indexSize': '10',
                'page': str(i),
                'currentPage': '0',
                'moreParam.direction': 'next',
                'moreParam.prev': '',
                'moreParam.next': '',
                'followSize': '100',
                'includeAllStatus': 'true',
            }
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'referer': url_ex
            }
            response = requests.get(
                'https://apis.naver.com/commentBox/cbox/web_naver_list_jsonp.json',
                params=params,
                headers=headers
            )

            response.encoding = "UTF-8-sig"
            res = response.text.replace("_callback(", "")[:-2]

            news_title_list_num += 1
            try:
                temp = json.loads(res)
                comment_list = temp['result'].get('commentList', [])
                if not comment_list:
                    print("comment 가져오기 실패")
                    break
                #아래는 가져온 comment_list( 위에서 요청한 json 내용 으로 'contents': '탄해반대집회는~~' 형태로 존재)
                user_nickname=[k['userName'] for k in comment_list] #json 내용에서 userName에 해당하는 부분을 가져와 리스트로 저장시킴
                comments = [c['contents'] for c in comment_list] #json에서 contents에 해당하는 부분을 가져와 리스트로 저장시킴
                total_comment.extend(comments) #없어도 되는 코드 gptexample에 있던 코드
                comment_list_sum=list(zip(user_nickname, comments)) #df로 저장하기 위해 묶어줌
                col=['작성자','내용']
                df=pd.DataFrame(comment_list_sum, columns=col) # columns를 작성자, 내용 으로 가지는 df생성
                #파일을 저장하기 위한 경로 이름 생성, 파일 이름 생성
                news_name=get_press_name(oid_2) #언론사 id를 언론사 이름 str로 바꾸는 함수
                folder_path=f'./{news_name}'
                os.makedirs(folder_path, exist_ok=True) #이 py가 있는 경로에 "언론사이름"을 이름으로 하는 폴더 생성, 존재시 넘어감
                file_name= f"{news_name}_{news_title_list[news_title_list_num]}.xlsx" #파일 이름을 언론사_뉴스제목 으로 정의
                if os.path.exists(f"{folder_path}/{file_name}"): #같은 이름 존재시 break
                    print(f"{folder_path}/{file_name} 이미 존재함. ")
                    continue;
                df.to_excel(f"{folder_path}/{file_name}", index=False) #엑셀파일로 저장 다른 형식으로 바꾸고자 하면  .xlsx와 이 메소드 바꾸면 됨.


                if len(comments) < 97: #연령 데이터 가져오려면 < 101 으로 설정 설정해야 함
                    break
                else:
                    i += 1 # 다음페이지 가져오기 위한 변수 같음 params= ..., 'page'=str(i),...
                    time.sleep(0.3)
            except Exception as e:
                print(f"[에러 발생] {url_ex}: {e}")
                break

    return total_comment #필요 없음


query = "탄핵"  # 원하는 검색어
encoded_query = urllib.parse.quote(query) #url에 쿼리스트링에 한글 사용하려면 인코딩 필수

news_links, news_title = news_url(encoded_query)
print(f"{len(news_links)}개의 뉴스 링크 수집 완료")
print(news_links)

all_comments = comment(news_links,news_title)
print(f"{len(all_comments)}개의 댓글 수집 완료")
