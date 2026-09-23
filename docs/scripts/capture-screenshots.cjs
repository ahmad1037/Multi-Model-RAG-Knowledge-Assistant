// Capture real pages; never inject mocked responses or alter the displayed UI.
const path = require('node:path');
const fs = require('node:fs');
const playwright = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const output = path.resolve(__dirname, '../images');
const mode = process.argv[2] || 'inspect';
const url = process.argv[3] || 'http://localhost:5173';
(async () => {
  fs.mkdirSync(output, {recursive: true});
  const browser = await playwright.chromium.launch({headless: true, channel: 'msedge'});
  const page = await browser.newPage({viewport: {width: 1600, height: 1000}, deviceScaleFactor: 1});
  try {
    if (mode === 'grafana') {
      const login = await page.context().request.post('http://localhost:3000/login', {
        data: {user: process.env.GRAFANA_USER || 'admin', password: process.env.GRAFANA_PASSWORD || 'admin'}
      });
      if (!login.ok()) throw new Error('Grafana login failed');
    }
    await page.goto(url, {waitUntil: 'domcontentloaded', timeout: 90000});
    if (mode === 'azure-preview') await page.getByText('Multimodal RAG', {exact: true}).waitFor({timeout: 60000});
    if (mode === 'grafana') {
      await page.getByText('RAG Multi Modal', {exact: false}).first().waitFor({timeout: 30000});
      await page.waitForTimeout(8000); // Let real Prometheus query responses render.
    }
    if (mode === 'processing') {
      const api = page.context().request;
      const all = await (await api.get('http://localhost:8000/api/v1/knowledge-bases')).json();
      let kb = all.find(k => k.slug === 'documentation-capture');
      if (!kb) {
        const result = await api.post('http://localhost:8000/api/v1/knowledge-bases', {data: {
          name: 'Documentation Capture', slug: 'documentation-capture', description: 'Synthetic screenshot demo; excluded from benchmarks.'
        }});
        if (!result.ok()) throw new Error(await result.text());
        kb = await result.json();
      }
      await page.reload({waitUntil: 'networkidle'});
      await page.locator('select').selectOption(kb.id);
      await page.locator('input[type=file]').setInputFiles(path.resolve(__dirname, '../fixtures/processing-demo.md'));
      await page.locator('.processing-status progress[value]').waitFor({timeout: 30000});
      await page.screenshot({path: path.join(output, 'processing.png'), fullPage: true});
      console.log('CAPTURED PROCESSING', await page.locator('.processing-status').innerText());
      await page.waitForFunction(() => /complete|failed/.test(document.querySelector('.processing-status')?.innerText || ''), null, {timeout: 180000});
      console.log('FINAL PROCESSING', await page.locator('.processing-status').innerText());
    } else if (mode === 'chat' || mode === 'visual') {
      await page.locator('select option').filter({hasText: 'Retail Sales Forecasting'}).waitFor({state: 'attached'});
      await page.locator('select').selectOption({label: 'Retail Sales Forecasting'});
      await page.getByRole('textbox', {name: 'Your question'}).waitFor();
      await page.waitForFunction(() => !document.querySelector('textarea[aria-label="Your question"]').disabled);
      if (mode === 'chat') await page.screenshot({path: path.join(output, 'chat.png'), fullPage: true});
      await page.getByRole('textbox', {name: 'Your question'}).fill(mode === 'visual' ? 'On the Forecast Drivers page, what percentage of importance belongs to rolling mean 7? Cite the page image.' : 'Why was Gradient Boosting selected as the production model?');
      await page.getByRole('button', {name: 'Send', exact: true}).click();
      await page.waitForFunction(() => !document.querySelector('textarea[aria-label="Your question"]').disabled, null, {timeout: 180000});
      if (!await page.locator('.citation-chip').count()) throw new Error('Answer had no citations: ' + await page.locator('body').innerText());
      if (mode === 'chat') await page.screenshot({path: path.join(output, 'answer-citations.png'), fullPage: true});
      const chips = page.locator('.citation-chip');
      for (let i = (await chips.count()) - 1; i >= 0; i--) {
        await chips.nth(i).click();
        if (await page.locator('.source-image').count()) {
          await page.locator('.source-image').waitFor();
          await page.waitForFunction(() => document.querySelector('.source-image')?.naturalWidth > 0);
          await page.screenshot({path: path.join(output, 'visual-citation.png'), fullPage: true});
          break;
        }
      }
    } else if (mode !== 'inspect') {
      await page.screenshot({path: path.join(output, mode + '.png'), fullPage: true});
    }
    console.log((await page.locator('body').innerText()).slice(0, 16000));
    console.log('BUTTONS', await page.getByRole('button').allTextContents());
  } finally { await browser.close(); }
})().catch(error => { console.error(error.message); process.exitCode = 1; });
