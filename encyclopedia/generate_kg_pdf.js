const fs = require('fs');
const path = require('path');

const md = fs.readFileSync(
    path.join(__dirname, 'chapters', 'knowledge_graph_implementation_guide.md'),
    'utf8'
);

function mdToHtml(text) {
    // Code blocks first
    text = text.replace(/```(\w*)\r?\n([\s\S]*?)```/g, (m, lang, code) => {
        code = code.replace(/</g, '&lt;').replace(/>/g, '&gt;');
        return '<pre><code class="' + (lang || '') + '">' + code + '</code></pre>';
    });

    // Inline code
    text = text.replace(/`([^`]+)`/g, '<code class="inline">$1</code>');

    // Headers
    text = text.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    text = text.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    text = text.replace(/^# (.*$)/gim, '<h1>$1</h1>');

    // Bold and italic
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');

    // Tables
    const lines = text.split('\n');
    const result = [];
    let inTable = false;
    let headerDone = false;

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        if (line.startsWith('|') && line.endsWith('|')) {
            if (/^\|[\s\-:|]+\|$/.test(line)) {
                headerDone = true;
                continue;
            }
            if (!inTable) {
                result.push('<table>');
                inTable = true;
            }
            const cells = line.split('|').filter(c => c.trim());
            const tag = !headerDone ? 'th' : 'td';
            result.push(
                '<tr>' +
                cells.map(c => '<' + tag + '>' + c.trim() + '</' + tag + '>').join('') +
                '</tr>'
            );
        } else {
            if (inTable) {
                result.push('</table>');
                inTable = false;
                headerDone = false;
            }
            result.push(lines[i]);
        }
    }
    if (inTable) result.push('</table>');
    text = result.join('\n');

    // Horizontal rules
    text = text.replace(/^---$/gm, '<hr>');

    // Lists
    text = text.replace(/^- (.*$)/gim, '<li>$1</li>');
    text = text.replace(/^(\d+)\. (.*$)/gim, '<li>$2</li>');

    // Paragraphs
    text = text.replace(/\n\n/g, '</p>\n<p>');

    return '<p>' + text + '</p>';
}

const htmlContent = mdToHtml(md);

const fullHtml = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Agentic Knowledge Graph — Complete Implementation Guide</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: 'Inter', sans-serif;
  background: #0a0e1a;
  color: #e2e8f0;
  line-height: 1.8;
  padding: 50px;
  max-width: 950px;
  margin: 0 auto;
}

.cover {
  text-align: center;
  padding: 60px 0 40px;
  border-bottom: 3px solid #1e3a5f;
  margin-bottom: 40px;
}
.cover-title {
  font-size: 36px;
  font-weight: 700;
  background: linear-gradient(135deg, #60a5fa, #a78bfa, #22d3ee);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 10px;
  border: none;
}
.cover .subtitle {
  font-size: 18px;
  color: #94a3b8;
  font-weight: 300;
}
.cover .badge {
  display: inline-block;
  background: linear-gradient(135deg, #1e40af, #7c3aed);
  color: white;
  padding: 6px 20px;
  border-radius: 20px;
  font-size: 13px;
  margin-top: 15px;
}

h1 {
  color: #60a5fa;
  font-size: 26px;
  margin-top: 50px;
  margin-bottom: 15px;
  padding-bottom: 8px;
  border-bottom: 2px solid #1e3a5f;
}
h2 {
  color: #38bdf8;
  font-size: 20px;
  margin-top: 35px;
  margin-bottom: 12px;
}
h3 {
  color: #22d3ee;
  font-size: 17px;
  margin-top: 25px;
  margin-bottom: 10px;
}
p { margin-bottom: 12px; }
strong { color: #f1f5f9; }

pre {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 10px;
  padding: 18px;
  overflow-x: auto;
  font-size: 12.5px;
  line-height: 1.6;
  margin: 16px 0;
}
code {
  font-family: 'JetBrains Mono', monospace;
  color: #a5f3fc;
}
code.inline {
  background: #1e293b;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin: 16px 0;
  border-radius: 8px;
  overflow: hidden;
}
th {
  background: #1e3a5f;
  color: #60a5fa;
  padding: 10px 14px;
  text-align: left;
  font-weight: 600;
  font-size: 13px;
}
td {
  padding: 10px 14px;
  border-bottom: 1px solid #1e293b;
  font-size: 13px;
}
tr:nth-child(odd) td { background: #0f172a; }
tr:nth-child(even) td { background: #1e293b; }

hr {
  border: none;
  border-top: 2px solid #1e293b;
  margin: 35px 0;
}
li {
  margin: 6px 0;
  padding-left: 5px;
  list-style-position: inside;
}
a { color: #60a5fa; }

@media print {
  body {
    background: white;
    color: #1e293b;
    padding: 30px;
    font-size: 11px;
    line-height: 1.5;
  }
  .cover-title {
    background: none;
    -webkit-text-fill-color: #1e40af;
    color: #1e40af;
  }
  .cover .subtitle { color: #475569; }
  .cover .badge { background: #1e40af; }
  h1 { color: #1e40af; border-bottom-color: #cbd5e1; font-size: 22px; }
  h2 { color: #0369a1; font-size: 17px; }
  h3 { color: #0e7490; font-size: 14px; }
  pre {
    background: #f1f5f9;
    border: 1px solid #cbd5e1;
    font-size: 10px;
    page-break-inside: avoid;
  }
  code { color: #0e7490; }
  code.inline { background: #f1f5f9; color: #0e7490; }
  th { background: #e2e8f0; color: #1e40af; }
  td { border-bottom-color: #e2e8f0; }
  tr:nth-child(odd) td { background: #f8fafc; }
  tr:nth-child(even) td { background: #ffffff; }
  hr { border-top-color: #e2e8f0; }
  strong { color: #1e293b; }
}
</style>
</head>
<body>

<div class="cover">
  <div class="cover-title">Agentic Knowledge Graph</div>
  <div class="subtitle">Complete Implementation Guide</div>
  <div class="subtitle" style="margin-top:8px;">Zenia Data Privacy Platform — Fake News Detection</div>
  <div class="badge">A2UI + Cytoscape.js + Python Backend</div>
</div>

${htmlContent}

<div style="text-align:center; margin-top:60px; padding:30px; border-top:2px solid #1e293b; color:#64748b;">
  <p>Agentic Knowledge Graph — Implementation Guide v1.0</p>
  <p>Zenia Data Privacy Platform &bull; March 2026</p>
</div>

</body>
</html>`;

const outPath = path.join(__dirname, 'pdfs', 'knowledge_graph_implementation_guide.html');
fs.writeFileSync(outPath, fullHtml, 'utf8');
console.log('✅ Generated: ' + outPath);
console.log('   → Open in Chrome → Ctrl+P → Save as PDF');
