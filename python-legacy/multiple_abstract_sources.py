#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
다양한 API 소스를 활용한 초록 가져오기 시스템
1. Crossref API
2. arXiv API (무료)
3. PubMed API (무료)
4. Semantic Scholar API (무료)
5. OpenAlex API (무료)
6. Unpaywall API (무료)
"""

import requests
import json
import time
import pandas as pd
import urllib3
from typing import Dict, List, Optional
from urllib.parse import quote

# SSL 경고 비활성화
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class MultipleAbstractSources:
    """다양한 API 소스를 활용한 초록 가져오기 클래스"""
    
    def __init__(self):
        self.sources = {
            'crossref': 'https://api.crossref.org/works',
            'arxiv': 'http://export.arxiv.org/api/query',
            'pubmed': 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils',
            'semantic_scholar': 'https://api.semanticscholar.org/v1',
            'openalex': 'https://api.openalex.org',
            'unpaywall': 'https://api.unpaywall.org/v2'
        }
    
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
                        return {
                            'source': 'crossref',
                            'abstract': abstract,
                            'success': True,
                            'title': message.get('title', ['N/A'])[0] if message.get('title') else 'N/A'
                        }
            
            return {'source': 'crossref', 'abstract': 'N/A', 'success': False}
            
        except Exception as e:
            print(f"Crossref API 오류: {e}")
            return {'source': 'crossref', 'abstract': 'N/A', 'success': False}
    
    def get_abstract_from_arxiv(self, doi: str) -> Dict:
        """arXiv API로 초록 가져오기 (DOI 기반 검색)"""
        if not doi or doi == 'N/A':
            return {'source': 'arxiv', 'abstract': 'N/A', 'success': False}
        
        # DOI를 arXiv 검색 쿼리로 변환
        query = f"doi:{doi}"
        url = f"{self.sources['arxiv']}?search_query={quote(query)}&start=0&max_results=1"
        
        try:
            response = requests.get(url, verify=False, timeout=10)
            
            if response.status_code == 200:
                # arXiv는 XML 응답
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.content)
                
                # 초록 찾기
                for entry in root.findall('.//{http://www.w3.org/2005/Atom}entry'):
                    summary = entry.find('.//{http://www.w3.org/2005/Atom}summary')
                    if summary is not None and summary.text:
                        title = entry.find('.//{http://www.w3.org/2005/Atom}title')
                        title_text = title.text if title is not None else 'N/A'
                        
                        return {
                            'source': 'arxiv',
                            'abstract': summary.text,
                            'success': True,
                            'title': title_text
                        }
            
            return {'source': 'arxiv', 'abstract': 'N/A', 'success': False}
            
        except Exception as e:
            print(f"arXiv API 오류: {e}")
            return {'source': 'arxiv', 'abstract': 'N/A', 'success': False}
    
    def get_abstract_from_pubmed(self, doi: str) -> Dict:
        """PubMed API로 초록 가져오기"""
        if not doi or doi == 'N/A':
            return {'source': 'pubmed', 'abstract': 'N/A', 'success': False}
        
        # DOI로 PubMed ID 찾기
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
                        
                        # PubMed ID로 상세 정보 가져오기
                        fetch_url = f"{self.sources['pubmed']}/efetch.fcgi"
                        fetch_params = {
                            'db': 'pubmed',
                            'id': pmid,
                            'retmode': 'xml'
                        }
                        
                        fetch_response = requests.get(fetch_url, params=fetch_params, verify=False, timeout=10)
                        
                        if fetch_response.status_code == 200:
                            # XML 파싱
                            import xml.etree.ElementTree as ET
                            root = ET.fromstring(fetch_response.content)
                            
                            # 초록 찾기
                            abstract = root.find('.//AbstractText')
                            if abstract is not None and abstract.text:
                                title = root.find('.//ArticleTitle')
                                title_text = title.text if title is not None else 'N/A'
                                
                                return {
                                    'source': 'pubmed',
                                    'abstract': abstract.text,
                                    'success': True,
                                    'title': title_text
                                }
            
            return {'source': 'pubmed', 'abstract': 'N/A', 'success': False}
            
        except Exception as e:
            print(f"PubMed API 오류: {e}")
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
                    return {
                        'source': 'semantic_scholar',
                        'abstract': abstract,
                        'success': True,
                        'title': data.get('title', 'N/A')
                    }
            
            return {'source': 'semantic_scholar', 'abstract': 'N/A', 'success': False}
            
        except Exception as e:
            print(f"Semantic Scholar API 오류: {e}")
            return {'source': 'semantic_scholar', 'abstract': 'N/A', 'success': False}
    
    def get_abstract_from_openalex(self, doi: str) -> Dict:
        """OpenAlex API로 초록 가져오기"""
        if not doi or doi == 'N/A':
            return {'source': 'openalex', 'abstract': 'N/A', 'success': False}
        
        url = f"{self.sources['openalex']}/works/doi:{doi}"
        
        try:
            response = requests.get(url, verify=False, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                abstract = data.get('abstract_inverted_index', {})
                if abstract:
                    # 역인덱스를 텍스트로 변환
                    abstract_text = self._convert_inverted_index_to_text(abstract)
                    
                    if abstract_text:
                        return {
                            'source': 'openalex',
                            'abstract': abstract_text,
                            'success': True,
                            'title': data.get('title', 'N/A')
                        }
            
            return {'source': 'openalex', 'abstract': 'N/A', 'success': False}
            
        except Exception as e:
            print(f"OpenAlex API 오류: {e}")
            return {'source': 'openalex', 'abstract': 'N/A', 'success': False}
    
    def _convert_inverted_index_to_text(self, inverted_index: Dict) -> str:
        """역인덱스를 텍스트로 변환"""
        try:
            # 위치 정보를 정렬하여 텍스트 재구성
            words = []
            for word, positions in inverted_index.items():
                for pos in positions:
                    words.append((pos, word))
            
            words.sort(key=lambda x: x[0])
            return ' '.join([word for _, word in words])
        except:
            return ''
    
    def get_abstract_from_unpaywall(self, doi: str) -> Dict:
        """Unpaywall API로 초록 가져오기"""
        if not doi or doi == 'N/A':
            return {'source': 'unpaywall', 'abstract': 'N/A', 'success': False}
        
        url = f"{self.sources['unpaywall']}/{doi}"
        
        try:
            response = requests.get(url, verify=False, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                abstract = data.get('abstract', 'N/A')
                if abstract and abstract != 'N/A':
                    return {
                        'source': 'unpaywall',
                        'abstract': abstract,
                        'success': True,
                        'title': data.get('title', 'N/A')
                    }
            
            return {'source': 'unpaywall', 'abstract': 'N/A', 'success': False}
            
        except Exception as e:
            print(f"Unpaywall API 오류: {e}")
            return {'source': 'unpaywall', 'abstract': 'N/A', 'success': False}
    
    def get_abstract_from_all_sources(self, doi: str) -> Dict:
        """모든 소스에서 초록 가져오기 시도"""
        print(f"\n🔍 DOI '{doi}'에 대한 모든 소스에서 초록 검색 중...")
        
        results = {}
        
        # 각 소스에서 시도
        sources = [
            ('crossref', self.get_abstract_from_crossref),
            ('arxiv', self.get_abstract_from_arxiv),
            ('pubmed', self.get_abstract_from_pubmed),
            ('semantic_scholar', self.get_abstract_from_semantic_scholar),
            ('openalex', self.get_abstract_from_openalex),
            ('unpaywall', self.get_abstract_from_unpaywall)
        ]
        
        for source_name, source_func in sources:
            print(f"  {source_name}에서 검색 중...", end="")
            result = source_func(doi)
            results[source_name] = result
            
            if result['success']:
                print(" ✅")
                print(f"    제목: {result.get('title', 'N/A')}")
                abstract = result['abstract']
                if len(abstract) > 200:
                    abstract = abstract[:200] + "..."
                print(f"    초록: {abstract}")
            else:
                print(" ❌")
            
            time.sleep(0.5)  # API 호출 간격
        
        # 성공한 결과 중 첫 번째 반환
        for source_name, result in results.items():
            if result['success']:
                return result
        
        return {'source': 'none', 'abstract': 'N/A', 'success': False}

def test_all_abstract_sources():
    """모든 초록 소스 테스트"""
    
    client = MultipleAbstractSources()
    
    # 테스트용 DOI들
    test_dois = [
        "10.1016/S0014-5793(01)03313-0",  # Crossref에서 성공한 DOI
        "10.1002/deo2.70150",              # AI Endoscopy 논문
        "10.1016/j.scico.2025.103365",     # WEST 논문
        "10.1038/nature12373",             # Nature 논문
        "10.1126/science.1234567"          # Science 논문
    ]
    
    print("🔍 모든 초록 소스 테스트")
    print("=" * 80)
    
    for i, doi in enumerate(test_dois, 1):
        print(f"\n[{i}] DOI: {doi}")
        print("=" * 60)
        
        result = client.get_abstract_from_all_sources(doi)
        
        if result['success']:
            print(f"\n✅ 성공! 소스: {result['source']}")
            print(f"제목: {result.get('title', 'N/A')}")
            abstract = result['abstract']
            if len(abstract) > 300:
                abstract = abstract[:300] + "..."
            print(f"초록: {abstract}")
        else:
            print(f"\n❌ 모든 소스에서 초록을 찾을 수 없습니다.")
        
        print("-" * 60)

def main():
    """메인 함수"""
    
    print("🔍 다양한 API 소스를 활용한 초록 가져오기 시스템")
    print("=" * 80)
    print("사용 가능한 소스:")
    print("1. Crossref API - DOI 기반 메타데이터")
    print("2. arXiv API - 무료 논문 아카이브")
    print("3. PubMed API - 생의학 논문 데이터베이스")
    print("4. Semantic Scholar API - AI 기반 논문 분석")
    print("5. OpenAlex API - 학술 데이터베이스")
    print("6. Unpaywall API - 오픈 액세스 정보")
    print("=" * 80)
    
    try:
        test_all_abstract_sources()
        
    except KeyboardInterrupt:
        print("\n\n사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main() 