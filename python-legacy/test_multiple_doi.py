#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
여러 DOI로 초록 조회 테스트
"""

import requests
import xml.etree.ElementTree as ET

def test_multiple_dois():
    """여러 DOI로 초록 조회 테스트"""
    
    api_key = "920a284740d2c60fc3249e6e795e928c"
    
    # 테스트할 DOI들
    test_dois = [
        "10.1016/S0014-5793(01)03313-0",  # 원래 테스트 DOI
        "10.1016/j.scico.2025.103365",     # WEST 논문
        "10.1002/deo2.70150",              # AI Endoscopy 논문
        "10.1016/j.fuel.2025.136284",      # Waste-chopped basalt fiber 논문
        "10.1016/j.eswa.2025.129011"       # Smart contract 논문
    ]
    
    headers = {
        'Accept': 'text/xml',
        'X-ELS-APIKey': api_key
    }
    
    for i, doi in enumerate(test_dois, 1):
        print(f"\n[{i}] DOI 테스트: {doi}")
        print("-" * 50)
        
        url = f"https://api.elsevier.com/content/abstract/doi/{doi}"
        params = {
            'apiKey': api_key
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                print("✅ 응답 성공!")
                
                # XML 파싱
                root = ET.fromstring(response.text)
                
                # 제목 찾기
                title_elem = root.find('.//{http://purl.org/dc/elements/1.1/}title')
                title = title_elem.text if title_elem is not None else "N/A"
                print(f"제목: {title}")
                
                # 초록 찾기 (description 태그)
                description_elem = root.find('.//{http://purl.org/dc/elements/1.1/}description')
                if description_elem is not None and description_elem.text:
                    abstract = description_elem.text
                    if len(abstract) > 200:
                        abstract = abstract[:200] + "..."
                    print(f"초록: {abstract}")
                else:
                    print("초록: 없음")
                
                # 저자 정보
                creator_elem = root.find('.//{http://purl.org/dc/elements/1.1/}creator')
                if creator_elem is not None:
                    print(f"저자: {creator_elem.text}")
                else:
                    print("저자: 없음")
                
            else:
                print(f"❌ 응답 실패: {response.status_code}")
                print(f"응답 내용: {response.text}")
                
        except Exception as e:
            print(f"❌ 요청 실패: {e}")
        
        print()

if __name__ == "__main__":
    test_multiple_dois() 