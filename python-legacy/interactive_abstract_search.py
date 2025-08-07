#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
인터랙티브 초록 검색 시스템
- 사용자 키워드 입력
- Scopus 검색 + 다중 소스 초록 가져오기
- 결과 저장 및 관리
"""

import requests
import json
import time
import pandas as pd
import urllib3
import re
from typing import Dict, List, Optional
from urllib.parse import quote

# SSL 경고 비활성화
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class InteractiveAbstractSearch:
    """인터랙티브 초록 검색 시스템"""
    
    def __init__(self, scopus_api_key: str):
        self.scopus_api_key = scopus_api_key
        self.scopus_url = "https://api.elsevier.com/content/search/scopus"
        self.sources = {
            'crossref': 'https://api.crossref.org/works',
            'pubmed': 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils',
            'semantic_scholar': 'https://api.semanticscholar.org/v1',
            'openalex': 'https://api.openalex.org'
        }
        
        self.headers = {
            'Accept': 'application/json',
            'X-ELS-APIKey': scopus_api_key
        }
    
    def clean_abstract(self, abstract: str) -> str:
        """초록 텍스트 정리 (HTML 태그 제거, 길이 조정)"""
        if not abstract or abstract == 'N/A':
            return 'N/A'
        
        # HTML 태그 제거
        clean_text = re.sub(r'<[^>]+>', '', abstract)
        
        # JATS 태그 제거
        clean_text = re.sub(r'<jats:[^>]+>', '', clean_text)
        clean_text = re.sub(r'</jats:[^>]+>', '', clean_text)
        
        # 특수 문자 정리
        clean_text = re.sub(r'\s+', ' ', clean_text)  # 여러 공백을 하나로
        clean_text = clean_text.strip()
        
        # 길이 제한 (500자)
        if len(clean_text) > 500:
            clean_text = clean_text[:500] + "..."
        
        return clean_text
    
    def search_scopus(self, query: str, count: int = 10, start: int = 0) -> Dict:
        """Scopus 검색"""
        
        params = {
            'query': query,
            'count': count,
            'start': start,
            'apiKey': self.scopus_api_key
        }
        
        try:
            response = requests.get(self.scopus_url, headers=self.headers, params=params, verify=False)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Scopus API 요청 실패: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"Scopus API 오류: {e}")
            return {}
    
    def get_abstract_from_crossref(self, doi: str) -> Dict:
        """Crossref API로 초록 가져오기"""
        if not doi or doi == 'N/A':
            return {'source': 'crossref', 'abstract': 'N/A', 'success': False}
        
        url = f"{self.sources['crossref']}/{doi}"
        
        try:
            response = requests.get(url, verify=False, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'message' in data:
                    message = data['message']
                    abstract = message.get('abstract', 'N/A')
                    
                    if abstract and abstract != 'N/A':
                        clean_abstract = self.clean_abstract(abstract)
                        return {
                            'source': 'crossref',
                            'abstract': clean_abstract,
                            'success': True,
                            'title': message.get('title', ['N/A'])[0] if message.get('title') else 'N/A',
                            'quality_score': 9
                        }
            
            return {'source': 'crossref', 'abstract': 'N/A', 'success': False}
            
        except Exception as e:
            return {'source': 'crossref', 'abstract': 'N/A', 'success': False}
    
    def get_abstract_from_pubmed(self, doi: str) -> Dict:
        """PubMed API로 초록 가져오기"""
        if not doi or doi == 'N/A':
            return {'source': 'pubmed', 'abstract': 'N/A', 'success': False}
        
        search_url = f"{self.sources['pubmed']}/esearch.fcgi"
        search_params = {
            'db': 'pubmed',
            'term': f"{doi}[doi]",
            'retmode': 'json'
        }
        
        try:
            response = requests.get(search_url, params=search_params, verify=False, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'esearchresult' in data and 'idlist' in data['esearchresult']:
                    pmid_list = data['esearchresult']['idlist']
                    
                    if pmid_list:
                        pmid = pmid_list[0]
                        
                        fetch_url = f"{self.sources['pubmed']}/efetch.fcgi"
                        fetch_params = {
                            'db': 'pubmed',
                            'id': pmid,
                            'retmode': 'xml'
                        }
                        
                        fetch_response = requests.get(fetch_url, params=fetch_params, verify=False, timeout=10)
                        
                        if fetch_response.status_code == 200:
                            import xml.etree.ElementTree as ET
                            root = ET.fromstring(fetch_response.content)
                            
                            abstract = root.find('.//AbstractText')
                            if abstract is not None and abstract.text:
                                title = root.find('.//ArticleTitle')
                                title_text = title.text if title is not None else 'N/A'
                                
                                clean_abstract = self.clean_abstract(abstract.text)
                                return {
                                    'source': 'pubmed',
                                    'abstract': clean_abstract,
                                    'success': True,
                                    'title': title_text,
                                    'quality_score': 8
                                }
            
            return {'source': 'pubmed', 'abstract': 'N/A', 'success': False}
            
        except Exception as e:
            return {'source': 'pubmed', 'abstract': 'N/A', 'success': False}
    
    def get_abstract_from_semantic_scholar(self, doi: str) -> Dict:
        """Semantic Scholar API로 초록 가져오기"""
        if not doi or doi == 'N/A':
            return {'source': 'semantic_scholar', 'abstract': 'N/A', 'success': False}
        
        url = f"{self.sources['semantic_scholar']}/paper/{doi}"
        
        try:
            response = requests.get(url, verify=False, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                abstract = data.get('abstract', 'N/A')
                if abstract and abstract != 'N/A':
                    clean_abstract = self.clean_abstract(abstract)
                    return {
                        'source': 'semantic_scholar',
                        'abstract': clean_abstract,
                        'success': True,
                        'title': data.get('title', 'N/A'),
                        'quality_score': 7
                    }
            
            return {'source': 'semantic_scholar', 'abstract': 'N/A', 'success': False}
            
        except Exception as e:
            return {'source': 'semantic_scholar', 'abstract': 'N/A', 'success': False}
    
    def get_best_abstract(self, doi: str) -> Dict:
        """모든 소스에서 최고 품질의 초록 가져오기"""
        results = []
        
        sources = [
            ('crossref', self.get_abstract_from_crossref),
            ('pubmed', self.get_abstract_from_pubmed),
            ('semantic_scholar', self.get_abstract_from_semantic_scholar)
        ]
        
        for source_name, source_func in sources:
            result = source_func(doi)
            if result['success']:
                results.append(result)
            time.sleep(0.3)  # API 호출 간격
        
        # 품질 점수로 정렬하여 최고 품질 반환
        if results:
            best_result = max(results, key=lambda x: x.get('quality_score', 0))
            return best_result
        
        return {'source': 'none', 'abstract': 'N/A', 'success': False}
    
    def search_papers_with_abstracts(self, query: str, count: int = 10) -> List[Dict]:
        """키워드로 논문 검색하고 초록 가져오기"""
        
        print(f"\n🔍 키워드 '{query}'로 논문 검색 중...")
        
        results = self.search_scopus(query=query, count=count, start=0)
        
        if results and 'search-results' in results:
            total_results = results['search-results'].get('opensearch:totalResults', 0)
            entries = results['search-results'].get('entry', [])
            
            print(f"✅ 검색 성공! 총 {total_results}개 결과")
            print(f"현재 페이지: {len(entries)}개 논문 처리 중...")
            print()
            
            papers = []
            for i, entry in enumerate(entries, 1):
                doi = entry.get('prism:doi', 'N/A')
                
                print(f"[{i}/{len(entries)}] {entry.get('dc:title', 'N/A')}")
                print(f"    저자: {entry.get('dc:creator', 'N/A')}")
                print(f"    저널: {entry.get('prism:publicationName', 'N/A')}")
                print(f"    발행일: {entry.get('prism:coverDate', 'N/A')}")
                print(f"    인용: {entry.get('citedby-count', 0)}")
                print(f"    DOI: {doi}")
                
                # 초록 가져오기
                if doi != 'N/A':
                    print("    초록 검색 중...", end="")
                    abstract_result = self.get_best_abstract(doi)
                    
                    if abstract_result['success']:
                        print(f" ✅ ({abstract_result['source']})")
                        abstract = abstract_result['abstract']
                    else:
                        print(" ❌")
                        abstract = 'N/A'
                else:
                    print("    DOI 없음 - 초록 검색 불가")
                    abstract = 'N/A'
                
                paper = {
                    'title': entry.get('dc:title', 'N/A'),
                    'authors': entry.get('dc:creator', 'N/A'),
                    'publication_name': entry.get('prism:publicationName', 'N/A'),
                    'publication_date': entry.get('prism:coverDate', 'N/A'),
                    'doi': doi,
                    'cited_by_count': entry.get('citedby-count', 0),
                    'scopus_id': entry.get('dc:identifier', '').replace('SCOPUS_ID:', ''),
                    'scopus_url': f"https://www.scopus.com/inward/record.uri?eid={entry.get('eid', '')}",
                    'abstract': abstract,
                    'abstract_source': abstract_result.get('source', 'N/A')
                }
                papers.append(paper)
                
                print("-" * 60)
                time.sleep(0.5)  # 처리 간격
            
            return papers
        else:
            print("❌ 검색 실패")
            return []
    
    def save_to_csv(self, papers: List[Dict], filename: str = None):
        """결과를 CSV 파일로 저장"""
        
        if not papers:
            print("저장할 결과가 없습니다.")
            return
        
        if not filename:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"abstract_search_{timestamp}.csv"
        
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
                'Abstract': paper['abstract'],
                'Abstract_Source': paper['abstract_source']
            })
        
        df = pd.DataFrame(df_data)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\n✅ 결과가 '{filename}' 파일로 저장되었습니다.")
        return filename

def main():
    """메인 함수"""
    
    print("🔍 인터랙티브 초록 검색 시스템")
    print("=" * 60)
    print("특징:")
    print("1. 사용자 키워드 입력")
    print("2. Scopus 검색 + 다중 소스 초록 가져오기")
    print("3. 품질 기반 초록 선택")
    print("4. CSV 파일로 결과 저장")
    print("=" * 60)
    
    # API 키 설정
    api_key = "920a284740d2c60fc3249e6e795e928c"
    client = InteractiveAbstractSearch(api_key)
    
    try:
        while True:
            print("\n" + "=" * 60)
            
            # 키워드 입력
            query = input("검색할 키워드를 입력하세요 (종료: 'quit'): ").strip()
            
            if query.lower() == 'quit':
                print("프로그램을 종료합니다.")
                break
            
            if not query:
                print("키워드를 입력해주세요.")
                continue
            
            # 검색 결과 수 입력
            try:
                count = input("검색할 논문 수를 입력하세요 (기본: 10): ").strip()
                count = int(count) if count else 10
                if count <= 0 or count > 50:
                    print("1-50 사이의 숫자를 입력해주세요. 기본값 10을 사용합니다.")
                    count = 10
            except ValueError:
                print("올바른 숫자를 입력해주세요. 기본값 10을 사용합니다.")
                count = 10
            
            # 논문 검색 및 초록 가져오기
            papers = client.search_papers_with_abstracts(query, count)
            
            if papers:
                print(f"\n✅ 검색 완료! {len(papers)}개의 논문을 찾았습니다.")
                
                # 초록이 있는 논문 수 계산
                papers_with_abstract = sum(1 for paper in papers if paper['abstract'] != 'N/A')
                print(f"초록이 있는 논문: {papers_with_abstract}개")
                
                # 저장 여부 확인
                save_choice = input("\n결과를 CSV 파일로 저장하시겠습니까? (y/n): ").strip().lower()
                if save_choice == 'y':
                    filename = input("파일명을 입력하세요 (기본: 자동생성): ").strip()
                    if not filename:
                        timestamp = time.strftime("%Y%m%d_%H%M%S")
                        filename = f"abstract_search_{query.replace(' ', '_')}_{timestamp}.csv"
                    
                    client.save_to_csv(papers, filename)
                
                # 계속 검색할지 확인
                continue_choice = input("\n다른 키워드로 검색하시겠습니까? (y/n): ").strip().lower()
                if continue_choice != 'y':
                    print("프로그램을 종료합니다.")
                    break
            else:
                print("❌ 검색 결과가 없습니다.")
                continue
                
    except KeyboardInterrupt:
        print("\n\n사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main() 