// render.mjs — turn a built report HTML into a PDF without opening a browser by hand.
//   node render.mjs [spec.html] [spec.pdf]
// Loads the HTML, lets Paged.js paginate, then prints to A4 PDF. This is a
// convenience / CI path; the everyday path is just: open the HTML, Ctrl+P, Save as PDF.

import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import puppeteer from 'puppeteer';

const here = path.dirname(fileURLToPath(import.meta.url));
const inHtml = path.resolve(here, process.argv[2] || 'spec.html');
const outPdf = path.resolve(here, process.argv[3] || inHtml.replace(/\.html$/, '.pdf'));

const browser = await puppeteer.launch({ headless: 'new', args: ['--no-sandbox'] });
const page = await browser.newPage();

// Tell Paged.js to flag when it has finished laying out the pages.
await page.evaluateOnNewDocument(() => {
  window.PagedConfig = { auto: true, after: () => { window.__pagedDone = true; } };
});

await page.goto(pathToFileURL(inHtml).href, { waitUntil: 'networkidle0', timeout: 120000 });
await page.waitForFunction('window.__pagedDone === true', { timeout: 120000 });

await page.pdf({ path: outPdf, printBackground: true, preferCSSPageSize: true });
await browser.close();

console.log(`wrote ${path.relative(process.cwd(), outPdf)}`);
