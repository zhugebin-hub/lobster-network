const fs = require('fs');
const path = require('path');
const { marked } = require('marked');

const inputDir = process.argv[2];
const outputDir = process.argv[3] || inputDir;

if (!inputDir) {
  console.error('Usage: node md2pdf.js <input-dir> [output-dir]');
  process.exit(1);
}

// Create output dir if not exists
if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

const files = fs.readdirSync(inputDir).filter(f => f.endsWith('.md'));

if (files.length === 0) {
  console.error('No .md files found in', inputDir);
  process.exit(1);
}

console.log(`Found ${files.length} markdown files`);

files.forEach(file => {
  const inputPath = path.join(inputDir, file);
  const outputHtml = path.join(outputDir, file.replace('.md', '.html'));
  
  const md = fs.readFileSync(inputPath, 'utf8');
  const html = `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Microsoft YaHei', sans-serif; padding: 40px; line-height: 1.6; color: #333; }
    code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-family: 'Courier New', monospace; }
    pre { background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }
    pre code { background: none; padding: 0; }
    h1, h2, h3 { color: #2c3e50; margin-top: 1.5em; }
    h1 { border-bottom: 2px solid #3498db; padding-bottom: 10px; }
    a { color: #3498db; text-decoration: none; }
    a:hover { text-decoration: underline; }
    blockquote { border-left: 4px solid #3498db; margin: 0; padding-left: 20px; color: #666; }
    table { border-collapse: collapse; width: 100%; margin: 20px 0; }
    th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
    th { background: #f4f4f4; }
  </style>
</head>
<body>
${marked(md)}
</body>
</html>`;
  
  fs.writeFileSync(outputHtml, html, 'utf8');
  console.log(`✓ Converted: ${file} -> ${path.basename(outputHtml)}`);
});

console.log('\nDone! HTML files ready for PDF conversion.');
console.log('Next step: Use Chrome Headless to convert HTML to PDF');
console.log('Example: google-chrome --headless --disable-gpu --print-to-pdf="output.pdf" "file://$(pwd)/input.html"');
