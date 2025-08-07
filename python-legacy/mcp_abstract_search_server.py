#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP (Model Context Protocol) 초록 검색 도구 - 완전한 서버 버전
LLM이 사용할 수 있는 논문 검색 및 초록 가져오기 도구
"""

import asyncio
import json
import time
import pandas as pd
import urllib3
import re
from typing import Dict, List, Optional, Any
from urllib.parse import quote

# SSL 경고 비활성화
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class MCPAbstractSearchTool:
    """MCP 초록 검색 도구"""
    
    def __init__(self):
        self.scopus_api_key = "920a284740d2c60fc3249e6e795e928c"
        self.scopus_url = "https://api.elsevier.com/content/search/scopus"
        self.sources = {
            'crossref': 'https://api.crossref.org/works',
            'pubmed': 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils',
            'semantic_scholar': 'https://api.semanticscholar.org/v1'
        }
        
        self.headers = {
            'Accept': 'application/json',
            'X-ELS-APIKey': self.scopus_api_key
        }
    
    def clean_abstract(self, abstract: str) -> str:
        """초록 텍스트 정리"""
        if not abstract or abstract == 'N/A':
            return 'N/A'
        
        # HTML 태그 제거
        clean_text = re.sub(r'<[^>]+>', '', abstract)
        clean_text = re.sub(r'<jats:[^>]+>', '', clean_text)
        clean_text = re.sub(r'</jats:[^>]+>', '', clean_text)
        
        # 특수 문자 정리
        clean_text = re.sub(r'\s+', ' ', clean_text)
        clean_text = clean_text.strip()
        
        # 길이 제한 (500자)
        if len(clean_text) > 500:
            clean_text = clean_text[:500] + "..."
        
        return clean_text
    
    def search_scopus(self, query: str, count: int = 10) -> Dict:
        """Scopus 검색"""
        params = {
            'query': query,
            'count': count,
            'start': 0,
            'apiKey': self.scopus_api_key
        }
        
        try:
            import requests
            response = requests.get(self.scopus_url, headers=self.headers, params=params, verify=False)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {}
                
        except Exception as e:
            return {}
    
    def get_abstract_from_crossref(self, doi: str) -> Dict:
        """Crossref API로 초록 가져오기"""
        if not doi or doi == 'N/A':
            return {'source': 'crossref', 'abstract': 'N/A', 'success': False}
        
        url = f"{self.sources['crossref']}/{doi}"
        
        try:
            import requests
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
            import requests
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
    
    def get_best_abstract(self, doi: str) -> Dict:
        """최고 품질의 초록 가져오기"""
        results = []
        
        sources = [
            ('crossref', self.get_abstract_from_crossref),
            ('pubmed', self.get_abstract_from_pubmed)
        ]
        
        for source_name, source_func in sources:
            result = source_func(doi)
            if result['success']:
                results.append(result)
            time.sleep(0.3)
        
        if results:
            best_result = max(results, key=lambda x: x.get('quality_score', 0))
            return best_result
        
        return {'source': 'none', 'abstract': 'N/A', 'success': False}
    
    def search_papers_with_abstracts(self, query: str, count: int = 10) -> List[Dict]:
        """키워드로 논문 검색하고 초록 가져오기"""
        results = self.search_scopus(query=query, count=count)
        
        if results and 'search-results' in results:
            total_results = results['search-results'].get('opensearch:totalResults', 0)
            entries = results['search-results'].get('entry', [])
            
            papers = []
            for entry in entries:
                doi = entry.get('prism:doi', 'N/A')
                
                # 초록 가져오기
                if doi != 'N/A':
                    abstract_result = self.get_best_abstract(doi)
                    abstract = abstract_result['abstract'] if abstract_result['success'] else 'N/A'
                else:
                    abstract = 'N/A'
                    abstract_result = {'source': 'N/A'}
                
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
            
            return papers
        else:
            return []

# MCP 서버 설정
tool = MCPAbstractSearchTool()

# MCP 서버 생성 (간단한 버전)
class MCPServer:
    def __init__(self):
        self.tool = MCPAbstractSearchTool()
    
    async def list_tools(self):
        """사용 가능한 도구 목록 반환"""
        return [
            {
                "name": "search_papers",
                "description": "키워드로 논문을 검색하고 초록을 가져옵니다.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "검색할 키워드"
                        },
                        "count": {
                            "type": "integer",
                            "description": "검색할 논문 수 (기본값: 10, 최대: 50)",
                            "default": 10
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "get_abstract_by_doi",
                "description": "DOI로 특정 논문의 초록을 가져옵니다.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "doi": {
                            "type": "string",
                            "description": "논문의 DOI"
                        }
                    },
                    "required": ["doi"]
                }
            }
        ]
    
    async def call_tool(self, name: str, arguments: dict):
        """도구 호출"""
        if name == "search_papers":
            return await self.search_papers_tool(arguments)
        elif name == "get_abstract_by_doi":
            return await self.get_abstract_by_doi_tool(arguments)
        else:
            return [{"type": "text", "text": f"알 수 없는 도구: {name}"}]
    
    async def search_papers_tool(self, arguments: dict):
        """논문 검색 도구"""
        query = arguments.get("query", "")
        count = arguments.get("count", 10)
        
        if not query:
            return [{"type": "text", "text": "검색할 키워드를 입력해주세요."}]
        
        papers = self.tool.search_papers_with_abstracts(query, count)
        
        if not papers:
            return [{"type": "text", "text": f"'{query}' 키워드로 검색된 논문이 없습니다."}]
        
        # 결과를 JSON 형태로 반환
        result_text = f"'{query}' 키워드로 {len(papers)}개 논문을 찾았습니다:\n\n"
        
        for i, paper in enumerate(papers, 1):
            result_text += f"[{i}] {paper['title']}\n"
            result_text += f"저자: {paper['authors']}\n"
            result_text += f"저널: {paper['publication_name']}\n"
            result_text += f"발행일: {paper['publication_date']}\n"
            result_text += f"인용: {paper['cited_by_count']}\n"
            result_text += f"DOI: {paper['doi']}\n"
            
            if paper['abstract'] != 'N/A':
                result_text += f"초록 ({paper['abstract_source']}): {paper['abstract']}\n"
            else:
                result_text += "초록: 없음\n"
            
            result_text += f"Scopus URL: {paper['scopus_url']}\n"
            result_text += "-" * 50 + "\n"
        
        return [{"type": "text", "text": result_text}]
    
    async def get_abstract_by_doi_tool(self, arguments: dict):
        """DOI로 초록 가져오기 도구"""
        doi = arguments.get("doi", "")
        
        if not doi:
            return [{"type": "text", "text": "DOI를 입력해주세요."}]
        
        abstract_result = self.tool.get_best_abstract(doi)
        
        if abstract_result['success']:
            result_text = f"DOI: {doi}\n"
            result_text += f"제목: {abstract_result.get('title', 'N/A')}\n"
            result_text += f"초록 소스: {abstract_result['source']}\n"
            result_text += f"초록: {abstract_result['abstract']}\n"
        else:
            result_text = f"DOI '{doi}'에 대한 초록을 찾을 수 없습니다."
        
        return [{"type": "text", "text": result_text}]

# 간단한 테스트 함수
def test_mcp_server():
    """MCP 서버 테스트"""
    print("🔍 MCP 서버 테스트")
    print("=" * 50)
    
    server = MCPServer()
    
    # 도구 목록 테스트
    print("1. 도구 목록:")
    tools = asyncio.run(server.list_tools())
    for tool in tools:
        print(f"  - {tool['name']}: {tool['description']}")
    
    # 검색 테스트
    print("\n2. 검색 테스트:")
    result = asyncio.run(server.search_papers_tool({"query": "artificial intelligence", "count": 2}))
    print(result[0]['text'][:200] + "...")
    
    # DOI 테스트
    print("\n3. DOI 테스트:")
    result = asyncio.run(server.get_abstract_by_doi_tool({"doi": "10.1016/S0014-5793(01)03313-0"}))
    print(result[0]['text'][:200] + "...")

if __name__ == "__main__":
    test_mcp_server() 