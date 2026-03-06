/**
 * 🛡️ Cybersecurity Encyclopedia - PDF Generator
 * 
 * Usage: node generate_chapter_pdf.js [chapter_number]
 *   - node generate_chapter_pdf.js 1        → generates Chapter 1 PDF
 *   - node generate_chapter_pdf.js all      → generates ALL chapter PDFs
 * 
 * Reads markdown from chapters/ folder, generates beautiful HTML+CSS styled
 * files in pdfs/ folder. Open in browser → Ctrl+P → Save as PDF.
 */
const fs = require('fs');
const path = require('path');

const CHAPTERS_DIR = path.join(__dirname, 'chapters');
const PDFS_DIR = path.join(__dirname, 'pdfs');

// ─── Markdown → HTML converter ──────────────────────────────────────
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
  html = html.replace(/^##### (.+)$/gm, '<h5>$1</h5>');
  html = html.replace(/^#### (.+)$/gm, '<h4>$1</h4>');
  html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
  html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
  html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');
  // Bold + Italic
  html = html.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>');
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
  // Inline code
  html = html.replace(/`([^`]+)`/g, '<code class="inline">$1</code>');
  // Unordered lists
  html = html.replace(/^- (.+)$/gm, '<li>$1</li>');
  html = html.replace(/(<li>.*<\/li>\n?)+/g, (m) => `<ul>${m}</ul>`);
  // Numbered lists
  html = html.replace(/^\d+\. (.+)$/gm, '<li class="ol">$1</li>');
  html = html.replace(/(<li class="ol">.*<\/li>\n?)+/g, (m) => `<ol>${m.replace(/ class="ol"/g, '')}</ol>`);
  // Horizontal rules
  html = html.replace(/^---$/gm, '<hr>');
  // Blockquotes (multi-level)
  html = html.replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>');
  // Paragraphs
  html = html.replace(/^(?!<[huptblodhr])((?!<).+)$/gm, '<p>$1</p>');
  // Emoji callout boxes
  html = html.replace(/<p>🔴(.+?)<\/p>/g, '<div class="callout danger"><p>🔴$1</p></div>');
  html = html.replace(/<p>🟡(.+?)<\/p>/g, '<div class="callout warning"><p>🟡$1</p></div>');
  html = html.replace(/<p>🟢(.+?)<\/p>/g, '<div class="callout success"><p>🟢$1</p></div>');
  html = html.replace(/<p>💡(.+?)<\/p>/g, '<div class="callout tip"><p>💡$1</p></div>');
  html = html.replace(/<p>⚠️(.+?)<\/p>/g, '<div class="callout warning"><p>⚠️$1</p></div>');
  html = html.replace(/<p>📌(.+?)<\/p>/g, '<div class="callout info"><p>📌$1</p></div>');
  return html;
}

// ─── HTML Template ──────────────────────────────────────────────────
function generateHTML(chapterMd, chapterNum, partNum, partTitle) {
  const content = mdToHtml(chapterMd);

  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Cybersecurity Encyclopedia - Chapter ${chapterNum}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    font-family: 'Inter', -apple-system, sans-serif;
    background: #0a0e1a;
    color: #e0e4ef;
    line-height: 1.8;
    padding: 50px 60px;
    max-width: 900px;
    margin: 0 auto;
  }

  /* ─── CHAPTER HEADER ─── */
  .chapter-header {
    text-align: center;
    padding: 60px 40px;
    margin-bottom: 50px;
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.9), rgba(30, 41, 59, 0.8));
    border: 1px solid rgba(99, 102, 241, 0.25);
    border-radius: 24px;
    position: relative;
    overflow: hidden;
  }
  .chapter-header::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(circle at 30% 40%, rgba(99, 102, 241, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 70% 60%, rgba(34, 211, 238, 0.06) 0%, transparent 50%);
  }
  .chapter-header .part-label {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 3px;
    color: #6366f1;
    font-weight: 700;
    margin-bottom: 12px;
    position: relative;
  }
  .chapter-header .chapter-num {
    font-size: 72px;
    font-weight: 900;
    background: linear-gradient(135deg, #6366f1, #22d3ee);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1;
    margin-bottom: 16px;
    position: relative;
  }
  .chapter-header .chapter-title {
    font-size: 28px;
    font-weight: 800;
    color: #f1f5f9;
    margin-bottom: 12px;
    position: relative;
  }
  .chapter-header .chapter-subtitle {
    font-size: 15px;
    color: #94a3b8;
    font-weight: 400;
    font-style: italic;
    position: relative;
  }

  /* ─── HEADINGS ─── */
  h1 {
    font-size: 30px;
    font-weight: 800;
    color: #f1f5f9;
    margin: 50px 0 20px;
    padding-bottom: 12px;
    border-bottom: 2px solid rgba(99, 102, 241, 0.3);
  }
  h2 {
    font-size: 23px;
    font-weight: 700;
    color: #c7d2fe;
    margin: 40px 0 16px;
    padding-left: 16px;
    border-left: 4px solid #6366f1;
  }
  h3 {
    font-size: 18px;
    font-weight: 600;
    color: #a5b4fc;
    margin: 30px 0 12px;
  }
  h4 {
    font-size: 15px;
    font-weight: 600;
    color: #818cf8;
    margin: 22px 0 10px;
  }
  h5 {
    font-size: 13px;
    font-weight: 600;
    color: #22d3ee;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 18px 0 8px;
  }

  /* ─── TEXT ─── */
  p {
    margin: 12px 0;
    color: #cbd5e1;
    font-size: 14.5px;
    line-height: 1.85;
  }
  strong { color: #f1f5f9; }
  em { color: #c7d2fe; }

  /* ─── STORY BOX ─── */
  .story-box {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.08), rgba(34, 211, 238, 0.04));
    border: 1px solid rgba(99, 102, 241, 0.2);
    border-radius: 16px;
    padding: 24px 28px;
    margin: 24px 0;
    position: relative;
  }
  .story-box::before {
    content: '🎬';
    position: absolute;
    top: -12px;
    left: 20px;
    font-size: 20px;
    background: #0a0e1a;
    padding: 0 8px;
  }
  .story-box h4 {
    color: #22d3ee;
    margin-top: 4px;
  }

  /* ─── TABLES ─── */
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 24px 0;
    font-size: 13px;
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(99, 102, 241, 0.15);
    border-radius: 12px;
    overflow: hidden;
  }
  th {
    background: rgba(99, 102, 241, 0.15);
    color: #c7d2fe;
    padding: 14px 16px;
    text-align: left;
    font-weight: 600;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  td {
    padding: 12px 16px;
    border-top: 1px solid rgba(99, 102, 241, 0.08);
    color: #cbd5e1;
  }
  tr:nth-child(even) { background: rgba(99, 102, 241, 0.03); }

  /* ─── CODE ─── */
  pre.code-block {
    background: rgba(15, 23, 42, 0.9);
    border: 1px solid rgba(99, 102, 241, 0.15);
    border-radius: 12px;
    padding: 20px 24px;
    margin: 20px 0;
    overflow-x: auto;
    font-size: 12.5px;
    line-height: 1.7;
  }
  pre.code-block code {
    color: #a5b4fc;
    font-family: 'JetBrains Mono', monospace;
  }
  code.inline {
    background: rgba(99, 102, 241, 0.15);
    color: #a5b4fc;
    padding: 2px 7px;
    border-radius: 5px;
    font-size: 13px;
    font-family: 'JetBrains Mono', monospace;
  }

  /* ─── LISTS ─── */
  ul, ol {
    margin: 14px 0 14px 28px;
    color: #cbd5e1;
    font-size: 14.5px;
  }
  li {
    margin: 8px 0;
    line-height: 1.7;
  }
  li::marker { color: #6366f1; }

  /* ─── BLOCKQUOTE ─── */
  blockquote {
    border-left: 4px solid #6366f1;
    padding: 16px 24px;
    margin: 20px 0;
    background: rgba(99, 102, 241, 0.06);
    border-radius: 0 12px 12px 0;
    color: #c7d2fe;
    font-style: italic;
    font-size: 15px;
  }

  /* ─── CALLOUT BOXES ─── */
  .callout {
    border-radius: 12px;
    padding: 16px 20px;
    margin: 16px 0;
    border: 1px solid;
  }
  .callout.danger {
    background: rgba(239, 68, 68, 0.06);
    border-color: rgba(239, 68, 68, 0.2);
  }
  .callout.warning {
    background: rgba(245, 158, 11, 0.06);
    border-color: rgba(245, 158, 11, 0.2);
  }
  .callout.success {
    background: rgba(34, 197, 94, 0.06);
    border-color: rgba(34, 197, 94, 0.2);
  }
  .callout.tip {
    background: rgba(99, 102, 241, 0.06);
    border-color: rgba(99, 102, 241, 0.2);
  }
  .callout.info {
    background: rgba(34, 211, 238, 0.06);
    border-color: rgba(34, 211, 238, 0.2);
  }
  .callout p { margin: 0; }

  hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.3), transparent);
    margin: 40px 0;
  }

  /* ─── TIMELINE ─── */
  .timeline-item {
    padding-left: 30px;
    border-left: 2px solid rgba(99, 102, 241, 0.3);
    margin: 16px 0;
    position: relative;
  }
  .timeline-item::before {
    content: '';
    position: absolute;
    left: -6px;
    top: 6px;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: #6366f1;
  }

  /* ─── KEY TAKEAWAYS ─── */
  .takeaways {
    background: linear-gradient(135deg, rgba(34, 197, 94, 0.06), rgba(34, 211, 238, 0.04));
    border: 1px solid rgba(34, 197, 94, 0.2);
    border-radius: 16px;
    padding: 24px 28px;
    margin: 30px 0;
  }
  .takeaways h3 { color: #22c55e; margin-top: 0; }

  /* ─── FOOTER ─── */
  .chapter-footer {
    margin-top: 60px;
    padding: 24px;
    text-align: center;
    border-top: 1px solid rgba(99, 102, 241, 0.15);
    color: #64748b;
    font-size: 12px;
  }
  .chapter-footer .next {
    margin-top: 12px;
    color: #6366f1;
    font-weight: 600;
    font-size: 14px;
  }

  /* ─── PRINT STYLES ─── */
  @media print {
    body { background: white; color: #1e293b; padding: 30px; }
    .chapter-header { background: #f8fafc; border-color: #6366f1; }
    .chapter-header .chapter-num { -webkit-text-fill-color: #4338ca; }
    .chapter-header .chapter-title { color: #1e293b; }
    .chapter-header .part-label { color: #6366f1; }
    .chapter-header .chapter-subtitle { color: #64748b; }
    h1 { color: #1e293b; border-bottom-color: #6366f1; }
    h2 { color: #4338ca; border-left-color: #6366f1; }
    h3 { color: #4f46e5; }
    h4 { color: #6366f1; }
    p, li, td { color: #334155; }
    strong { color: #1e293b; }
    th { background: #e0e7ff; color: #312e81; }
    td { border-top-color: #e2e8f0; }
    table { border-color: #e2e8f0; background: #f8fafc; }
    pre.code-block { background: #f8fafc; border-color: #e2e8f0; }
    pre.code-block code { color: #4338ca; }
    code.inline { background: #e0e7ff; color: #4338ca; }
    blockquote { background: #f0f0ff; color: #4338ca; }
    .story-box { background: #f0f4ff; border-color: #c7d2fe; }
    .takeaways { background: #f0fdf4; border-color: #86efac; }
    .callout.danger { background: #fef2f2; }
    .callout.warning { background: #fffbeb; }
    .callout.success { background: #f0fdf4; }
    .callout.tip { background: #eef2ff; }
    .chapter-footer { border-top-color: #e2e8f0; }
    .page-break { page-break-before: always; }
  }
</style>
</head>
<body>

<div class="chapter-header">
  <div class="part-label">Part ${partNum} — ${partTitle}</div>
  <div class="chapter-num">${String(chapterNum).padStart(2, '0')}</div>
  <div class="chapter-title" id="chapter-title"></div>
  <div class="chapter-subtitle" id="chapter-subtitle"></div>
</div>

${content}

<div class="chapter-footer">
  <div>🛡️ The Cybersecurity Encyclopedia — Chapter ${chapterNum}</div>
  <div>© 2026 | From the First Hack to the Last Firewall</div>
</div>

<script>
  // Extract title from first h1
  const h1 = document.querySelector('h1');
  if (h1) {
    document.getElementById('chapter-title').textContent = h1.textContent;
    h1.style.display = 'none';
  }
  // Extract subtitle from first blockquote
  const bq = document.querySelector('blockquote');
  if (bq) {
    document.getElementById('chapter-subtitle').textContent = bq.textContent;
    bq.style.display = 'none';
  }
</script>

</body>
</html>`;
}

// ─── Chapter metadata ───────────────────────────────────────────────
const CHAPTER_META = {
  1: { part: 'I', partTitle: 'The Genesis (1960s–1970s)' },
  2: { part: 'I', partTitle: 'The Genesis (1960s–1970s)' },
  3: { part: 'I', partTitle: 'The Genesis (1960s–1970s)' },
  4: { part: 'II', partTitle: 'The Wild West (1990s)' },
  5: { part: 'II', partTitle: 'The Wild West (1990s)' },
  6: { part: 'II', partTitle: 'The Wild West (1990s)' },
  7: { part: 'II', partTitle: 'The Wild West (1990s)' },
  8: { part: 'III', partTitle: 'The Awakening (2000s)' },
  9: { part: 'III', partTitle: 'The Awakening (2000s)' },
  10: { part: 'III', partTitle: 'The Awakening (2000s)' },
  11: { part: 'III', partTitle: 'The Awakening (2000s)' },
  12: { part: 'IV', partTitle: 'The Stuxnet Era (2007–2012)' },
  13: { part: 'IV', partTitle: 'The Stuxnet Era (2007–2012)' },
  14: { part: 'IV', partTitle: 'The Stuxnet Era (2007–2012)' },
  15: { part: 'IV', partTitle: 'The Stuxnet Era (2007–2012)' },
  16: { part: 'V', partTitle: 'The Age of Mega-Breaches (2013–2016)' },
  17: { part: 'V', partTitle: 'The Age of Mega-Breaches (2013–2016)' },
  18: { part: 'V', partTitle: 'The Age of Mega-Breaches (2013–2016)' },
  19: { part: 'V', partTitle: 'The Age of Mega-Breaches (2013–2016)' },
  20: { part: 'VI', partTitle: 'Ransomware: The Digital Pandemic (2017–2020)' },
};

// ─── Main ───────────────────────────────────────────────────────────
const arg = process.argv[2];
if (!arg) {
  console.log('Usage: node generate_chapter_pdf.js <chapter_number|all>');
  process.exit(1);
}

const chapters = arg === 'all'
  ? fs.readdirSync(CHAPTERS_DIR).filter(f => f.endsWith('.md')).sort()
  : [`chapter_${String(arg).padStart(2, '0')}.md`];

chapters.forEach(filename => {
  const filePath = path.join(CHAPTERS_DIR, filename);
  if (!fs.existsSync(filePath)) {
    console.log(`⚠️  ${filename} not found, skipping`);
    return;
  }
  const md = fs.readFileSync(filePath, 'utf-8');
  const num = parseInt(filename.match(/(\d+)/)[1]);
  const meta = CHAPTER_META[num] || { part: '?', partTitle: 'Unknown' };

  const html = generateHTML(md, num, meta.part, meta.partTitle);
  const outFile = path.join(PDFS_DIR, filename.replace('.md', '.html'));
  fs.writeFileSync(outFile, html, 'utf-8');
  console.log(`✅ Generated: ${outFile}`);
  console.log(`   → Open in browser → Ctrl+P → Save as PDF`);
});

console.log('\\n🎉 Done! Open the HTML files in your browser and print to PDF.');
