#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
특정 DOI 조회 테스트
"""

import requests
import xml.etree.ElementTree as ET

def check_specific_doi():
    """특정 DOI 조회"""
    
    api_key = "920a284740d2c60fc3249e6e795e928c"
    doi = "10.1016/S0014-5793(01)03313-0"
    
    url = f"https://api.elsevier.com/content/abstract/doi/{doi}"
    headers = {
        'Accept': 'text/xml',
        'X-ELS-APIKey': api_key
    }
    params = {
        'apiKey': api_key
    }
    
    print("🔍 특정 DOI 조회 테스트...")
    print(f"DOI: {doi}")
    print(f"URL: {url}")
    print("-" * 60)
    
    try:
        response = requests.get(url, headers=headers, params=params)
        
        print(f"응답 상태 코드: {response.status_code}")
        print("-" * 60)
        
        if response.status_code == 200:
            print("✅ 응답 성공!")
            
            # XML 파싱
            root = ET.fromstring(response.text)
            
            # 모든 정보 추출
            print("\n📋 논문 정보:")
            print("-" * 40)
            
            # 제목
            title_elem = root.find('.//{http://purl.org/dc/elements/1.1/}title')
            if title_elem is not None:
                print(f"제목: {title_elem.text}")
            
            # 저자
            creator_elem = root.find('.//{http://purl.org/dc/elements/1.1/}creator')
            if creator_elem is not None:
                print(f"저자: {creator_elem.text}")
            
            # 저널명
            pub_name_elem = root.find('.//{http://prismstandard.org/namespaces/basic/2.0/}publicationName')
            if pub_name_elem is not None:
                print(f"저널: {pub_name_elem.text}")
            
            # 발행일
            cover_date_elem = root.find('.//{http://prismstandard.org/namespaces/basic/2.0/}coverDate')
            if cover_date_elem is not None:
                print(f"발행일: {cover_date_elem.text}")
            
            # 인용 횟수
            cited_by_elem = root.find('.//{http://www.elsevier.com/xml/svapi/abstract/dtd}citedby-count')
            if cited_by_elem is not None:
                print(f"인용 횟수: {cited_by_elem.text}")
            
            # DOI
            doi_elem = root.find('.//{http://prismstandard.org/namespaces/basic/2.0/}doi')
            if doi_elem is not None:
                print(f"DOI: {doi_elem.text}")
            
            # Scopus ID
            scopus_id_elem = root.find('.//{http://purl.org/dc/elements/1.1/}identifier')
            if scopus_id_elem is not None:
                print(f"Scopus ID: {scopus_id_elem.text}")
            
            # 초록 (description 태그 찾기)
            print("\n🔍 초록 정보 검색...")
            description_elem = root.find('.//{http://purl.org/dc/elements/1.1/}description')
            if description_elem is not None and description_elem.text:
                print(f"✅ 초록 발견!")
                abstract = description_elem.text
                if len(abstract) > 300:
                    abstract = abstract[:300] + "..."
                print(f"초록: {abstract}")
            else:
                print("❌ 초록 정보 없음")
                
                # 다른 방법으로 초록 찾기
                print("\n🔍 다른 방법으로 초록 검색...")
                for elem in root.iter():
                    if 'description' in elem.tag:
                        print(f"발견된 description 태그: {elem.tag}")
                        if elem.text:
                            print(f"초록: {elem.text[:200]}...")
                            break
                else:
                    print("description 태그를 찾을 수 없습니다.")
            
            # 모든 태그 출력 (디버깅용)
            print("\n📋 모든 XML 태그:")
            print("-" * 40)
            for elem in root.iter():
                if elem.text and elem.text.strip():
                    print(f"{elem.tag}: {elem.text[:100]}")
            
        else:
            print(f"❌ 응답 실패: {response.status_code}")
            print(f"응답 내용: {response.text}")
            
    except Exception as e:
        print(f"❌ 요청 실패: {e}")

if __name__ == "__main__":
    check_specific_doi() 