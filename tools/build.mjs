// build.mjs — flatten one or more Markdown files into a styled, A4 print-to-PDF report.
//
//   node build.mjs out=spec.html title="..." subtitle="..." ../draft5.1-1.md ../draft5.1-2.md
//
// Output: a single self-contained HTML file (theme.css alongside it) that Paged.js
// flows onto A4 pages with a cover, a table of contents, running headers, and page
// numbers. Open it in a browser -> Ctrl/Cmd+P -> Save as PDF (paper A4, margins None,
// "Background graphics" ON). Same export habit as post/p8.content.html.

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import MarkdownIt from 'markdown-it';
import anchor from 'markdown-it-anchor';

const here = path.dirname(fileURLToPath(import.meta.url));

// ---- parse key=value options and positional .md files ----------------------
const opts = {};
const files = [];
for (const a of process.argv.slice(2)) {
  const m = a.match(/^([a-zA-Z]+)=(.*)$/s);
  if (m) opts[m[1]] = m[2];
  else files.push(a);
}
if (files.length === 0) {
  console.error('usage: node build.mjs [out=spec.html] [title="..."] [subtitle="..."] file1.md [file2.md ...]');
  process.exit(1);
}

const outPath   = path.resolve(here, opts.out || 'spec.html');
const title     = opts.title    || 'Specification';
const subtitle  = opts.subtitle || '';
const metaLine  = opts.meta     || 'github.com/Jakkarin-Promsee/bio-analog-cpu';

// ---- markdown -> html ------------------------------------------------------
const slugify = s => '§' + s.trim().toLowerCase()
  .replace(/[^\w\s.-]/g, '')
  .replace(/[\s.]+/g, '-')
  .replace(/-+/g, '-')
  .replace(/^-+|-+$/g, '');

const md = new MarkdownIt({ html: true, linkify: false, typographer: false, breaks: false });
md.use(anchor, { level: [1, 2, 3], slugify, tabIndex: false });

// Concatenate sources; a sentinel between files becomes a "part" page break.
const raw = files
  .map(f => fs.readFileSync(path.resolve(here, f), 'utf8'))
  .join('\n\n<hr class="partbreak">\n\n');

const env = {};
const tokens = md.parse(raw, env);

// ---- table of contents (from h2 + h3) --------------------------------------
const toc = [];
for (let i = 0; i < tokens.length; i++) {
  const t = tokens[i];
  if (t.type === 'heading_open' && (t.tag === 'h2' || t.tag === 'h3')) {
    toc.push({ level: t.tag === 'h2' ? 2 : 3, id: t.attrGet('id'), text: tokens[i + 1].content });
  }
}
const tocHtml =
  '<nav class="toc">\n<h1 class="toc-title">Contents</h1>\n<ul>\n' +
  toc.map(e =>
    `<li class="lvl${e.level}"><a href="#${e.id}"><span class="t">${md.utils.escapeHtml(e.text)}</span></a></li>`
  ).join('\n') +
  '\n</ul>\n</nav>';

const bodyHtml = md.renderer.render(tokens, md.options, env);

const esc = md.utils.escapeHtml;
const html = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>${esc(title)}</title>
<link rel="stylesheet" href="theme.css">
</head>
<body>

<section class="cover">
  <p class="kicker">Bio-inspired Analog CPU</p>
  <h1 class="cover-title">${esc(title)}</h1>
  ${subtitle ? `<p class="cover-sub">${esc(subtitle)}</p>` : ''}
  <div class="cover-foot">
    <span>${esc(metaLine)}</span>
    <span>Draft 5.1</span>
  </div>
</section>

${tocHtml}

<main class="prose">
${bodyHtml}
</main>

<script src="https://unpkg.com/pagedjs/dist/paged.polyfill.js"></script>
</body>
</html>
`;

fs.writeFileSync(outPath, html);
console.log(`wrote ${path.relative(process.cwd(), outPath)}  ·  ${toc.length} TOC entries  ·  ${files.length} source file(s)`);
