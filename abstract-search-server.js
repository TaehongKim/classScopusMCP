#!/usr/bin/env node

/**
 * MCP (Model Context Protocol) 초록 검색 도구 - Node.js 버전
 * LLM이 사용할 수 있는 논문 검색 및 초록 가져오기 도구
 */

const axios = require('axios');
const xml2js = require('xml2js');
const readline = require('readline');

// MCP Abstract Search Tool 클래스
class MCPAbstractSearchTool {
    constructor() {
        this.scopusApiKey = this.loadApiKey();
        this.scopusUrl = "https://api.elsevier.com/content/search/scopus";
        this.sources = {
            crossref: 'https://api.crossref.org/works',
            pubmed: 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils'
        };
        
        this.headers = {
            'Accept': 'application/json',
            'X-ELS-APIKey': this.scopusApiKey
        };
    }

    /**
     * API Key를 환경변수 또는 로컬 설정 파일에서 로드
     */
    loadApiKey() {
        // 1. 환경변수에서 확인 (MCP 클라이언트가 env로 전달)
        if (process.env.SCOPUS_API_KEY) {
            console.error('✅ Scopus API Key loaded from environment variable');
            return process.env.SCOPUS_API_KEY;
        }

        // 2. 로컬 설정 파일에서 확인 (개발/테스트용)
        const fs = require('fs');
        const path = require('path');
        
        const configPaths = [
            './config.json',
            './config/config.json',
            path.join(process.cwd(), 'config.json'),
            path.join(__dirname, 'config.json')
        ];

        for (const configPath of configPaths) {
            try {
                if (fs.existsSync(configPath)) {
                    const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
                    if (config.scopus_api_key) {
                        console.error(`✅ Scopus API Key loaded from config file: ${configPath}`);
                        return config.scopus_api_key;
                    }
                }
            } catch (error) {
                console.error(`⚠️ Error reading config file ${configPath}: ${error.message}`);
            }
        }

        // 3. API Key가 없으면 에러
        this.showApiKeySetupInstructions();
        throw new Error('Scopus API Key is required');
    }

    /**
     * API Key 설정 방법 안내
     */
    showApiKeySetupInstructions() {
        console.error('❌ Scopus API Key not found!');
        console.error('');
        console.error('📝 Please set your Scopus API Key using one of these methods:');
        console.error('');
        console.error('1. MCP Client environment variable (recommended):');
        console.error('   {');
        console.error('     "mcpServers": {');
        console.error('       "abstract-search": {');
        console.error('         "command": "npx",');
        console.error('         "args": ["abstract-search-mcp"],');
        console.error('         "env": {');
        console.error('           "SCOPUS_API_KEY": "your_api_key_here"');
        console.error('         }');
        console.error('       }');
        console.error('     }');
        console.error('   }');
        console.error('');
        console.error('2. System environment variable:');
        console.error('   export SCOPUS_API_KEY="your_api_key_here"');
        console.error('');
        console.error('3. Create local config.json file (for development):');
        console.error('   {');
        console.error('     "scopus_api_key": "your_api_key_here"');
        console.error('   }');
        console.error('');
        console.error('🔗 Get your Scopus API Key at: https://dev.elsevier.com/');
    }

    /**
     * 초록 텍스트 정리
     */
    cleanAbstract(abstract) {
        if (!abstract || abstract === 'N/A') {
            return 'N/A';
        }

        // HTML 태그 제거
        let cleanText = abstract.replace(/<[^>]+>/g, '');
        cleanText = cleanText.replace(/<jats:[^>]+>/g, '');
        cleanText = cleanText.replace(/<\/jats:[^>]+>/g, '');

        // 특수 문자 정리
        cleanText = cleanText.replace(/\s+/g, ' ').trim();

        // 길이 제한 (500자)
        if (cleanText.length > 500) {
            cleanText = cleanText.substring(0, 500) + "...";
        }

        return cleanText;
    }

    /**
     * Scopus 검색
     */
    async searchScopus(query, count = 10) {
        const params = {
            query: query,
            count: count,
            start: 0,
            apiKey: this.scopusApiKey
        };

        try {
            const response = await axios.get(this.scopusUrl, {
                headers: this.headers,
                params: params,
                httpsAgent: new (require('https').Agent)({
                    rejectUnauthorized: false
                })
            });

            if (response.status === 200) {
                return response.data;
            } else {
                return {};
            }
        } catch (error) {
            console.error('Scopus API 오류:', error.message);
            return {};
        }
    }

    /**
     * Crossref API로 초록 가져오기
     */
    async getAbstractFromCrossref(doi) {
        if (!doi || doi === 'N/A') {
            return { source: 'crossref', abstract: 'N/A', success: false };
        }

        const url = `${this.sources.crossref}/${doi}`;

        try {
            const response = await axios.get(url, {
                httpsAgent: new (require('https').Agent)({
                    rejectUnauthorized: false
                }),
                timeout: 10000
            });

            if (response.status === 200) {
                const data = response.data;

                if (data.message) {
                    const message = data.message;
                    const abstract = message.abstract || 'N/A';

                    if (abstract && abstract !== 'N/A') {
                        const cleanAbstract = this.cleanAbstract(abstract);
                        return {
                            source: 'crossref',
                            abstract: cleanAbstract,
                            success: true,
                            title: message.title ? message.title[0] : 'N/A',
                            quality_score: 9
                        };
                    }
                }
            }

            return { source: 'crossref', abstract: 'N/A', success: false };
        } catch (error) {
            console.error('Crossref API 오류:', error.message);
            return { source: 'crossref', abstract: 'N/A', success: false };
        }
    }

    /**
     * PubMed API로 초록 가져오기
     */
    async getAbstractFromPubMed(doi) {
        if (!doi || doi === 'N/A') {
            return { source: 'pubmed', abstract: 'N/A', success: false };
        }

        const searchUrl = `${this.sources.pubmed}/esearch.fcgi`;
        const searchParams = {
            db: 'pubmed',
            term: `${doi}[doi]`,
            retmode: 'json'
        };

        try {
            const response = await axios.get(searchUrl, {
                params: searchParams,
                httpsAgent: new (require('https').Agent)({
                    rejectUnauthorized: false
                }),
                timeout: 10000
            });

            if (response.status === 200) {
                const data = response.data;

                if (data.esearchresult && data.esearchresult.idlist) {
                    const pmidList = data.esearchresult.idlist;

                    if (pmidList.length > 0) {
                        const pmid = pmidList[0];
                        const fetchUrl = `${this.sources.pubmed}/efetch.fcgi`;
                        const fetchParams = {
                            db: 'pubmed',
                            id: pmid,
                            retmode: 'xml'
                        };

                        const fetchResponse = await axios.get(fetchUrl, {
                            params: fetchParams,
                            httpsAgent: new (require('https').Agent)({
                                rejectUnauthorized: false
                            }),
                            timeout: 10000
                        });

                        if (fetchResponse.status === 200) {
                            const parser = new xml2js.Parser();
                            const result = await parser.parseStringPromise(fetchResponse.data);

                            const abstractElement = this.findElement(result, 'AbstractText');
                            if (abstractElement && abstractElement[0]) {
                                const titleElement = this.findElement(result, 'ArticleTitle');
                                const titleText = titleElement && titleElement[0] ? titleElement[0] : 'N/A';

                                const cleanAbstract = this.cleanAbstract(abstractElement[0]);
                                return {
                                    source: 'pubmed',
                                    abstract: cleanAbstract,
                                    success: true,
                                    title: titleText,
                                    quality_score: 8
                                };
                            }
                        }
                    }
                }
            }

            return { source: 'pubmed', abstract: 'N/A', success: false };
        } catch (error) {
            console.error('PubMed API 오류:', error.message);
            return { source: 'pubmed', abstract: 'N/A', success: false };
        }
    }

    /**
     * XML에서 요소 찾기 헬퍼 함수
     */
    findElement(obj, tagName) {
        if (obj && typeof obj === 'object') {
            for (const key in obj) {
                if (key === tagName) {
                    return obj[key];
                }
                if (typeof obj[key] === 'object') {
                    const result = this.findElement(obj[key], tagName);
                    if (result) return result;
                }
            }
        }
        return null;
    }

    /**
     * 최고 품질의 초록 가져오기
     */
    async getBestAbstract(doi) {
        const results = [];

        const sources = [
            ['crossref', this.getAbstractFromCrossref.bind(this)],
            ['pubmed', this.getAbstractFromPubMed.bind(this)]
        ];

        for (const [sourceName, sourceFunc] of sources) {
            const result = await sourceFunc(doi);
            if (result.success) {
                results.push(result);
            }
            // API 호출 간격 조절
            await new Promise(resolve => setTimeout(resolve, 300));
        }

        if (results.length > 0) {
            return results.reduce((best, current) => 
                (current.quality_score || 0) > (best.quality_score || 0) ? current : best
            );
        }

        return { source: 'none', abstract: 'N/A', success: false };
    }

    /**
     * 키워드로 논문 검색하고 초록 가져오기
     */
    async searchPapersWithAbstracts(query, count = 10) {
        const results = await this.searchScopus(query, count);

        if (results && results['search-results']) {
            const totalResults = results['search-results']['opensearch:totalResults'] || 0;
            const entries = results['search-results'].entry || [];

            const papers = [];
            for (const entry of entries) {
                const doi = entry['prism:doi'] || 'N/A';

                // 초록 가져오기
                let abstract = 'N/A';
                let abstractResult = { source: 'N/A' };

                if (doi !== 'N/A') {
                    abstractResult = await this.getBestAbstract(doi);
                    abstract = abstractResult.success ? abstractResult.abstract : 'N/A';
                }

                const paper = {
                    title: entry['dc:title'] || 'N/A',
                    authors: entry['dc:creator'] || 'N/A',
                    publication_name: entry['prism:publicationName'] || 'N/A',
                    publication_date: entry['prism:coverDate'] || 'N/A',
                    doi: doi,
                    cited_by_count: entry['citedby-count'] || 0,
                    scopus_id: (entry['dc:identifier'] || '').replace('SCOPUS_ID:', ''),
                    scopus_url: `https://www.scopus.com/inward/record.uri?eid=${entry.eid || ''}`,
                    abstract: abstract,
                    abstract_source: abstractResult.source || 'N/A'
                };
                papers.push(paper);
            }

            return papers;
        } else {
            return [];
        }
    }
}

// MCP 서버 클래스
class MCPServer {
    constructor() {
        this.tool = new MCPAbstractSearchTool();
        this.initialized = false;
    }

    async handleInitialize(request) {
        console.error('🔧 MCP 서버 초기화 중...');
        
        this.initialized = true;
        
        return {
            jsonrpc: "2.0",
            id: request.id,
            result: {
                protocolVersion: "2024-11-05",
                capabilities: {
                    tools: {}
                },
                serverInfo: {
                    name: "abstract-search",
                    version: "1.0.0"
                }
            }
        };
    }

    async handleListTools(request) {
        console.error('📋 도구 목록 요청...');
        
        const tools = [
            {
                name: "search_papers",
                description: "키워드로 논문을 검색하고 초록을 가져옵니다.",
                inputSchema: {
                    type: "object",
                    properties: {
                        query: {
                            type: "string",
                            description: "검색할 키워드"
                        },
                        count: {
                            type: "integer",
                            description: "검색할 논문 수 (기본값: 10, 최대: 50)",
                            default: 10
                        }
                    },
                    required: ["query"]
                }
            },
            {
                name: "get_abstract_by_doi",
                description: "DOI로 특정 논문의 초록을 가져옵니다.",
                inputSchema: {
                    type: "object",
                    properties: {
                        doi: {
                            type: "string",
                            description: "논문의 DOI"
                        }
                    },
                    required: ["doi"]
                }
            }
        ];

        return {
            jsonrpc: "2.0",
            id: request.id,
            result: {
                tools: tools
            }
        };
    }

    async handleCallTool(request) {
        const params = request.params || {};
        const name = params.name;
        const arguments_ = params.arguments || {};

        console.error(`🛠️ 도구 호출: ${name}`);

        let result;
        try {
            if (name === "search_papers") {
                result = await this.searchPapersTool(arguments_);
            } else if (name === "get_abstract_by_doi") {
                result = await this.getAbstractByDoiTool(arguments_);
            } else {
                result = [{ type: "text", text: `알 수 없는 도구: ${name}` }];
            }
        } catch (error) {
            console.error(`❌ 도구 실행 오류: ${error.message}`);
            result = [{ type: "text", text: `도구 실행 중 오류가 발생했습니다: ${error.message}` }];
        }

        return {
            jsonrpc: "2.0",
            id: request.id,
            result: {
                content: result
            }
        };
    }

    async searchPapersTool(arguments_) {
        const query = arguments_.query || "";
        const count = arguments_.count || 10;

        if (!query) {
            return [{ type: "text", text: "검색할 키워드를 입력해주세요." }];
        }

        console.error(`🔍 논문 검색: "${query}" (${count}개)`);

        const papers = await this.tool.searchPapersWithAbstracts(query, count);

        if (papers.length === 0) {
            return [{ type: "text", text: `'${query}' 키워드로 검색된 논문이 없습니다.` }];
        }

        // 결과를 JSON 형태로 반환
        let resultText = `'${query}' 키워드로 ${papers.length}개 논문을 찾았습니다:\n\n`;

        for (let i = 0; i < papers.length; i++) {
            const paper = papers[i];
            resultText += `[${i + 1}] ${paper.title}\n`;
            resultText += `저자: ${paper.authors}\n`;
            resultText += `저널: ${paper.publication_name}\n`;
            resultText += `발행일: ${paper.publication_date}\n`;
            resultText += `인용: ${paper.cited_by_count}\n`;
            resultText += `DOI: ${paper.doi}\n`;

            if (paper.abstract !== 'N/A') {
                resultText += `초록 (${paper.abstract_source}): ${paper.abstract}\n`;
            } else {
                resultText += "초록: 없음\n";
            }

            resultText += `Scopus URL: ${paper.scopus_url}\n`;
            resultText += "-".repeat(50) + "\n";
        }

        return [{ type: "text", text: resultText }];
    }

    async getAbstractByDoiTool(arguments_) {
        const doi = arguments_.doi || "";

        if (!doi) {
            return [{ type: "text", text: "DOI를 입력해주세요." }];
        }

        console.error(`📄 DOI 초록 가져오기: "${doi}"`);

        const abstractResult = await this.tool.getBestAbstract(doi);

        if (abstractResult.success) {
            let resultText = `DOI: ${doi}\n`;
            resultText += `제목: ${abstractResult.title || 'N/A'}\n`;
            resultText += `초록 소스: ${abstractResult.source}\n`;
            resultText += `초록: ${abstractResult.abstract}\n`;
            return [{ type: "text", text: resultText }];
        } else {
            return [{ type: "text", text: `DOI '${doi}'에 대한 초록을 찾을 수 없습니다.` }];
        }
    }
}

// MCP 서버 실행
async function main() {
    console.error('🚀 MCP Abstract Search Tool 시작...');
    
    const server = new MCPServer();
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout,
        terminal: false
    });

    // 프로세스 종료 처리
    process.on('SIGINT', () => {
        console.error('\n🛑 서버를 종료합니다...');
        rl.close();
        process.exit(0);
    });

    process.on('SIGTERM', () => {
        console.error('\n🛑 서버를 종료합니다...');
        rl.close();
        process.exit(0);
    });

    // 서버가 계속 실행되도록 유지
    process.on('exit', (code) => {
        console.error(`🔚 서버 종료 (코드: ${code})`);
    });

    // stdin 데이터 이벤트 리스너 추가
    process.stdin.on('data', (data) => {
        console.error(`📥 stdin 데이터 수신: ${data.toString().trim()}`);
    });

    rl.on('line', async (line) => {
        try {
            if (!line.trim()) {
                console.error('📭 빈 라인 무시');
                return;
            }

            console.error(`📨 원시 라인 수신: ${line.trim()}`);
            const request = JSON.parse(line.trim());
            const method = request.method;

            console.error(`📨 요청 수신: ${method} (ID: ${request.id})`);

            let response;
            if (method === "initialize") {
                response = await server.handleInitialize(request);
            } else if (method === "tools/list") {
                response = await server.handleListTools(request);
            } else if (method === "tools/call") {
                response = await server.handleCallTool(request);
            } else if (method === "notifications/initialized") {
                // notifications/initialized 메시지에 대한 응답 (빈 응답)
                console.error('✅ 초기화 완료 알림 수신');
                response = null;
            } else {
                console.error(`❌ 알 수 없는 메서드: ${method}`);
                response = {
                    jsonrpc: "2.0",
                    id: request.id,
                    error: {
                        code: -32601,
                        message: `Method not found: ${method}`
                    }
                };
            }

            // notifications/initialized는 응답을 보내지 않음
            if (response !== null) {
                console.error(`📤 응답 전송: ${response.jsonrpc ? 'success' : 'error'}`);
                console.log(JSON.stringify(response));
            }
        } catch (error) {
            console.error(`❌ 요청 처리 오류: ${error.message}`);
            const errorResponse = {
                jsonrpc: "2.0",
                id: request ? request.id : null,
                error: {
                    code: -32603,
                    message: `Internal error: ${error.message}`
                }
            };
            console.log(JSON.stringify(errorResponse));
        }
    });

    rl.on('close', () => {
        console.error('🔌 서버 연결이 종료되었습니다.');
        process.exit(0);
    });

    rl.on('error', (error) => {
        console.error(`❌ 읽기 오류: ${error.message}`);
        process.exit(1);
    });

    // 서버가 계속 실행되도록 유지
    console.error('⏳ 서버가 요청을 기다리는 중...');
}

if (require.main === module) {
    main().catch((error) => {
        console.error(`💥 치명적 오류: ${error.message}`);
        process.exit(1);
    });
}

module.exports = { MCPServer, MCPAbstractSearchTool }; 