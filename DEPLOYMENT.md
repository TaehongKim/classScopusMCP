# 🚀 Abstract Search MCP Tool 배포 가이드

이 문서는 Abstract Search MCP Tool을 다양한 플랫폼에 배포하는 방법을 설명합니다.

## 📦 NPM 배포

### 1. 사전 준비

```bash
# package.json 정보 확인 및 수정
npm login
npm whoami
```

### 2. 버전 관리

```bash
# 버전 업데이트 (patch: 1.0.0 -> 1.0.1)
npm version patch

# 또는 수동으로 package.json 수정
npm version minor  # 1.0.0 -> 1.1.0
npm version major  # 1.0.0 -> 2.0.0
```

### 3. 배포 실행

```bash
# 배포 전 패키지 내용 확인
npm pack --dry-run

# NPM 레지스트리에 배포
npm publish

# 스코프가 있는 패키지의 경우
npm publish --access public
```

### 4. 배포 확인

```bash
# 배포된 패키지 확인
npm view abstract-search-mcp

# 설치 테스트
npx abstract-search-mcp@latest
```

## 🐙 GitHub Packages 배포

### 1. GitHub 저장소 설정

```bash
# GitHub 저장소 생성 및 푸시
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/abstract-search-mcp.git
git push -u origin main
```

### 2. .npmrc 설정

```bash
# 프로젝트 루트에 .npmrc 파일 생성
echo "@yourusername:registry=https://npm.pkg.github.com" > .npmrc
```

### 3. package.json 수정

```json
{
  "name": "@yourusername/abstract-search-mcp",
  "publishConfig": {
    "registry": "https://npm.pkg.github.com"
  }
}
```

**⚠️ 주의**: 배포 전에 API 키가 하드코딩되지 않았는지 확인하세요. 이 도구는 환경변수를 통해 API 키를 받도록 설계되었습니다.

### 4. GitHub Personal Access Token 설정

```bash
# GitHub PAT으로 로그인
npm login --scope=@yourusername --registry=https://npm.pkg.github.com
```

### 5. 배포

```bash
npm publish
```

## 🏠 프라이빗 배포

### 1. Git 저장소를 통한 직접 설치

```bash
# 공개 저장소에서 설치
npm install -g git+https://github.com/yourusername/abstract-search-mcp.git

# 프라이빗 저장소에서 설치 (SSH)
npm install -g git+ssh://git@github.com/yourusername/abstract-search-mcp.git
```

### 2. 로컬 패키지 배포

```bash
# 타르볼 생성
npm pack

# 생성된 .tgz 파일로 설치
npm install -g abstract-search-mcp-1.0.0.tgz
```

## 🔧 CI/CD 자동화

### GitHub Actions 설정

`.github/workflows/publish.yml` 생성:

```yaml
name: Publish Package

on:
  release:
    types: [created]

jobs:
  publish-npm:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
          registry-url: 'https://registry.npmjs.org'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run tests
        run: npm test || echo "No tests specified"
      
      - name: Publish to NPM
        run: npm publish
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
  
  publish-github:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
          registry-url: 'https://npm.pkg.github.com'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Publish to GitHub Packages
        run: npm publish
        env:
          NODE_AUTH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## 📋 배포 체크리스트

### 배포 전 확인사항

- [ ] **보안**: API 키가 하드코딩되지 않았는지 확인
- [ ] **테스트**: 환경변수 방식으로 API 키가 정상 작동하는지 확인
- [ ] **문서**: README.md가 최신 상태인지 확인
- [ ] **버전**: package.json 버전이 올바른지 확인
- [ ] **라이선스**: LICENSE 파일이 존재하는지 확인
- [ ] **의존성**: package.json의 dependencies가 정확한지 확인
- [ ] **설정 예시**: 모든 MCP 클라이언트 설정 예시가 환경변수 방식으로 업데이트되었는지 확인

### 배포 후 확인사항

- [ ] **설치 테스트**: `npx abstract-search-mcp`로 설치 확인
- [ ] **환경변수 테스트**: `SCOPUS_API_KEY` 환경변수로 API 키가 정상 작동하는지 확인
- [ ] **기능 테스트**: 주요 기능들이 정상 작동하는지 확인
- [ ] **문서 업데이트**: 설치 가이드가 정확한지 확인
- [ ] **MCP 클라이언트 테스트**: Claude Desktop, Cursor 등에서 정상 작동하는지 확인

## 🔐 보안 고려사항

### 1. API 키 보안

- **절대 하드코딩 금지**: API 키를 코드에 직접 포함하지 않음
- **환경변수 사용**: 모든 민감한 정보는 환경변수로 관리
- **설정 파일 제외**: `.npmignore`에 `config.json` 포함

### 2. 의존성 보안

```bash
# 취약점 검사
npm audit

# 자동 수정
npm audit fix
```

## 📈 버전 관리 전략

### Semantic Versioning (SemVer)

- **MAJOR.MINOR.PATCH** (예: 1.2.3)
- **MAJOR**: 호환되지 않는 API 변경
- **MINOR**: 하위 호환되는 기능 추가
- **PATCH**: 하위 호환되는 버그 수정

### 브랜치 전략

```bash
# 개발 브랜치
git checkout -b develop

# 기능 브랜치
git checkout -b feature/new-api-support

# 릴리즈 브랜치
git checkout -b release/1.1.0

# 핫픽스 브랜치
git checkout -b hotfix/critical-bug
```

## 🌍 글로벌 배포 고려사항

### 1. 다국어 지원

```json
{
  "keywords": [
    "mcp", "논문검색", "academic", "research",
    "学术论文", "recherche académique"
  ]
}
```

### 2. 지역별 API 엔드포인트

```javascript
const regions = {
  'us': 'https://api.elsevier.com',
  'eu': 'https://api-eu.elsevier.com',
  'asia': 'https://api-asia.elsevier.com'
};
```

---

이 가이드를 따라 안전하고 효율적으로 Abstract Search MCP Tool을 배포할 수 있습니다. 질문이 있으시면 GitHub Issues를 통해 문의해 주세요.