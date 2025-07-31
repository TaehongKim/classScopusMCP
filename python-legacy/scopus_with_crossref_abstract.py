#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scopus API + Crossref API를 활용한 논문 검색 (초록 포함)
Crossref API를 사용하여 DOI로부터 초록 정보를 가져옴
"""

import requests
import json
import time
import pandas as pd
from typing import Dict, List, Optional

class ScopusWithCrossrefClient:
    """Scopus API + Crossref API 클라이언트"""
    
    def __init__(self, scopus_api_key: str):
        self.scopus_api_key = scopus_api_key
        self.scopus_url = "https://api.elsevier.com/content/search/scopus"
        self.crossref_url = "https://api.crossref.org/works"
        self.headers = {
            'Accept': 'application/json',
            'X-ELS-APIKey': scopus_api_key
        }
    
    def search_scopus(self, query: str, count: int = 25, start: int = 0) -> Dict:
        """Scopus 검색"""
        
        params = {
            'query': query,
            'count': count,
            'start': start,
            'apiKey': self.scopus_api_key
        }
        
        try:
            response = requests.get(self.scopus_url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Scopus API 요청 실패: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"Scopus API 오류: {e}")
            return {}
    
    def get_abstract_from_crossref(self, doi: str) -> str:
        """Crossref API를 사용하여 DOI로부터 초록 가져오기"""
        
        if not doi or doi == 'N/A':
            return 'N/A'
        
        url = f"{self.crossref_url}/{doi}"
        
        try:
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                # 초록 정보 찾기
                if 'message' in data:
                    message = data['message']
                    
                    # abstract 필드 확인
                    if 'abstract' in message:
                        return message['abstract']
                    
                    # 다른 방법으로 초록 찾기
                    if 'description' in message:
                        return message['description']
                    
                    # content 필드 확인
                    if 'content' in message:
                        for content in message['content']:
                            if content.get('type') == 'text/html' and 'content' in content:
                                return content['content']
                
                return 'N/A'
            else:
                print(f"Crossref API 요청 실패 (DOI: {doi}): {response.status_code}")
                return 'N/A'
                
        except Exception as e:
            print(f"Crossref API 오류 (DOI: {doi}): {e}")
            return 'N/A'
    
    def get_paper_info_from_crossref(self, doi: str) -> Dict:
        """Crossref API를 사용하여 논문 정보 가져오기"""
        
        if not doi or doi == 'N/A':
            return {}
        
        url = f"{self.crossref_url}/{doi}"
        
        try:
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'message' in data:
                    message = data['message']
                    
                    paper_info = {
                        'title': message.get('title', ['N/A'])[0] if message.get('title') else 'N/A',
                        'authors': [],
                        'journal': message.get('container-title', ['N/A'])[0] if message.get('container-title') else 'N/A',
                        'published_date': message.get('published-print', {}).get('date-parts', [['N/A']])[0][0] if message.get('published-print') else 'N/A',
                        'doi': doi,
                        'abstract': message.get('abstract', 'N/A'),
                        'url': message.get('URL', 'N/A')
                    }
                    
                    # 저자 정보 추출
                    if 'author' in message:
                        for author in message['author']:
                            if 'given' in author and 'family' in author:
                                author_name = f"{author['given']} {author['family']}"
                                paper_info['authors'].append(author_name)
                            elif 'name' in author:
                                paper_info['authors'].append(author['name'])
                    
                    return paper_info
                
                return {}
            else:
                print(f"Crossref API 요청 실패 (DOI: {doi}): {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"Crossref API 오류 (DOI: {doi}): {e}")
            return {}

def search_usability_papers_with_crossref():
    """Usability 관련 논문 검색 (Crossref 초록 포함)"""
    
    api_key = "920a284740d2c60fc3249e6e795e928c"
    client = ScopusWithCrossrefClient(api_key)
    
    print("🔍 Usability 논문 검색 시작 (Crossref 초록 포함)...")
    print("=" * 60)
    
    # 검색 쿼리
    query = "usability"
    print(f"검색 쿼리: {query}")
    print("-" * 50)
    
    results = client.search_scopus(query=query, count=5, start=0)
    
    if results and 'search-results' in results:
        total_results = results['search-results'].get('opensearch:totalResults', 0)
        entries = results['search-results'].get('entry', [])
        
        print(f"✅ 성공! 총 {total_results}개 결과")
        print(f"현재 페이지: {len(entries)}개")
        print()
        
        papers = []
        for i, entry in enumerate(entries, 1):
            doi = entry.get('prism:doi', 'N/A')
            
            print(f"[{i}] {entry.get('dc:title', 'N/A')}")
            print(f"    저자: {entry.get('dc:creator', 'N/A')}")
            print(f"    저널: {entry.get('prism:publicationName', 'N/A')}")
            print(f"    발행일: {entry.get('prism:coverDate', 'N/A')}")
            print(f"    인용: {entry.get('citedby-count', 0)}")
            print(f"    DOI: {doi}")
            
            # Crossref에서 초록 정보 가져오기
            if doi != 'N/A':
                print("    Crossref에서 초록 조회 중...", end="")
                abstract = client.get_abstract_from_crossref(doi)
                if abstract and abstract != 'N/A':
                    if len(abstract) > 300:
                        abstract = abstract[:300] + "..."
                    print(f" ✅")
                    print(f"    초록: {abstract}")
                else:
                    print(" ❌ (초록 없음)")
            else:
                print("    DOI 없음 - 초록 조회 불가")
            
            paper = {
                'title': entry.get('dc:title', 'N/A'),
                'authors': entry.get('dc:creator', 'N/A'),
                'publication_name': entry.get('prism:publicationName', 'N/A'),
                'publication_date': entry.get('prism:coverDate', 'N/A'),
                'doi': doi,
                'cited_by_count': entry.get('citedby-count', 0),
                'scopus_id': entry.get('dc:identifier', '').replace('SCOPUS_ID:', ''),
                'scopus_url': f"https://www.scopus.com/inward/record.uri?eid={entry.get('eid', '')}",
                'abstract': abstract if doi != 'N/A' else 'N/A'
            }
            papers.append(paper)
            
            print("-" * 50)
            
            # API 호출 간격
            time.sleep(1)
        
        return papers
    else:
        print("❌ 검색 실패")
        return []

def test_crossref_doi():
    """Crossref API 테스트"""
    
    client = ScopusWithCrossrefClient("dummy_key")  # Crossref는 API 키가 필요 없음
    
    # 테스트용 DOI들
    test_dois = [
        "10.1016/S0014-5793(01)03313-0",  # 원래 테스트 DOI
        "10.1016/j.scico.2025.103365",     # WEST 논문
        "10.1002/deo2.70150",              # AI Endoscopy 논문
        "10.1038/nature12373",             # Nature 논문 (초록 있을 가능성 높음)
        "10.1126/science.1234567"          # Science 논문
    ]
    
    print("🔍 Crossref API 테스트...")
    print("=" * 60)
    
    for i, doi in enumerate(test_dois, 1):
        print(f"\n[{i}] DOI 테스트: {doi}")
        print("-" * 40)
        
        paper_info = client.get_paper_info_from_crossref(doi)
        
        if paper_info:
            print("✅ Crossref API 성공!")
            print(f"제목: {paper_info.get('title', 'N/A')}")
            print(f"저자: {', '.join(paper_info.get('authors', []))}")
            print(f"저널: {paper_info.get('journal', 'N/A')}")
            print(f"발행일: {paper_info.get('published_date', 'N/A')}")
            
            abstract = paper_info.get('abstract', 'N/A')
            if abstract and abstract != 'N/A':
                if len(abstract) > 200:
                    abstract = abstract[:200] + "..."
                print(f"초록: {abstract}")
            else:
                print("초록: 없음")
        else:
            print("❌ Crossref API 실패")
        
        time.sleep(1)  # API 호출 간격

def save_to_csv(papers: List[Dict], filename: str = "scopus_crossref_abstract.csv"):
    """결과를 CSV 파일로 저장"""
    
    if not papers:
        print("저장할 결과가 없습니다.")
        return
    
    df_data = []
    for paper in papers:
        df_data.append({
            'Title': paper['title'],
            'Authors': paper['authors'],
            'Publication': paper['publication_name'],
            'Date': paper['publication_date'],
            'DOI': paper['doi'],
            'Citations': paper['cited_by_count'],
            'Scopus_ID': paper['scopus_id'],
            'Scopus_URL': paper['scopus_url'],
            'Abstract': paper['abstract']
        })
    
    df = pd.DataFrame(df_data)
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"\n✅ 결과가 '{filename}' 파일로 저장되었습니다.")

def main():
    """메인 함수"""
    
    print("🔍 Scopus + Crossref 논문 검색 시스템")
    print("=" * 60)
    
    try:
        # 먼저 Crossref API 테스트
        print("1. Crossref API 테스트...")
        test_crossref_doi()
        
        print("\n" + "=" * 60)
        print("2. Usability 논문 검색 (Crossref 초록 포함)...")
        
        # Usability 논문 검색 (Crossref 초록 포함)
        papers = search_usability_papers_with_crossref()
        
        if papers:
            # CSV 저장
            save_choice = input("\n결과를 CSV 파일로 저장하시겠습니까? (y/n): ").strip().lower()
            if save_choice == 'y':
                filename = input("파일명을 입력하세요 (기본: scopus_crossref_abstract.csv): ").strip()
                if not filename:
                    filename = "scopus_crossref_abstract.csv"
                save_to_csv(papers, filename)
            
            print(f"\n✅ 검색 완료! {len(papers)}개의 논문을 찾았습니다.")
        else:
            print("❌ 검색 결과가 없습니다.")
            
    except KeyboardInterrupt:
        print("\n\n사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main() 