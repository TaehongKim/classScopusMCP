# MCP Abstract Search Tool 사용 가이드

## 📋 개요

이 도구는 LLM이 사용할 수 있는 논문 검색 및 초록 가져오기 MCP (Model Context Protocol) 서버입니다. Scopus API를 사용하여 논문을 검색하고, Crossref 및 PubMed API를 통해 초록을 가져옵니다.

## 🔑 API Key 필요

사용하기 전에 [Elsevier Developer Portal](https://dev.elsevier.com/)에서 Scopus API 키를 발급받고, MCP 클라이언트 설정에서 환경변수로 전달해야 합니다.

## 🚀 설치 및 실행

### 1. 의존성 설치

```bash
npm install
```

### 2. 서버 실행

```bash
# 직접 실행
node abstract-search-server.js

# npm 스크립트 사용
npm start

# npx로 실행 (로컬 링크 후)
npm link
npx abstract-search-mcp
```

## 🔧 MCP 클라이언트 설정

### Cursor 설정

1. Cursor 설정 파일을 열거나 생성:
   - Windows: `%APPDATA%\Cursor\User\settings.json`
   - macOS: `~/Library/Application Support/Cursor/User/settings.json`
   - Linux: `~/.config/Cursor/User/settings.json`

2. 다음 설정을 추가:

```json
{
  "mcpServers": {
    "abstract-search": {
      "command": "npx",
      "args": ["abstract-search-mcp"],
      "env": {
        "SCOPUS_API_KEY": "your_scopus_api_key_here"
      }
    }
  }
}
```

### Claude Desktop 설정

1. Claude Desktop 설정 파일을 열거나 생성:
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. 다음 설정을 추가:

```json
{
  "mcpServers": {
    "abstract-search": {
      "command": "npx",
      "args": ["abstract-search-mcp"],
      "env": {
        "SCOPUS_API_KEY": "your_scopus_api_key_here"
      }
    }
  }
}
```

### Ollama 설정

1. Ollama 설정 파일을 열거나 생성:
   - Windows: `%APPDATA%\Ollama\ollama_config.json`
   - macOS: `~/Library/Application Support/Ollama/ollama_config.json`
   - Linux: `~/.config/Ollama/ollama_config.json`

2. 다음 설정을 추가:

```json
{
  "mcpServers": {
    "abstract-search": {
      "command": "npx",
      "args": ["abstract-search-mcp"],
      "env": {
        "SCOPUS_API_KEY": "your_scopus_api_key_here"
      }
    }
  }
}
```

## 🛠️ 사용 가능한 도구

### 1. search_papers
키워드로 논문을 검색하고 초록을 가져옵니다.

**매개변수:**
- `query` (필수): 검색할 키워드
- `count` (선택): 검색할 논문 수 (기본값: 10, 최대: 50)

**사용 예시:**
```
search_papers를 사용하여 "machine learning" 키워드로 5개 논문을 검색해주세요.
```

### 2. get_abstract_by_doi
DOI로 특정 논문의 초록을 가져옵니다.

**매개변수:**
- `doi` (필수): 논문의 DOI

**사용 예시:**
```
get_abstract_by_doi를 사용하여 DOI "10.1016/S0014-5793(01)03313-0"의 초록을 가져와주세요.
```

## 🔍 기능

- **Scopus 검색**: Elsevier의 Scopus 데이터베이스에서 논문 검색
- **Crossref 초록**: DOI를 통해 Crossref에서 초록 가져오기
- **PubMed 초록**: DOI를 통해 PubMed에서 초록 가져오기
- **품질 기반 선택**: 여러 소스에서 최고 품질의 초록 자동 선택
- **텍스트 정리**: HTML 태그 제거 및 텍스트 정리

## 📊 지원하는 API

1. **Scopus API**: 논문 메타데이터 검색
2. **Crossref API**: DOI 기반 초록 가져오기
3. **PubMed API**: DOI 기반 초록 가져오기

## 🚨 주의사항

- Scopus API 키가 필요합니다 (MCP 클라이언트 설정에서 `SCOPUS_API_KEY` 환경변수로 전달)
- 네트워크 연결이 필요합니다
- API 호출 제한이 있을 수 있습니다

## 📝 실제 사용 예시

### Claude Desktop에서 사용
1. API 키를 설정한 후 Claude Desktop을 재시작
2. 다음과 같이 요청:

```
search_papers를 사용해서 "artificial intelligence" 관련 논문을 3개 검색해줘
```

```
get_abstract_by_doi를 사용해서 DOI "10.1038/nature12373"의 초록을 가져와줘
```

### Cursor에서 사용
1. MCP 설정 후 Cursor를 재시작
2. AI와 대화에서 동일한 방식으로 사용

## 📞 문의

추가 지원이 필요한 경우 [GitHub Issues](https://github.com/TaehongKim/classScopusMCP/issues)를 통해 문의해주세요.

## 🔗 참고 자료

- [MCP 공식 문서](https://modelcontextprotocol.io/)
- [Cursor MCP 설정](https://cursor.sh/docs/mcp)
- [Claude Desktop MCP 설정](https://docs.anthropic.com/claude/docs/model-context-protocol-mcp) 