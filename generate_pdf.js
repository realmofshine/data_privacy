const fs = require('fs');
const path = require('path');

const artifactDir = 'C:\\Users\\Abhishek\\.gemini\\antigravity\\brain\\30e84c4e-4d8f-4bd9-8064-cf818bcd684c';

const part1 = fs.readFileSync(path.join(artifactDir, 'dp_platform_complete_part1.md'), 'utf-8');
const part2 = fs.readFileSync(path.join(artifactDir, 'dp_platform_complete_part2.md'), 'utf-8');
const part3 = fs.readFileSync(path.join(artifactDir, 'dp_platform_complete_part3.md'), 'utf-8');

function mdToHtml(md) {
    let html = md;
    // Code blocks
    html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (_, lang, code) => {
        return `<pre class="code-block"><code>${code.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</code></pre>`;
    });
    // Tables
    html = html.replace(/^(\|.+\|)\n(\|[-| :]+\|)\n((?:\|.+\|\n?)*)/gm, (match, header, sep, body) => {
        const hCells = header.split('|').filter(c => c.trim());
        const rows = body.trim().split('\n').filter(r => r.trim());
        let t = '<table><thead><tr>';
        hCells.forEach(c => t += `<th>${c.trim()}</th>`);
        t += '</tr></thead><tbody>';
        rows.forEach(r => {
            const cells = r.split('|').filter(c => c.trim());
            t += '<tr>';
            cells.forEach(c => t += `<td>${c.trim()}</td>`);
            t += '</tr>';
        });
        t += '</tbody></table>';
        return t;
    });
    // Headers
    html = html.replace(/^#### (.+)$/gm, '<h4>$1</h4>');
    html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
    html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
    html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');
    // Bold
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    // Italic
    html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
    // Inline code
    html = html.replace(/`([^`]+)`/g, '<code class="inline">$1</code>');
    // Unordered lists
    html = html.replace(/^- (.+)$/gm, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>\n?)+/g, (m) => `<ul>${m}</ul>`);
    // Numbered lists
    html = html.replace(/^\d+\. (.+)$/gm, '<li>$1</li>');
    // Horizontal rules
    html = html.replace(/^---$/gm, '<hr>');
    // Blockquotes
    html = html.replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>');
    // Paragraphs
    html = html.replace(/^(?!<[huptblodhr])((?!<).+)$/gm, '<p>$1</p>');
    // Checkboxes
    html = html.replace(/☐/g, '☐');
    return html;
}

const fullContent = part1 + '\n\n<div class="page-break"></div>\n\n' + part2 + '\n\n<div class="page-break"></div>\n\n' + part3;

const htmlContent = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Data Privacy & Security Intelligence Platform - Complete Document</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    font-family: 'Inter', -apple-system, sans-serif;
    background: #0a0e1a;
    color: #e0e4ef;
    line-height: 1.7;
    padding: 40px;
    max-width: 1000px;
    margin: 0 auto;
  }

  /* COVER PAGE */
  .cover {
    height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    background: linear-gradient(135deg, #0a0e1a 0%, #1a1e3a 50%, #0a0e1a 100%);
    border: 1px solid rgba(99, 102, 241, 0.2);
    border-radius: 20px;
    padding: 60px;
    margin-bottom: 60px;
    position: relative;
    overflow: hidden;
  }
  .cover::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle at 30% 40%, rgba(99, 102, 241, 0.08) 0%, transparent 50%),
                radial-gradient(circle at 70% 60%, rgba(34, 197, 94, 0.06) 0%, transparent 50%);
  }
  .cover .shield { font-size: 80px; margin-bottom: 30px; position: relative; }
  .cover h1 {
    font-size: 42px;
    font-weight: 900;
    background: linear-gradient(135deg, #6366f1, #22d3ee, #22c55e);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 16px;
    position: relative;
  }
  .cover .subtitle {
    font-size: 20px;
    color: #94a3b8;
    font-weight: 300;
    margin-bottom: 40px;
    position: relative;
  }
  .cover .stats {
    display: flex;
    gap: 40px;
    position: relative;
  }
  .cover .stat {
    text-align: center;
  }
  .cover .stat .num {
    font-size: 36px;
    font-weight: 800;
    color: #6366f1;
  }
  .cover .stat .label {
    font-size: 12px;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 1px;
  }

  h1 {
    font-size: 32px;
    font-weight: 800;
    color: #f1f5f9;
    margin: 50px 0 20px;
    padding-bottom: 12px;
    border-bottom: 2px solid rgba(99, 102, 241, 0.3);
  }
  h2 {
    font-size: 24px;
    font-weight: 700;
    color: #c7d2fe;
    margin: 40px 0 16px;
  }
  h3 {
    font-size: 19px;
    font-weight: 600;
    color: #a5b4fc;
    margin: 30px 0 12px;
  }
  h4 {
    font-size: 16px;
    font-weight: 600;
    color: #818cf8;
    margin: 20px 0 10px;
  }

  p {
    margin: 10px 0;
    color: #cbd5e1;
    font-size: 14px;
  }

  strong { color: #f1f5f9; }

  table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
    font-size: 13px;
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(99, 102, 241, 0.15);
    border-radius: 10px;
    overflow: hidden;
  }
  th {
    background: rgba(99, 102, 241, 0.15);
    color: #c7d2fe;
    padding: 12px 16px;
    text-align: left;
    font-weight: 600;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  td {
    padding: 10px 16px;
    border-top: 1px solid rgba(99, 102, 241, 0.08);
    color: #cbd5e1;
  }
  tr:hover { background: rgba(99, 102, 241, 0.05); }

  pre.code-block {
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid rgba(99, 102, 241, 0.15);
    border-radius: 10px;
    padding: 20px;
    margin: 16px 0;
    overflow-x: auto;
    font-size: 12px;
    line-height: 1.6;
  }
  pre.code-block code {
    color: #a5b4fc;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
  }
  code.inline {
    background: rgba(99, 102, 241, 0.15);
    color: #a5b4fc;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 13px;
  }

  ul, ol {
    margin: 10px 0 10px 24px;
    color: #cbd5e1;
    font-size: 14px;
  }
  li { margin: 6px 0; }

  hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.3), transparent);
    margin: 40px 0;
  }

  blockquote {
    border-left: 3px solid #6366f1;
    padding: 12px 20px;
    margin: 16px 0;
    background: rgba(99, 102, 241, 0.05);
    border-radius: 0 8px 8px 0;
    color: #c7d2fe;
    font-style: italic;
  }

  .page-break { page-break-before: always; margin: 60px 0; }

  /* Card mockups in the document */
  .toc {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(99, 102, 241, 0.2);
    border-radius: 16px;
    padding: 30px;
    margin: 30px 0;
  }
  .toc h2 { margin-top: 0; }
  .toc ol { padding-left: 20px; }
  .toc li { margin: 8px 0; color: #94a3b8; }
  .toc a { color: #818cf8; text-decoration: none; }

  @media print {
    body { background: white; color: #1e293b; padding: 20px; }
    h1 { color: #1e293b; border-bottom-color: #6366f1; }
    h2 { color: #4338ca; }
    h3 { color: #4f46e5; }
    h4 { color: #6366f1; }
    p, li, td { color: #334155; }
    th { background: #e0e7ff; color: #312e81; }
    td { border-top-color: #e2e8f0; }
    pre.code-block { background: #f8fafc; border-color: #e2e8f0; }
    pre.code-block code { color: #4338ca; }
    code.inline { background: #e0e7ff; color: #4338ca; }
    table { border-color: #e2e8f0; background: #f8fafc; }
    blockquote { background: #f0f0ff; color: #4338ca; }
    .cover { background: white; border-color: #6366f1; }
    .cover h1 { -webkit-text-fill-color: #4338ca; }
    .cover .subtitle { color: #64748b; }
    .cover .stat .num { color: #4338ca; }
    strong { color: #1e293b; }
    .page-break { page-break-before: always; }
  }
</style>
</head>
<body>

<!-- COVER PAGE -->
<div class="cover">
  <div class="shield">🛡️</div>
  <h1 style="border:none; margin:0; font-size:42px;">Data Privacy & Security<br>Intelligence Platform</h1>
  <p class="subtitle">Complete Technical & Business Document</p>
  <div class="stats">
    <div class="stat"><div class="num">15</div><div class="label">Modes</div></div>
    <div class="stat"><div class="num">55</div><div class="label">AI Agents</div></div>
    <div class="stat"><div class="num">25</div><div class="label">A2UI Cards</div></div>
    <div class="stat"><div class="num">4</div><div class="label">Protocols</div></div>
  </div>
</div>

<!-- TABLE OF CONTENTS -->
<div class="toc">
  <h2>📑 Table of Contents</h2>
  <ol>
    <li><strong>Platform Overview</strong> — What, Why, Architecture</li>
    <li><strong>The 4 Protocols</strong> — AG-UI, A2UI, A2A, MCP</li>
    <li><strong>Mode 1:</strong> 🔍 Breach Analysis (7 agents)</li>
    <li><strong>Mode 2:</strong> 📚 Knowledge Search (4 agents)</li>
    <li><strong>Mode 3:</strong> ⚖️ Compliance Check (4 agents)</li>
    <li><strong>Mode 4:</strong> 📊 Risk Assessment (4 agents)</li>
    <li><strong>Mode 5:</strong> 🛡️ Safety Validation (4 agents)</li>
    <li><strong>Mode 6:</strong> 🚨 Incident Response (5 agents)</li>
    <li><strong>Mode 7:</strong> 🗺️ Data Mapping (3 agents)</li>
    <li><strong>Mode 8:</strong> 👤 Data Subject Rights (3 agents)</li>
    <li><strong>Mode 9:</strong> 🌐 Dark Web Monitor (3 agents)</li>
    <li><strong>Mode 10:</strong> 📝 Executive Reporting (3 agents)</li>
    <li><strong>Mode 11:</strong> 🎯 Threat Modeling (3 agents)</li>
    <li><strong>Mode 12:</strong> 🔓 Vulnerability Assessment (3 agents)</li>
    <li><strong>Mode 13:</strong> 🔐 Access Control & IAM (3 agents)</li>
    <li><strong>Mode 14:</strong> 🔬 Digital Forensics (3 agents)</li>
    <li><strong>Mode 15:</strong> 🏗️ Security Architecture (3 agents)</li>
    <li><strong>Complete Demo Script</strong> — 20-minute walkthrough</li>
  </ol>
</div>

${mdToHtml(fullContent)}

</body>
</html>`;

const outPath = path.join('C:\\Users\\Abhishek\\Documents\\AgenticUI\\dp_privacy', 'DP_Platform_Complete_Document.html');
fs.writeFileSync(outPath, htmlContent, 'utf-8');
console.log('HTML file created at:', outPath);
console.log('Open this file in your browser and press Ctrl+P to save as PDF');
