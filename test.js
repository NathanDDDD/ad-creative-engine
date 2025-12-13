#!/usr/bin/env node

/**
 * Simple test to verify the module structure and basic functionality
 * This test doesn't make actual API calls (requires MISTRAL_API_KEY)
 */

const path = require('path');
const fs = require('fs');

// Test 1: Module exports
console.log('Test 1: Checking module exports...');
try {
  // Temporarily set API key to avoid exit
  process.env.MISTRAL_API_KEY = 'test-key-for-import';
  const module = require('./index.js');
  
  if (typeof module.generateAdCreatives !== 'function') {
    console.error('❌ FAIL: generateAdCreatives is not exported as a function');
    process.exit(1);
  }
  console.log('✅ PASS: Module exports generateAdCreatives function');
} catch (error) {
  console.error('❌ FAIL: Module failed to load:', error.message);
  process.exit(1);
}

// Test 2: Output directory creation
console.log('\nTest 2: Checking output directory...');
try {
  const outputDir = path.join(__dirname, 'output');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir);
    console.log('✅ PASS: Output directory created successfully');
  } else {
    console.log('✅ PASS: Output directory already exists');
  }
} catch (error) {
  console.error('❌ FAIL: Could not create output directory:', error.message);
  process.exit(1);
}

// Test 3: Package.json structure
console.log('\nTest 3: Checking package.json...');
try {
  const pkg = JSON.parse(fs.readFileSync(path.join(__dirname, 'package.json'), 'utf8'));
  
  if (!pkg.dependencies || !pkg.dependencies['@mistralai/mistralai']) {
    console.error('❌ FAIL: Mistral AI dependency not found in package.json');
    process.exit(1);
  }
  
  if (!pkg.scripts || !pkg.scripts.start) {
    console.error('❌ FAIL: Start script not found in package.json');
    process.exit(1);
  }
  
  console.log('✅ PASS: package.json is properly configured');
} catch (error) {
  console.error('❌ FAIL: Could not read package.json:', error.message);
  process.exit(1);
}

// Test 4: README exists
console.log('\nTest 4: Checking documentation...');
try {
  const readmePath = path.join(__dirname, 'README.md');
  if (!fs.existsSync(readmePath)) {
    console.error('❌ FAIL: README.md not found');
    process.exit(1);
  }
  
  const readme = fs.readFileSync(readmePath, 'utf8');
  if (!readme.includes('MISTRAL_API_KEY') || !readme.includes('npm')) {
    console.error('❌ FAIL: README missing important setup instructions');
    process.exit(1);
  }
  
  console.log('✅ PASS: README.md exists with proper documentation');
} catch (error) {
  console.error('❌ FAIL: Could not check README:', error.message);
  process.exit(1);
}

console.log('\n✅ All tests passed!');
console.log('\nNote: These are basic structure tests.');
console.log('To test full functionality, set MISTRAL_API_KEY and run: npm start');
