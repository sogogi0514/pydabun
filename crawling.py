import urllib.request
from urllib.parse import urlparse,parse_qs
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time

# 사용자 에이전트 정의
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
}


# 뉴스 URL 수집 함수
def news_url(query):
    page = 1
    url_list = []

    while page <= 151:
        url = (
                "https://m.search.naver.com/search.naver?where=m_news&sm=tab_pge&query="
                + query +
                "&sort=0&photo=0&field=0&pd=1&ds=&de=&cluster_rank=129&mynews=0&office_type=0"
                "&office_section_code=0&news_office_checked=&nso=so:r,p:1w,a:all&start=" + str(page)
        )

        response = requests.get(url, headers=headers)
        html = response.text
        soup = BeautifulSoup(html, "lxml")
        atags = soup.select('.news_tit')

        for i in atags:
            if "https://n.news.naver.com/" in i['href']:
                url_list.append(i['href'])

        if len(atags) < 15:
            break

        page += 15
        time.sleep(0.5)  # 너무 빠르게 요청하지 않도록 sleep

    return url_list

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







# 댓글 수집 함수
def comment(url_list):
    total_comment = []
    url_list_num=0

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

            try:
                temp = json.loads(res)
                comment_list = temp['result'].get('commentList', [])
                if not comment_list:
                    print("comment 가져오기 실패")
                    break
                user_nickname=[i['userName'] for i in comment_list]
                comments = [c['contents'] for c in comment_list]
                total_comment.extend(comments)
                comment_list_sum=list(zip(user_nickname, comments))
                col=['작성자','내용']
                df=pd.DataFrame(comment_list_sum, columns=col)
                news_name=get_press_name(oid_2)
                folder_path=f'./{news_name}'
                os.makedirs(folder_path, exist_ok=True)
                file_name= f"{news_name}1.xlsx"
                same_file_counter=1;
                while os.path.exists(f"{folder_path}/{file_name}"):
                    print(f"{folder_path}/{file_name} 이미 존재함. ")
                    same_file_counter+=1
                    file_name= f"{news_name}{same_file_counter}.xlsx"
                df.to_excel(f"{folder_path}/{file_name}", index=False)


                if len(comments) < 97:
                    break
                else:
                    i += 1
                    time.sleep(0.3)
            except Exception as e:
                print(f"[에러 발생] {url_ex}: {e}")
                break

    return total_comment


query = "탄핵"  # 원하는 검색어
news_links = news_url(query)
print(f"{len(news_links)}개의 뉴스 링크 수집 완료")
print(news_links)

all_comments = comment(news_links)
print(f"{len(all_comments)}개의 댓글 수집 완료")
