#!/usr/bin/env node

/**
 * Deploy Check Script
 * Kiểm tra dự án trước khi deploy lên Vercel
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('🔍 Kiểm tra dự án trước khi deploy...\n');

// Kiểm tra các file cần thiết
const requiredFiles = [
  'package.json',
  'vite.config.ts',
  'tsconfig.json',
  'src/main.tsx',
  'index.html'
];

console.log('📁 Kiểm tra file cấu hình:');
requiredFiles.forEach(file => {
  if (fs.existsSync(file)) {
    console.log(`✅ ${file}`);
  } else {
    console.log(`❌ ${file} - KHÔNG TỒN TẠI`);
    process.exit(1);
  }
});

// Kiểm tra dependencies
console.log('\n📦 Kiểm tra dependencies:');
try {
  const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
  const requiredDeps = ['react', 'react-dom', 'vite'];
  
  requiredDeps.forEach(dep => {
    if (packageJson.dependencies[dep] || packageJson.devDependencies[dep]) {
      console.log(`✅ ${dep}`);
    } else {
      console.log(`❌ ${dep} - THIẾU`);
    }
  });
} catch (error) {
  console.log('❌ Không thể đọc package.json');
  process.exit(1);
}

// Kiểm tra TypeScript
console.log('\n🔧 Kiểm tra TypeScript:');
try {
  execSync('npm run type-check', { stdio: 'inherit' });
  console.log('✅ TypeScript compilation successful');
} catch (error) {
  console.log('❌ TypeScript compilation failed');
  process.exit(1);
}

// Build test
console.log('\n🏗️  Test build:');
try {
  execSync('npm run build', { stdio: 'inherit' });
  console.log('✅ Build successful');
} catch (error) {
  console.log('❌ Build failed');
  process.exit(1);
}

// Kiểm tra dist folder
console.log('\n📂 Kiểm tra build output:');
const distFiles = ['index.html', 'assets'];
distFiles.forEach(file => {
  const filePath = path.join('dist', file);
  if (fs.existsSync(filePath)) {
    console.log(`✅ dist/${file}`);
  } else {
    console.log(`❌ dist/${file} - KHÔNG TỒN TẠI`);
  }
});

console.log('\n🎉 Tất cả kiểm tra đã hoàn tất! Dự án sẵn sàng deploy.');
console.log('\n📋 Bước tiếp theo:');
console.log('1. Push code lên GitHub');
console.log('2. Truy cập vercel.com');
console.log('3. Import repository và deploy');
console.log('4. Cấu hình environment variables trong Vercel Dashboard');
