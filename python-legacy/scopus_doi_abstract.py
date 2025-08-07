#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scopus API를 활용한 논문 검색 (DOI 기반 초록 포함)
DOI를 사용한 Abstract Retrieval API 활용
"""

import requests
import json
import time
import pandas as pd
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional

class ScopusDOIAbstractClient:
    """Scopus API 클라이언트 (DOI 기반 초록 포함)"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.elsevier.com/content/search/scopus"
        self.abstract_url = "https://api.elsevier.com/content/abstract/doi"
        self.headers = {
            'Accept': 'text/xml',
            'X-ELS-APIKey': api_key
        }
    
    def search_scopus(self, query: str, count: int = 25, start: int = 0) -> Dict:
        """Scopus 검색"""
        
        params = {
            'query': query,
            'count': count,
            'start': start,
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
    
    def get_abstract_by_doi(self, doi: str) -> str:
        """DOI를 사용하여 초록 가져오기"""
        
        if not doi or doi == 'N/A':
            return 'N/A'
        
        url = f"{self.abstract_url}/{doi}"
        params = {
            'apiKey': self.api_key
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                # XML 응답 파싱
                root = ET.fromstring(response.text)
                
                # XML 네임스페이스 정의
                namespaces = {
                    'ns': 'http://www.elsevier.com/xml/svapi/abstract/dtd',
                    'dc': 'http://purl.org/dc/elements/1.1/',
                    'prism': 'http://prismstandard.org/namespaces/basic/2.0/'
                }
                
                # 초록 정보 찾기 (XML에서 description 태그 찾기)
                abstract_elements = root.findall('.//dc:description', namespaces)
                if abstract_elements:
                    return abstract_elements[0].text
                
                # 다른 방법으로 초록 찾기
                for elem in root.iter():
                    if 'description' in elem.tag:
                        return elem.text
                
                return 'N/A'
            else:
                print(f"초록 조회 실패 (DOI: {doi}): {response.status_code}")
                return 'N/A'
                
        except Exception as e:
            print(f"초록 조회 오류 (DOI: {doi}): {e}")
            return 'N/A'

def search_usability_papers_with_doi_abstract():
    """Usability 관련 논문 검색 (DOI 기반 초록 포함)"""
    
    api_key = "920a284740d2c60fc3249e6e795e928c"
    client = ScopusDOIAbstractClient(api_key)
    
    print("🔍 Usability 논문 검색 시작 (DOI 기반 초록 포함)...")
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
            
            # DOI를 사용하여 초록 정보 가져오기
            if doi != 'N/A':
                print("    초록 조회 중...", end="")
                abstract = client.get_abstract_by_doi(doi)
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

def save_to_csv(papers: List[Dict], filename: str = "scopus_doi_abstract.csv"):
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

def test_doi_abstract():
    """DOI 기반 초록 조회 테스트"""
    
    api_key = "920a284740d2c60fc3249e6e795e928c"
    client = ScopusDOIAbstractClient(api_key)
    
    # 테스트용 DOI (제공된 예제)
    test_doi = "10.1016/S0014-5793(01)03313-0"
    
    print("🔍 DOI 기반 초록 조회 테스트...")
    print(f"테스트 DOI: {test_doi}")
    print("-" * 50)
    
    abstract = client.get_abstract_by_doi(test_doi)
    
    if abstract and abstract != 'N/A':
        print("✅ 초록 조회 성공!")
        print(f"초록: {abstract[:200]}...")
        return True
    else:
        print("❌ 초록 조회 실패")
        return False

def main():
    """메인 함수"""
    
    print("🔍 Scopus 논문 검색 시스템 (DOI 기반 초록 포함)")
    print("=" * 60)
    
    try:
        # 먼저 DOI 기반 초록 조회 테스트
        print("1. DOI 기반 초록 조회 테스트...")
        test_success = test_doi_abstract()
        
        if test_success:
            print("\n2. Usability 논문 검색 (초록 포함)...")
            # Usability 논문 검색 (초록 포함)
            papers = search_usability_papers_with_doi_abstract()
            
            if papers:
                # CSV 저장
                save_choice = input("\n결과를 CSV 파일로 저장하시겠습니까? (y/n): ").strip().lower()
                if save_choice == 'y':
                    filename = input("파일명을 입력하세요 (기본: scopus_doi_abstract.csv): ").strip()
                    if not filename:
                        filename = "scopus_doi_abstract.csv"
                    save_to_csv(papers, filename)
                
                print(f"\n✅ 검색 완료! {len(papers)}개의 논문을 찾았습니다.")
            else:
                print("❌ 검색 결과가 없습니다.")
        else:
            print("❌ DOI 기반 초록 조회가 실패했습니다.")
            
    except KeyboardInterrupt:
        print("\n\n사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main() 