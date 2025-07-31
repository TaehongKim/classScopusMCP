# MCP 초록 검색 도구

LLM을 위한 Model Context Protocol (MCP) 기반 논문 검색 및 초록 가져오기 도구입니다.

## 🚀 설치 및 설정

### 1. 의존성 설치
```bash
pip install -r requirements_mcp.txt
```

### 2. MCP 라이브러리 설치
```bash
pip install mcp
```

## 📋 사용 가능한 도구

### 1. `search_papers` - 키워드로 논문 검색
- **설명**: 키워드로 논문을 검색하고 초록을 가져옵니다.
- **매개변수**:
  - `query` (필수): 검색할 키워드
  - `count` (선택): 검색할 논문 수 (기본값: 10, 최대: 50)

**사용 예시**:
```json
{
  "query": "artificial intelligence",
  "count": 5
}
```

### 2. `get_abstract_by_doi` - DOI로 초록 가져오기
- **설명**: DOI로 특정 논문의 초록을 가져옵니다.
- **매개변수**:
  - `doi` (필수): 논문의 DOI

**사용 예시**:
```json
{
  "doi": "10.1016/S0014-5793(01)03313-0"
}
```

## 🔧 MCP 클라이언트 설정

### Cursor에서 사용하기

1. **설정 파일 생성**: `~/.cursor/mcp_config.json` 파일을 생성하고 다음 내용을 추가:

```json
{
  "mcpServers": {
    "abstract-search": {
      "command": "python",
      "args": ["/path/to/your/mcp_abstract_search_tool.py"],
      "env": {
        "PYTHONPATH": "/path/to/your/project"
      }
    }
  }
}
```

2. **Cursor 재시작**: Cursor를 재시작하여 MCP 도구를 로드합니다.

### 다른 MCP 클라이언트에서 사용하기

1. **Claude Desktop**:
   - 설정에서 MCP 서버 추가
   - 명령어: `python mcp_abstract_search_tool.py`

2. **Ollama**:
   - `ollama serve` 실행 후 MCP 플러그인 설정

## 📊 기능

### 지원하는 API 소스
- **Crossref API**: DOI 기반 메타데이터 (품질 점수: 9)
- **PubMed API**: 생의학 논문 데이터베이스 (품질 점수: 8)
- **Scopus API**: 학술 논문 검색

### 초록 처리 기능
- HTML 태그 자동 제거
- 길이 최적화 (500자 제한)
- 품질 기반 우선순위 선택
- 다중 소스 중복 제거

## 🎯 사용 예시

### LLM과의 대화 예시

**사용자**: "AI 관련 최신 논문 5개를 찾아서 초록을 보여줘"

**LLM**: `search_papers` 도구를 사용하여 검색:

```json
{
  "query": "artificial intelligence",
  "count": 5
}
```

**결과**: 5개의 AI 관련 논문과 초록이 반환됩니다.

**사용자**: "DOI 10.1016/S0014-5793(01)03313-0의 초록을 가져와줘"

**LLM**: `get_abstract_by_doi` 도구를 사용:

```json
{
  "doi": "10.1016/S0014-5793(01)03313-0"
}
```

**결과**: 해당 논문의 제목, 저자, 초록이 반환됩니다.

## 🔍 반환되는 정보

### 논문 검색 결과
- 제목 (Title)
- 저자 (Authors)
- 저널명 (Publication)
- 발행일 (Date)
- DOI
- 인용 수 (Citations)
- Scopus ID 및 URL
- 초록 (Abstract)
- 초록 소스 (Abstract Source)

### DOI 검색 결과
- 제목 (Title)
- 초록 (Abstract)
- 초록 소스 (Abstract Source)

## ⚠️ 주의사항

1. **API 키**: Scopus API 키가 필요합니다.
2. **네트워크**: 인터넷 연결이 필요합니다.
3. **속도 제한**: API 호출 간격을 고려하여 설계되었습니다.
4. **SSL 인증서**: 자체 서명된 인증서 문제를 해결하기 위해 SSL 검증을 비활성화했습니다.

## 🛠️ 문제 해결

### MCP 도구가 로드되지 않는 경우
1. Python 경로 확인
2. 의존성 설치 확인
3. 설정 파일 경로 확인

### API 오류가 발생하는 경우
1. API 키 유효성 확인
2. 네트워크 연결 확인
3. API 호출 제한 확인

## 📝 라이선스

이 도구는 교육 및 연구 목적으로 제작되었습니다. 