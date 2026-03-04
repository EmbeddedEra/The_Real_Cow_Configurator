#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const version = process.argv[2];

if (!version) {
  console.error('Version argument is required');
  process.exit(1);
}

// Update index.html - adjust path based on where script runs from
const possiblePaths = [
  path.join(__dirname, '../../index.html'),
  path.join(process.cwd(), 'index.html'),
  './index.html'
];

let htmlPath = null;
for (const p of possiblePaths) {
  if (fs.existsSync(p)) {
    htmlPath = p;
    break;
  }
}

if (!htmlPath) {
  console.error('Could not find index.html');
  process.exit(1);
}

let htmlContent = fs.readFileSync(htmlPath, 'utf8');
const updatedContent = htmlContent.replace(
  /content="v[\d.]+"/,
  `content="v${version}"`
);

if (htmlContent === updatedContent) {
  console.warn('Warning: No version tag found to update');
}

fs.writeFileSync(htmlPath, updatedContent, 'utf8');
console.log(`Updated ${htmlPath} to version v${version}`);
