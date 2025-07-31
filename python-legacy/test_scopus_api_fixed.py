#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scopus API 테스트 파일 (수정된 버전)
"""

import requests
import json

def test_scopus_api():
    """Scopus API 테스트"""
    
    # API 설정
    api_key = "920a284740d2c60fc3249e6e795e928c"
    base_url = "https://api.elsevier.com/content/search/scopus"
    
    headers = {
        'Accept': 'application/json',
        'X-ELS-APIKey': api_key
    }
    
    # 테스트 쿼리
    params = {
        'query': 'all(gene)',
        'count': 5,
        'start': 0,
        'apiKey': api_key
    }
    
    try:
        print("🔍 Scopus API 테스트 시작...")
        print(f"URL: {base_url}")
        print(f"쿼리: {params['query']}")
        print("-" * 50)
        
        response = requests.get(base_url, headers=headers, params=params)
        
        print(f"응답 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # 결과 요약
            if 'search-results' in data:
                total_results = data['search-results'].get('opensearch:totalResults', 0)
                entries = data['search-results'].get('entry', [])
                
                print(f"✅ API 테스트 성공!")
                print(f"총 검색 결과: {total_results}개")
                print(f"현재 페이지 결과: {len(entries)}개")
                print()
                
                # 첫 번째 결과 출력
                if entries:
                    print("📋 첫 번째 검색 결과:")
                    first_entry = entries[0]
                    print(f"제목: {first_entry.get('dc:title', 'N/A')}")
                    print(f"저자: {first_entry.get('dc:creator', 'N/A')}")
                    print(f"저널: {first_entry.get('prism:publicationName', 'N/A')}")
                    print(f"발행일: {first_entry.get('prism:coverDate', 'N/A')}")
                    print(f"DOI: {first_entry.get('prism:doi', 'N/A')}")
                    print(f"인용 횟수: {first_entry.get('citedby-count', 0)}")
                    print()
                
                return True
            else:
                print("❌ 응답에 'search-results' 키가 없습니다.")
                return False
                
        else:
            print(f"❌ API 요청 실패: {response.status_code}")
            print(f"응답 내용: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

def test_usability_search():
    """Usability 관련 검색 테스트"""
    
    api_key = "920a284740d2c60fc3249e6e795e928c"
    base_url = "https://api.elsevier.com/content/search/scopus"
    
    headers = {
        'Accept': 'application/json',
        'X-ELS-APIKey': api_key
    }
    
    # Usability 검색 쿼리
    params = {
        'query': 'TITLE-ABS-KEY(usability) AND PUBYEAR > 2020',
        'count': 3,
        'start': 0,
        'apiKey': api_key
    }
    
    try:
        print("🔍 Usability 검색 테스트...")
        print(f"쿼리: {params['query']}")
        print("-" * 50)
        
        response = requests.get(base_url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'search-results' in data:
                total_results = data['search-results'].get('opensearch:totalResults', 0)
                entries = data['search-results'].get('entry', [])
                
                print(f"✅ Usability 검색 성공!")
                print(f"총 검색 결과: {total_results}개")
                print(f"현재 페이지 결과: {len(entries)}개")
                print()
                
                # 결과 출력
                for i, entry in enumerate(entries, 1):
                    print(f"[{i}] {entry.get('dc:title', 'N/A')}")
                    print(f"    저자: {entry.get('dc:creator', 'N/A')}")
                    print(f"    저널: {entry.get('prism:publicationName', 'N/A')}")
                    print(f"    발행일: {entry.get('prism:coverDate', 'N/A')}")
                    print(f"    인용: {entry.get('citedby-count', 0)}")
                    print()
                
                return True
            else:
                print("❌ 응답에 'search-results' 키가 없습니다.")
                return False
        else:
            print(f"❌ Usability 검색 실패: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

def test_simple_search():
    """간단한 검색 테스트"""
    
    api_key = "920a284740d2c60fc3249e6e795e928c"
    base_url = "https://api.elsevier.com/content/search/scopus"
    
    headers = {
        'Accept': 'application/json',
        'X-ELS-APIKey': api_key
    }
    
    # 간단한 검색 쿼리
    params = {
        'query': 'usability',
        'count': 2,
        'start': 0,
        'apiKey': api_key
    }
    
    try:
        print("🔍 간단한 검색 테스트...")
        print(f"쿼리: {params['query']}")
        print("-" * 50)
        
        response = requests.get(base_url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'search-results' in data:
                total_results = data['search-results'].get('opensearch:totalResults', 0)
                entries = data['search-results'].get('entry', [])
                
                print(f"✅ 간단한 검색 성공!")
                print(f"총 검색 결과: {total_results}개")
                print(f"현재 페이지 결과: {len(entries)}개")
                print()
                
                # 결과 출력
                for i, entry in enumerate(entries, 1):
                    print(f"[{i}] {entry.get('dc:title', 'N/A')}")
                    print(f"    저자: {entry.get('dc:creator', 'N/A')}")
                    print(f"    저널: {entry.get('prism:publicationName', 'N/A')}")
                    print(f"    발행일: {entry.get('prism:coverDate', 'N/A')}")
                    print(f"    인용: {entry.get('citedby-count', 0)}")
                    print()
                
                return True
            else:
                print("❌ 응답에 'search-results' 키가 없습니다.")
                return False
        else:
            print(f"❌ 간단한 검색 실패: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🔬 Scopus API 테스트 프로그램 (수정된 버전)")
    print("=" * 60)
    
    # 기본 API 테스트
    success1 = test_scopus_api()
    
    print("\n" + "=" * 60)
    
    # 간단한 검색 테스트
    success2 = test_simple_search()
    
    print("\n" + "=" * 60)
    
    # Usability 검색 테스트
    success3 = test_usability_search()
    
    print("\n" + "=" * 60)
    
    if success1 and success2 and success3:
        print("✅ 모든 테스트가 성공했습니다!")
        print("🎉 Scopus API가 정상적으로 작동합니다.")
        print("📝 이제 scopusAPI.py 파일을 사용할 수 있습니다.")
    else:
        print("❌ 일부 테스트가 실패했습니다.")
        print("💡 API 키나 네트워크 연결을 확인해주세요.") 