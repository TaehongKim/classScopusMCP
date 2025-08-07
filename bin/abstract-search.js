#!/usr/bin/env node

/**
 * MCP Abstract Search Tool - Node.js Wrapper
 * npx로 실행할 수 있는 래퍼
 */

const path = require('path');
const fs = require('fs');

// Node.js 서버 스크립트 경로
const serverScriptPath = path.join(__dirname, '..', 'abstract-search-server.js');

// 메인 함수
function main() {
    // 서버 스크립트 존재 확인
    if (!fs.existsSync(serverScriptPath)) {
        console.error('❌ 서버 스크립트를 찾을 수 없습니다:', serverScriptPath);
        console.error('📁 현재 디렉토리:', __dirname);
        console.error('🔍 찾는 파일:', serverScriptPath);
        process.exit(1);
    }
    
    console.error('🚀 MCP Abstract Search Tool 시작...');
    console.error(`📄 서버 스크립트: ${serverScriptPath}`);
    
    // Node.js 서버 직접 실행
    try {
        // 서버 스크립트를 직접 require하여 실행
        require(serverScriptPath);
        
        // 프로세스가 계속 실행되도록 유지
        process.on('SIGINT', () => {
            console.error('\n🛑 서버를 종료합니다...');
            process.exit(0);
        });
        
        process.on('SIGTERM', () => {
            console.error('\n🛑 서버를 종료합니다...');
            process.exit(0);
        });
        
        // 서버가 계속 실행되도록 유지
        console.error('⏳ 서버가 요청을 기다리는 중...');
        
    } catch (error) {
        console.error('❌ 서버 실행 중 오류:', error.message);
        process.exit(1);
    }
}

// 스크립트가 직접 실행될 때만 main 함수 호출
if (require.main === module) {
    main();
}

module.exports = { main }; 