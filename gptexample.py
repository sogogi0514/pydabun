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

# 댓글 수집 함수
def comment(url_list):
    total_comment = []

    for url_ex in url_list:
        url = url_ex.split('?')[0]
        oid_1 = url.split('/')[-1]
        oid_2 = url.split('/')[-2]
        i = 1

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

                comments = [c['contents'] for c in comment_list]
                total_comment.extend(comments)

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
