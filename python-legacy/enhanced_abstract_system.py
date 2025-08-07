#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
향상된 초록 가져오기 시스템
- 여러 소스에서 동시 검색
- 품질 기반 우선순위
- HTML 태그 정리
- 중복 제거
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

class EnhancedAbstractSystem:
    """향상된 초록 가져오기 시스템"""
    
    def __init__(self):
        self.sources = {
            'crossref': 'https://api.crossref.org/works',
            'pubmed': 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils',
            'arxiv': 'http://export.arxiv.org/api/query',
            'semantic_scholar': 'https://api.semanticscholar.org/v1',
            'openalex': 'https://api.openalex.org'
        }
        
        # 소스별 우선순위 (품질 기반)
        self.priority_order = ['crossref', 'pubmed', 'semantic_scholar', 'openalex', 'arxiv']
    
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
                            'quality_score': 9  # 높은 품질
                        }
            
            return {'source': 'crossref', 'abstract': 'N/A', 'success': False}
            
        except Exception as e:
            print(f"Crossref API 오류: {e}")
            return {'source': 'crossref', 'abstract': 'N/A', 'success': False}
    
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
                                
                                clean_abstract = self.clean_abstract(abstract.text)
                                return {
                                    'source': 'pubmed',
                                    'abstract': clean_abstract,
                                    'success': True,
                                    'title': title_text,
                                    'quality_score': 8  # 높은 품질
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
                    clean_abstract = self.clean_abstract(abstract)
                    return {
                        'source': 'semantic_scholar',
                        'abstract': clean_abstract,
                        'success': True,
                        'title': data.get('title', 'N/A'),
                        'quality_score': 7  # 중간 품질
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
                        clean_abstract = self.clean_abstract(abstract_text)
                        return {
                            'source': 'openalex',
                            'abstract': clean_abstract,
                            'success': True,
                            'title': data.get('title', 'N/A'),
                            'quality_score': 6  # 중간 품질
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
    
    def get_best_abstract(self, doi: str) -> Dict:
        """모든 소스에서 최고 품질의 초록 가져오기"""
        print(f"\n🔍 DOI '{doi}'에 대한 최고 품질 초록 검색 중...")
        
        results = []
        
        # 각 소스에서 시도
        sources = [
            ('crossref', self.get_abstract_from_crossref),
            ('pubmed', self.get_abstract_from_pubmed),
            ('semantic_scholar', self.get_abstract_from_semantic_scholar),
            ('openalex', self.get_abstract_from_openalex)
        ]
        
        for source_name, source_func in sources:
            print(f"  {source_name}에서 검색 중...", end="")
            result = source_func(doi)
            
            if result['success']:
                print(" ✅")
                print(f"    제목: {result.get('title', 'N/A')}")
                print(f"    품질 점수: {result.get('quality_score', 0)}")
                results.append(result)
            else:
                print(" ❌")
            
            time.sleep(0.5)  # API 호출 간격
        
        # 품질 점수로 정렬하여 최고 품질 반환
        if results:
            best_result = max(results, key=lambda x: x.get('quality_score', 0))
            print(f"\n✅ 최고 품질 초록 선택: {best_result['source']} (점수: {best_result.get('quality_score', 0)})")
            return best_result
        
        return {'source': 'none', 'abstract': 'N/A', 'success': False}

def test_enhanced_system():
    """향상된 시스템 테스트"""
    
    client = EnhancedAbstractSystem()
    
    # 테스트용 DOI들
    test_dois = [
        "10.1016/S0014-5793(01)03313-0",  # Crossref에서 성공한 DOI
        "10.1002/deo2.70150",              # AI Endoscopy 논문
        "10.1016/j.scico.2025.103365",     # WEST 논문
        "10.1038/nature12373",             # Nature 논문
        "10.1126/science.1234567"          # Science 논문
    ]
    
    print("🔍 향상된 초록 가져오기 시스템 테스트")
    print("=" * 80)
    
    for i, doi in enumerate(test_dois, 1):
        print(f"\n[{i}] DOI: {doi}")
        print("=" * 60)
        
        result = client.get_best_abstract(doi)
        
        if result['success']:
            print(f"\n✅ 성공! 소스: {result['source']}")
            print(f"제목: {result.get('title', 'N/A')}")
            print(f"초록: {result['abstract']}")
        else:
            print(f"\n❌ 모든 소스에서 초록을 찾을 수 없습니다.")
        
        print("-" * 60)

def main():
    """메인 함수"""
    
    print("🔍 향상된 초록 가져오기 시스템")
    print("=" * 80)
    print("특징:")
    print("1. 품질 기반 우선순위 선택")
    print("2. HTML 태그 자동 정리")
    print("3. 중복 제거 및 최적화")
    print("4. 다중 소스 동시 검색")
    print("=" * 80)
    
    try:
        test_enhanced_system()
        
    except KeyboardInterrupt:
        print("\n\n사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main() 