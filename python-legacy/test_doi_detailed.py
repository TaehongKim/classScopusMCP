#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DOI 기반 초록 조회 상세 테스트
"""

import requests
import xml.etree.ElementTree as ET

def test_doi_abstract_detailed():
    """DOI 기반 초록 조회 상세 테스트"""
    
    api_key = "920a284740d2c60fc3249e6e795e928c"
    test_doi = "10.1016/S0014-5793(01)03313-0"
    
    url = f"https://api.elsevier.com/content/abstract/doi/{test_doi}"
    headers = {
        'Accept': 'text/xml',
        'X-ELS-APIKey': api_key
    }
    params = {
        'apiKey': api_key
    }
    
    print("🔍 DOI 기반 초록 조회 상세 테스트...")
    print(f"URL: {url}")
    print(f"DOI: {test_doi}")
    print("-" * 50)
    
    try:
        response = requests.get(url, headers=headers, params=params)
        
        print(f"응답 상태 코드: {response.status_code}")
        print(f"응답 헤더: {dict(response.headers)}")
        print("-" * 50)
        
        if response.status_code == 200:
            print("✅ 응답 성공!")
            print("XML 응답 내용:")
            print(response.text[:1000])  # 처음 1000자만 출력
            
            # XML 파싱 시도
            try:
                root = ET.fromstring(response.text)
                print("\n✅ XML 파싱 성공!")
                
                # 모든 태그 찾기
                print("\n발견된 태그들:")
                for elem in root.iter():
                    print(f"  {elem.tag}: {elem.text[:100] if elem.text else 'None'}")
                
            except ET.ParseError as e:
                print(f"❌ XML 파싱 실패: {e}")
                
        else:
            print(f"❌ 응답 실패: {response.status_code}")
            print(f"응답 내용: {response.text}")
            
    except Exception as e:
        print(f"❌ 요청 실패: {e}")

if __name__ == "__main__":
    test_doi_abstract_detailed() 