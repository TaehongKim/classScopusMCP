# ClassScopus MCP Tool

📚 **Model Context Protocol (MCP) 도구로 학술 논문 검색 및 초록 가져오기**

Scopus, Crossref, PubMed API를 통합하여 논문을 검색하고 초록을 가져오는 MCP 서버입니다. Claude Desktop, Cursor, Ollama 등 MCP를 지원하는 모든 AI 클라이언트에서 사용할 수 있습니다.

## ✨ 주요 기능

- 🔍 **논문 검색**: Scopus API를 통한 강력한 학술 논문 검색
- 📄 **초록 가져오기**: Crossref, PubMed에서 자동으로 초록 수집
- 🔄 **다중 소스**: 여러 데이터베이스에서 최고 품질의 초록 선택
- 🛡️ **보안**: 환경변수를 통한 안전한 API 키 관리
- 🚀 **간편 설치**: npx로 즉시 사용 가능
- 🐍 **Python 레거시**: 기존 Python 버전 코드 포함

## 🚀 빠른 시작

### 1. 설치

```bash
# NPM을 통한 전역 설치
npm install -g abstract-search-mcp

# 또는 npx로 즉시 사용
npx abstract-search-mcp
```

### 2. API 키 설정

Scopus API 키가 필요합니다. [Elsevier Developer Portal](https://dev.elsevier.com/)에서 무료로 발급받을 수 있습니다.

#### 방법 1: 환경변수 (권장)
```bash
export SCOPUS_API_KEY="your_scopus_api_key_here"
```

#### 방법 2: 설정 파일
```bash
# config.json 파일 생성
cp config.example.json config.json
# config.json 파일을 편집하여 API 키 입력
```

### 3. MCP 클라이언트 설정

#### Claude Desktop
`~/.claude_desktop_config.json` (macOS) 또는 `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

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

#### Cursor
프로젝트 루트의 `.cursor/mcp_config.json`:

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

#### Ollama
MCP 설정 파일에 추가:

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

## 🛠️ 사용 방법

### 논문 검색
```
search_papers를 사용해서 'machine learning' 관련 논문을 5개 검색해줘
```

### DOI로 초록 가져오기
```
get_abstract_by_doi를 사용해서 DOI '10.1038/nature12373'의 초록을 가져와줘
```

## 📋 사용 가능한 도구

### 1. search_papers
키워드로 논문을 검색하고 초록을 가져옵니다.

**매개변수:**
- `query` (필수): 검색할 키워드
- `count` (선택): 검색할 논문 수 (기본값: 10, 최대: 50)

### 2. get_abstract_by_doi
DOI로 특정 논문의 초록을 가져옵니다.

**매개변수:**
- `doi` (필수): 논문의 DOI

## 🔧 개발자 정보

### 로컬 개발

```bash
# 저장소 복제
git clone https://github.com/TaehongKim/classScopusMCP.git
cd classScopusMCP

# 의존성 설치
npm install

# 로컬 링크
npm link

# 테스트
npx abstract-search-mcp
```

### 프로젝트 구조

```
classScopusMCP/
├── abstract-search-server.js    # 메인 MCP 서버
├── bin/
│   └── abstract-search.js       # 실행 래퍼
├── config.example.json          # 설정 파일 예시
├── claude_desktop_config.example.json  # Claude Desktop 설정 예시
├── package.json                 # 패키지 정보
├── .npmignore                   # NPM 무시 파일
├── README.md                    # 메인 문서
├── MCP_SETUP_GUIDE.md          # MCP 설정 가이드
├── MCP_USAGE_GUIDE.md          # MCP 사용 가이드
├── DEPLOYMENT.md               # 배포 가이드
└── python-legacy/              # Python 레거시 코드
    ├── scopusAPI.py            # Python Scopus API
    ├── mcp_abstract_search_server.py  # Python MCP 서버
    └── requirements_mcp.txt     # Python 의존성
```

## 🌐 지원하는 데이터베이스

- **Scopus**: 주요 검색 엔진
- **Crossref**: DOI 기반 메타데이터 및 초록
- **PubMed**: 의학/생물학 논문 초록

## 📝 라이선스

MIT License - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🤝 기여하기

기여를 환영합니다! Issue를 생성하거나 Pull Request를 제출해 주세요.

## 📞 지원

- GitHub Issues: [이슈 생성](https://github.com/TaehongKim/classScopusMCP/issues)
- 문서: [MCP 공식 문서](https://modelcontextprotocol.io/)

## 🎯 로드맵

- [x] Scopus API 통합
- [x] Crossref API 통합
- [x] PubMed API 통합
- [x] MCP 서버 구현
- [x] Python 레거시 코드 포함
- [ ] arXiv API 통합
- [ ] Google Scholar 지원
- [ ] 인용 정보 추가
- [ ] 논문 전문 링크 제공
- [ ] 캐싱 기능 추가

## 📚 추가 문서

- [MCP 설정 가이드](MCP_SETUP_GUIDE.md) - MCP 서버 설정 방법
- [MCP 사용 가이드](MCP_USAGE_GUIDE.md) - 실제 사용 예시
- [배포 가이드](DEPLOYMENT.md) - NPM 배포 및 배포 전략

---

**Made with ❤️ for the academic research community**