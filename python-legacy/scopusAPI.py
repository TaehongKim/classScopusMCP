#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scopus API를 활용한 Usability 논문 검색 예제
기반 문서: Elsevier Scopus APIs Getting Started Guide Version 1 (September 2023)
"""

import requests
import json
import time
from typing import Dict, List, Optional
import pandas as pd


class ScopusAPIClient:
    """Scopus API 클라이언트 클래스"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.elsevier.com"):
        """
        Scopus API 클라이언트 초기화
        
        Args:
            api_key (str): Elsevier API Key
            base_url (str): API 기본 URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            'Accept': 'application/json',
            'X-ELS-APIKey': api_key
        }
    
    def search_scopus(self, query: str, count: int = 25, start: int = 0, 
                     view: str = "STANDARD", sort: str = "relevancy") -> Dict:
        """
        Scopus Search API를 사용하여 논문 검색
        
        Args:
            query (str): 검색 쿼리
            count (int): 반환할 결과 수 (최대 200)
            start (int): 시작 위치 (기본값: 0)
            view (str): 응답 뷰 (STANDARD 또는 COMPLETE)
            sort (str): 정렬 방식 (relevancy, citedby-count, coverDate 등)
            
        Returns:
            Dict: API 응답 데이터
        """
        endpoint = f"{self.base_url}/content/search/scopus"
        
        params = {
            'query': query,
            'count': count,
            'start': start,
            'view': view,
            'sort': sort,
            'apiKey': self.api_key
        }
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            
            # Rate limit 처리 (문서에 따르면 throttling 제한 있음)
            if response.status_code == 429:
                print("Rate limit exceeded. Waiting 60 seconds...")
                time.sleep(60)
                response = requests.get(endpoint, headers=self.headers, params=params)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"API 요청 오류: {e}")
            return {}
    
    def get_abstract_details(self, scopus_id: str) -> Dict:
        """
        Abstract Retrieval API를 사용하여 논문 상세 정보 조회
        
        Args:
            scopus_id (str): Scopus 문서 ID
            
        Returns:
            Dict: 논문 상세 정보
        """
        endpoint = f"{self.base_url}/content/abstract/scopus_id/{scopus_id}"
        
        params = {
            'apiKey': self.api_key,
            'view': 'FULL'
        }
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Abstract 조회 오류: {e}")
            return {}
    
    def get_citation_count(self, doi: str) -> Dict:
        """
        Citation Count API를 사용하여 인용 횟수 조회
        
        Args:
            doi (str): 논문의 DOI
            
        Returns:
            Dict: 인용 정보
        """
        endpoint = f"{self.base_url}/content/abstract/citation-count"
        
        params = {
            'doi': doi,
            'apiKey': self.api_key
        }
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Citation count 조회 오류: {e}")
            return {}


def get_user_search_inputs():
    """사용자로부터 검색 조건을 입력받는 함수"""
    print("\n🔍 논문 검색 조건을 입력해주세요")
    print("=" * 50)
    
    # 키워드 입력
    print("\n1. 검색 키워드 입력:")
    print("   - 여러 키워드는 쉼표(,)로 구분해주세요")
    print("   - 예: usability, user experience, UX")
    keywords = input("   키워드: ").strip()
    
    if not keywords:
        keywords = "usability"
        print(f"   기본값 사용: {keywords}")
    
    # 연도 범위 입력
    print("\n2. 발행 연도 범위:")
    print("   - 시작 연도만 입력하면 해당 연도 이후 모든 논문")
    print("   - 범위 입력 예: 2020-2024")
    year_input = input("   연도 (기본값: 2020): ").strip()
    
    if not year_input:
        year_filter = "PUBYEAR > 2019"
        print("   기본값 사용: 2020년 이후")
    elif "-" in year_input:
        try:
            start_year, end_year = map(int, year_input.split("-"))
            year_filter = f"PUBYEAR > {start_year-1} AND PUBYEAR < {end_year+1}"
            print(f"   설정: {start_year}년 ~ {end_year}년")
        except ValueError:
            year_filter = "PUBYEAR > 2019"
            print("   잘못된 형식입니다. 기본값 사용: 2020년 이후")
    else:
        try:
            start_year = int(year_input)
            year_filter = f"PUBYEAR > {start_year-1}"
            print(f"   설정: {start_year}년 이후")
        except ValueError:
            year_filter = "PUBYEAR > 2019"
            print("   잘못된 형식입니다. 기본값 사용: 2020년 이후")
    
    # 언어 선택
    print("\n3. 논문 언어:")
    print("   1) 영어만 (기본값)")
    print("   2) 모든 언어")
    lang_choice = input("   선택 (1 또는 2): ").strip()
    
    if lang_choice == "2":
        lang_filter = ""
        print("   설정: 모든 언어")
    else:
        lang_filter = "AND LANGUAGE(english)"
        print("   설정: 영어만")
    
    # 검색할 논문 수
    print("\n4. 검색할 논문 수:")
    print("   - 최대 200개까지 가능")
    count_input = input("   논문 수 (기본값: 25): ").strip()
    
    try:
        count = int(count_input) if count_input else 25
        count = min(count, 200)  # 최대 200개로 제한
        print(f"   설정: {count}개")
    except ValueError:
        count = 25
        print("   잘못된 형식입니다. 기본값 사용: 25개")
    
    # 정렬 방식
    print("\n5. 정렬 방식:")
    print("   1) 관련도순 (기본값)")
    print("   2) 최신순")
    print("   3) 인용횟수순")
    sort_choice = input("   선택 (1, 2, 또는 3): ").strip()
    
    sort_options = {
        "1": ("relevancy", "관련도순"),
        "2": ("-coverDate", "최신순"),
        "3": ("-citedby-count", "인용횟수순")
    }
    
    sort_key, sort_desc = sort_options.get(sort_choice, ("relevancy", "관련도순"))
    print(f"   설정: {sort_desc}")
    
    return keywords, year_filter, lang_filter, count, sort_key


def build_search_query(keywords: str, year_filter: str, lang_filter: str) -> str:
    """검색 쿼리를 구성하는 함수"""
    
    # 키워드 처리 - 쉼표로 구분된 키워드들을 OR로 연결
    keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]
    
    if len(keyword_list) == 1:
        keyword_query = f'TITLE-ABS-KEY({keyword_list[0]})'
    else:
        # 각 키워드를 따옴표로 감싸고 OR로 연결
        formatted_keywords = []
        for keyword in keyword_list:
            if " " in keyword:  # 공백이 있는 키워드는 따옴표로 감싸기
                formatted_keywords.append(f'"{keyword}"')
            else:
                formatted_keywords.append(keyword)
        keyword_query = f'TITLE-ABS-KEY({" OR ".join(formatted_keywords)})'
    
    # 전체 쿼리 조합
    query_parts = [keyword_query, year_filter]
    if lang_filter:
        query_parts.append(lang_filter)
    
    return " ".join(query_parts)


def search_papers_with_user_input(api_key: str) -> List[Dict]:
    """
    사용자 입력을 받아 논문을 검색하고 결과를 반환
    
    Args:
        api_key (str): Scopus API Key
        
    Returns:
        List[Dict]: 검색된 논문 리스트
    """
    client = ScopusAPIClient(api_key)
    
    # 사용자 입력 받기
    keywords, year_filter, lang_filter, count, sort_key = get_user_search_inputs()
    
    # 검색 쿼리 구성
    query = build_search_query(keywords, year_filter, lang_filter)
    
    print(f"\n검색 쿼리: {query}")
    print("-" * 80)
    
    # 사용자 설정에 따른 검색 실행
    results = client.search_scopus(
        query=query,
        count=count,
        start=0,
        view="COMPLETE",  # 더 많은 정보 포함
        sort=sort_key
    )
    
    if not results or 'search-results' not in results:
        print("검색 결과가 없습니다.")
        return []
    
    search_results = results['search-results']
    total_results = int(search_results.get('opensearch:totalResults', 0))
    
    print(f"총 검색 결과: {total_results:,}개")
    print(f"현재 페이지 결과: {len(search_results.get('entry', []))}개")
    print("-" * 80)
    
    papers = []
    
    for entry in search_results.get('entry', []):
        paper = {
            'title': entry.get('dc:title', 'N/A'),
            'authors': [],
            'publication_name': entry.get('prism:publicationName', 'N/A'),
            'publication_date': entry.get('prism:coverDate', 'N/A'),
            'doi': entry.get('prism:doi', 'N/A'),
            'scopus_id': entry.get('dc:identifier', '').replace('SCOPUS_ID:', ''),
            'cited_by_count': entry.get('citedby-count', 0),
            'abstract': entry.get('dc:description', 'N/A'),
            'subject_areas': [],
            'open_access': entry.get('openaccess', '0') == '1',
            'scopus_url': f"https://www.scopus.com/inward/record.uri?eid={entry.get('eid', '')}"
        }
        
        # 저자 정보 추출
        if 'author' in entry:
            authors = entry['author'] if isinstance(entry['author'], list) else [entry['author']]
            for author in authors:
                author_name = f"{author.get('given-name', '')} {author.get('surname', '')}".strip()
                if author_name:
                    paper['authors'].append(author_name)
        
        # 주제 분야 정보
        if 'subject-area' in entry:
            subject_areas = entry['subject-area'] if isinstance(entry['subject-area'], list) else [entry['subject-area']]
            for subject in subject_areas:
                if isinstance(subject, dict):
                    paper['subject_areas'].append(subject.get('$', ''))
                else:
                    paper['subject_areas'].append(str(subject))
        
        papers.append(paper)
        
        # API Rate limit 고려하여 잠시 대기
        time.sleep(0.5)
    
    return papers


def display_papers(papers: List[Dict], top_n: int = None):
    """검색된 논문들을 보기 좋게 출력"""
    
    if top_n is None:
        top_n = len(papers)
    
    print(f"\n=== 검색된 논문 목록 (총 {len(papers)}개 중 상위 {min(top_n, len(papers))}개) ===\n")
    
    for i, paper in enumerate(papers[:top_n], 1):
        print(f"[{i}] {paper['title']}")
        print(f"    저자: {', '.join(paper['authors'][:3])}{'...' if len(paper['authors']) > 3 else ''}")
        print(f"    저널: {paper['publication_name']}")
        print(f"    발행일: {paper['publication_date']}")
        print(f"    인용 횟수: {paper['cited_by_count']}")
        print(f"    DOI: {paper['doi']}")
        print(f"    Open Access: {'Yes' if paper['open_access'] else 'No'}")
        print(f"    주제 분야: {', '.join(paper['subject_areas'][:3])}")
        
        # 초록 요약 (처음 200자)
        abstract = paper['abstract']
        if abstract and abstract != 'N/A' and len(abstract) > 200:
            abstract = abstract[:200] + "..."
        print(f"    초록: {abstract}")
        print(f"    Scopus URL: {paper['scopus_url']}")
        print("-" * 80)


def save_to_csv(papers: List[Dict], keywords: str, filename: str = None):
    """검색 결과를 CSV 파일로 저장"""
    
    if filename is None:
        # 키워드를 파일명에 포함 (특수문자 제거)
        safe_keywords = "".join(c for c in keywords if c.isalnum() or c in (' ', '_')).strip()
        safe_keywords = safe_keywords.replace(' ', '_')[:30]  # 최대 30자
        filename = f"scopus_search_{safe_keywords}.csv"
    
    # DataFrame용 데이터 준비
    df_data = []
    for paper in papers:
        df_data.append({
            'Title': paper['title'],
            'Authors': '; '.join(paper['authors']),
            'Publication': paper['publication_name'],
            'Date': paper['publication_date'],
            'DOI': paper['doi'],
            'Scopus_ID': paper['scopus_id'],
            'Citations': paper['cited_by_count'],
            'Open_Access': paper['open_access'],
            'Subject_Areas': '; '.join(paper['subject_areas']),
            'Abstract': paper['abstract'],
            'Scopus_URL': paper['scopus_url']
        })
    
    df = pd.DataFrame(df_data)
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"\n검색 결과가 '{filename}' 파일로 저장되었습니다.")


def get_advanced_statistics(papers: List[Dict]):
    """검색 결과에 대한 통계 정보 제공"""
    
    if not papers:
        return
    
    print("\n=== 검색 결과 통계 ===")
    
    # 연도별 분포
    years = {}
    total_citations = 0
    open_access_count = 0
    
    for paper in papers:
        # 연도 추출
        date_str = paper.get('publication_date', '')
        if date_str and len(date_str) >= 4:
            year = date_str[:4]
            years[year] = years.get(year, 0) + 1
        
        # 인용 횟수 합계
        citations = paper.get('cited_by_count', 0)
        if isinstance(citations, (int, str)) and str(citations).isdigit():
            total_citations += int(citations)
        
        # Open Access 비율
        if paper.get('open_access', False):
            open_access_count += 1
    
    print(f"총 논문 수: {len(papers)}")
    print(f"총 인용 횟수: {total_citations:,}")
    print(f"평균 인용 횟수: {total_citations/len(papers):.1f}")
    print(f"Open Access 비율: {open_access_count/len(papers)*100:.1f}% ({open_access_count}/{len(papers)})")
    
    # 연도별 분포 (상위 5개년)
    if years:
        print("\n연도별 논문 수 (상위 5개년):")
        sorted_years = sorted(years.items(), key=lambda x: x[1], reverse=True)[:5]
        for year, count in sorted_years:
            print(f"  {year}: {count}편")


def main():
    """메인 실행 함수"""
    
    # API Key 설정 (실제 사용시 환경변수나 설정파일에서 읽어오세요)
    API_KEY = "920a284740d2c60fc3249e6e795e928c"  # 실제 API Key로 교체 필요
    
    if API_KEY == "YOUR_SCOPUS_API_KEY_HERE":
        print("⚠️  API Key를 설정해주세요!")
        print("Elsevier Developer Portal (https://dev.elsevier.com)에서 API Key를 발급받으세요.")
        return
    
    print("🔍 Scopus API를 사용한 논문 검색 시스템")
    print("=" * 60)
    
    try:
        # 사용자 입력을 받아 논문 검색
        papers = search_papers_with_user_input(API_KEY)
        
        if papers:
            # 결과 출력 (모든 결과 표시)
            display_papers(papers)
            
            # 통계 정보
            get_advanced_statistics(papers)
            
            # CSV 파일로 저장 (키워드 기반 파일명)
            keywords = input("\n저장용 키워드를 입력하세요 (파일명 생성용): ").strip()
            if not keywords:
                keywords = "search_results"
            save_to_csv(papers, keywords)
            
            print(f"\n✅ 검색 완료! {len(papers)}개의 논문을 찾았습니다.")
            
        else:
            print("❌ 검색 결과가 없습니다.")
            print("💡 다른 키워드나 검색 조건을 시도해보세요.")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        
        
def interactive_search_examples():
    """대화형 검색 예제 제안"""
    
    print("\n💡 검색 예제 및 팁:")
    print("-" * 40)
    
    examples = {
        "1. 기본 사용성 연구": {
            "keywords": "usability, user experience, UX",
            "years": "2020-2024",
            "description": "일반적인 사용성 연구 논문"
        },
        "2. 모바일 앱 사용성": {
            "keywords": "mobile usability, app usability, smartphone UX",
            "years": "2021",
            "description": "모바일 애플리케이션 사용성 연구"
        },
        "3. 웹 접근성": {
            "keywords": "web accessibility, digital accessibility, inclusive design",
            "years": "2020-2023",
            "description": "웹 접근성 및 포용적 디자인"
        },
        "4. 의료 시스템 UI": {
            "keywords": "healthcare UI, medical interface, clinical usability",
            "years": "2022",
            "description": "의료 분야 사용자 인터페이스"
        },
        "5. AI/ML 사용성": {
            "keywords": "AI usability, machine learning UX, explainable AI",
            "years": "2020-2024",
            "description": "인공지능 시스템의 사용성"
        }
    }
    
    for key, example in examples.items():
        print(f"{key}")
        print(f"   키워드: {example['keywords']}")
        print(f"   연도: {example['years']}")
        print(f"   설명: {example['description']}")
        print()
    
    print("🔍 검색 팁:")
    print("- 구체적인 키워드일수록 관련성 높은 결과")
    print("- 여러 키워드는 쉼표로 구분하여 OR 검색")
    print("- 연도 범위를 좁히면 더 집중된 결과")
    print("- 영어 논문이 일반적으로 더 많은 결과 제공")


# 추가된 유틸리티 함수들

def preview_search_results(api_key: str, query: str, count: int = 5):
    """검색 결과 미리보기 (제목만)"""
    
    client = ScopusAPIClient(api_key)
    results = client.search_scopus(query=query, count=count, view="STANDARD")
    
    if results and 'search-results' in results:
        entries = results['search-results'].get('entry', [])
        total = results['search-results'].get('opensearch:totalResults', 0)
        
        print(f"\n📋 검색 결과 미리보기 (총 {total}개 중 {len(entries)}개):")
        print("-" * 50)
        
        for i, entry in enumerate(entries, 1):
            title = entry.get('dc:title', 'N/A')[:100]
            year = entry.get('prism:coverDate', 'N/A')[:4]
            citations = entry.get('citedby-count', 0)
            print(f"{i}. [{year}] {title}... (인용: {citations})")
        
        return int(total)
    return 0


if __name__ == "__main__":
    # 실행 전 예제 보기 옵션
    print("🔍 Scopus 논문 검색 프로그램")
    print("1) 바로 검색 시작")
    print("2) 검색 예제 및 팁 보기")
    
    choice = input("선택하세요 (1 또는 2): ").strip()
    
    if choice == "2":
        interactive_search_examples()
        input("\n계속하려면 Enter를 누르세요...")
    
    main()


# 사용 예제 및 추가 기능들

def example_advanced_search():
    """고급 검색 예제들"""
    
    # 더 구체적인 검색 쿼리 예제들
    queries = {
        "모바일 앱 Usability": (
            'TITLE-ABS-KEY(usability AND ("mobile app" OR "mobile application" OR smartphone)) '
            'AND PUBYEAR > 2020'
        ),
        
        "웹사이트 사용성": (
            'TITLE-ABS-KEY(("web usability" OR "website usability" OR "web user experience")) '
            'AND PUBYEAR > 2019 AND PUBYEAR < 2024'
        ),
        
        "의료 시스템 사용성": (
            'TITLE-ABS-KEY(usability AND (healthcare OR medical OR "health system")) '
            'AND SUBJAREA(MEDI) AND PUBYEAR > 2021'
        ),
        
        "고령자 대상 사용성": (
            'TITLE-ABS-KEY(usability AND (elderly OR "older adult" OR senior OR aging)) '
            'AND PUBYEAR > 2020'
        )
    }
    
    return queries


def example_citation_analysis(api_key: str, doi: str):
    """특정 논문의 인용 분석 예제"""
    
    client = ScopusAPIClient(api_key)
    
    # Citation Count API 사용
    citation_data = client.get_citation_count(doi)
    
    if citation_data:
        print(f"DOI {doi}의 인용 정보:")
        print(f"총 인용 횟수: {citation_data.get('citation-count', 'N/A')}")
    
    return citation_data