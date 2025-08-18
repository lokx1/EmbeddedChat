// Debug script để kiểm tra URL được tạo trong frontend
// Chạy trong browser console hoặc như một test script

console.log('🔍 Debugging Frontend API URLs');
console.log('================================');

// Simulate các environment variables có thể có
const possibleEnvConfigs = [
  { VITE_API_URL: 'https://embeddedchat-production.up.railway.app' },
  { VITE_API_URL: 'https://embeddedchat-production.up.railway.app/' },
  { VITE_API_BASE_URL: 'https://embeddedchat-production.up.railway.app' },
  { VITE_API_BASE_URL: 'https://embeddedchat-production.up.railway.app/' },
  {},  // No env vars, use default
];

possibleEnvConfigs.forEach((env, index) => {
  console.log(`\n📋 Config ${index + 1}:`, env);
  
  // Simulate the logic from AuthContext.tsx line 5
  const API_BASE_URL = env.VITE_API_URL || env.VITE_API_BASE_URL || 'http://localhost:8000';
  
  // Test các endpoints
  const registerUrl = `${API_BASE_URL}/auth/register`;
  const loginUrl = `${API_BASE_URL}/auth/login-json`;
  const meUrl = `${API_BASE_URL}/auth/me`;
  
  console.log('  API_BASE_URL:', API_BASE_URL);
  console.log('  Register URL:', registerUrl);
  console.log('  Login URL:', loginUrl);
  console.log('  Me URL:', meUrl);
  
  // Check for double slashes
  if (registerUrl.includes('//auth')) {
    console.log('  ⚠️  WARNING: Double slash detected in register URL!');
  }
  if (loginUrl.includes('//auth')) {
    console.log('  ⚠️  WARNING: Double slash detected in login URL!');
  }
  if (meUrl.includes('//auth')) {
    console.log('  ⚠️  WARNING: Double slash detected in me URL!');
  }
});

console.log('\n🎯 Recommendations:');
console.log('1. If VITE_API_URL ends with "/", URLs will have double slashes');
console.log('2. Use VITE_API_URL without trailing slash: "https://embeddedchat-production.up.railway.app"');
console.log('3. Check Vercel environment variables for trailing slashes');

// Function to clean URL 
function cleanApiUrl(url) {
  return url?.endsWith('/') ? url.slice(0, -1) : url;
}

console.log('\n🔧 Fixed URL examples:');
const cleanUrl = cleanApiUrl('https://embeddedchat-production.up.railway.app/');
console.log('Clean URL:', cleanUrl);
console.log('Register:', `${cleanUrl}/auth/register`);
console.log('Login:', `${cleanUrl}/auth/login-json`);
