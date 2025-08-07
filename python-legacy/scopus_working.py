#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scopus API를 활용한 논문 검색 (작동하는 버전)
테스트 파일의 함수들을 활용
"""

import requests
import json
import time
import pandas as pd
from typing import Dict, List, Optional

class ScopusWorkingClient:
    """Scopus API 클라이언트 (작동하는 버전)"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.elsevier.com/content/search/scopus"
        self.headers = {
            'Accept': 'application/json',
            'X-ELS-APIKey': api_key
        }
    
    def search_scopus(self, query: str, count: int = 25, start: int = 0, view: str = "COMPLETE") -> Dict:
        """Scopus 검색 (테스트에서 작동하는 방식)"""
        
        params = {
            'query': query,
            'count': count,
            'start': start,
            'view': view,
            'apiKey': self.api_key
        }
        
        try:
            response = requests.get(self.base_url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"API 요청 실패: {response.status_code}")
                print(f"응답 내용: {response.text}")
                return {}
                
        except Exception as e:
            print(f"오류 발생: {e}")
            return {}

def search_usability_papers():
    """Usability 관련 논문 검색"""
    
    api_key = "920a284740d2c60fc3249e6e795e928c"
    client = ScopusWorkingClient(api_key)
    
    print("🔍 Usability 논문 검색 시작...")
    print("=" * 60)
    
    # 다양한 검색 쿼리 시도
    queries = [
        "usability",
        "TITLE-ABS-KEY(usability)",
        "TITLE-ABS-KEY(usability) AND PUBYEAR > 2020",
        "TITLE-ABS-KEY(user experience)",
        "TITLE-ABS-KEY(UX)",
        "TITLE-ABS-KEY(usability) AND LANGUAGE(english)"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n[{i}] 쿼리 테스트: {query}")
        print("-" * 50)
        
        results = client.search_scopus(query=query, count=5, start=0, view="STANDARD")
        
        if results and 'search-results' in results:
            total_results = results['search-results'].get('opensearch:totalResults', 0)
            entries = results['search-results'].get('entry', [])
            
            print(f"✅ 성공! 총 {total_results}개 결과")
            print(f"현재 페이지: {len(entries)}개")
            
            # 결과 출력
            for j, entry in enumerate(entries, 1):
                print(f"  {j}. {entry.get('dc:title', 'N/A')}")
                print(f"     저자: {entry.get('dc:creator', 'N/A')}")
                print(f"     저널: {entry.get('prism:publicationName', 'N/A')}")
                print(f"     발행일: {entry.get('prism:coverDate', 'N/A')}")
                print(f"     인용: {entry.get('citedby-count', 0)}")
                
                # 초록 정보 출력
                abstract = entry.get('dc:description', '')
                if abstract and abstract != 'N/A':
                    # 초록이 너무 길면 잘라서 표시
                    if len(abstract) > 200:
                        abstract = abstract[:200] + "..."
                    print(f"     초록: {abstract}")
                print()
            
            # 성공한 쿼리로 더 많은 결과 검색
            if int(total_results) > 0:
                print(f"🎯 이 쿼리로 더 많은 결과를 검색하시겠습니까? (y/n): ", end="")
                choice = input().strip().lower()
                
                if choice == 'y':
                    return search_more_results(client, query, int(total_results))
                else:
                    break
        else:
            print("❌ 검색 실패")
        
        time.sleep(1)  # API 호출 간격
    
    return []

def search_more_results(client: ScopusWorkingClient, query: str, total_results: int):
    """더 많은 결과 검색"""
    
    print(f"\n🔍 '{query}' 쿼리로 더 많은 결과 검색...")
    print(f"총 {total_results}개 결과 중에서 검색할 개수를 입력하세요 (최대 200): ", end="")
    
    try:
        count = int(input().strip())
        count = min(count, 200)  # 최대 200개로 제한
    except ValueError:
        count = 25
        print("기본값 25개로 설정")
    
    results = client.search_scopus(query=query, count=count, start=0, view="STANDARD")
    
    if results and 'search-results' in results:
        entries = results['search-results'].get('entry', [])
        
        print(f"\n✅ {len(entries)}개 결과를 찾았습니다!")
        print("=" * 60)
        
        papers = []
        for i, entry in enumerate(entries, 1):
            paper = {
                'title': entry.get('dc:title', 'N/A'),
                'authors': entry.get('dc:creator', 'N/A'),
                'publication_name': entry.get('prism:publicationName', 'N/A'),
                'publication_date': entry.get('prism:coverDate', 'N/A'),
                'doi': entry.get('prism:doi', 'N/A'),
                'cited_by_count': entry.get('citedby-count', 0),
                'scopus_id': entry.get('dc:identifier', '').replace('SCOPUS_ID:', ''),
                'scopus_url': f"https://www.scopus.com/inward/record.uri?eid={entry.get('eid', '')}",
                'abstract': entry.get('dc:description', 'N/A')
            }
            papers.append(paper)
            
            print(f"[{i}] {paper['title']}")
            print(f"    저자: {paper['authors']}")
            print(f"    저널: {paper['publication_name']}")
            print(f"    발행일: {paper['publication_date']}")
            print(f"    인용: {paper['cited_by_count']}")
            print(f"    DOI: {paper['doi']}")
            
            # 초록 정보 출력
            abstract = paper['abstract']
            if abstract and abstract != 'N/A':
                # 초록이 너무 길면 잘라서 표시
                if len(abstract) > 300:
                    abstract = abstract[:300] + "..."
                print(f"    초록: {abstract}")
            print("-" * 50)
        
        return papers
    else:
        print("❌ 검색 실패")
        return []

def save_to_csv(papers: List[Dict], filename: str = "scopus_results.csv"):
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
    
    print("🔍 Scopus 논문 검색 시스템 (작동하는 버전)")
    print("=" * 60)
    
    try:
        # Usability 논문 검색
        papers = search_usability_papers()
        
        if papers:
            # CSV 저장
            save_choice = input("\n결과를 CSV 파일로 저장하시겠습니까? (y/n): ").strip().lower()
            if save_choice == 'y':
                filename = input("파일명을 입력하세요 (기본: scopus_results.csv): ").strip()
                if not filename:
                    filename = "scopus_results.csv"
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