#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const version = process.argv[2];

if (!version) {
  console.error('Version argument is required');
  process.exit(1);
}

// Update index.html
const indexPath = path.join(__dirname, '../../index.html');
let htmlContent = fs.readFileSync(indexPath, 'utf8');

htmlContent = htmlContent.replace(
  /content="v[\d.]+"/,
  `content="v${version}"`
);

fs.writeFileSync(indexPath, htmlContent, 'utf8');
console.log(`Updated index.html to version v${version}`);
