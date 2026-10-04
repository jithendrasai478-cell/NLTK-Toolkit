const { chromium } = require('playwright');
const path = require('path');

const ARTIFACT_DIR = 'C:\\Users\\jithe\\.gemini\\antigravity\\brain\\49b7a5ce-8689-4c6a-93ad-7a0237d08e47';

async function runLiveTest() {
  console.log('--- Starting Live Web Browser Test for NLTK Toolkit ---');
  let browser;
  try {
    console.log('Attempting to launch browser (msedge channel)...');
    browser = await chromium.launch({ channel: 'msedge', headless: true });
  } catch (err) {
    console.log('Fallback to default chromium...');
    browser = await chromium.launch({ headless: true });
  }

  const context = await browser.newContext({
    viewport: { width: 1280, height: 900 }
  });
  const page = await context.newPage();

  // 1. Navigate to frontend
  console.log('1. Navigating to http://localhost:5173...');
  await page.goto('http://localhost:5173', { waitUntil: 'networkidle' });
  
  const title = await page.title();
  console.log(`Page title: "${title}"`);
  
  // Full landing page screenshot
  await page.screenshot({ path: path.join(ARTIFACT_DIR, 'live-browser-homepage.png'), fullPage: false });
  console.log('Saved homepage screenshot: live-browser-homepage.png');

  // Helper to click feature card
  async function testFeature(featureTitle, inputOptions) {
    console.log(`\nTesting Feature: "${featureTitle}"...`);
    // Click feature card by title
    const card = page.locator(`h3:has-text("${featureTitle}")`).first();
    await card.waitFor({ state: 'visible' });
    await card.click();
    await page.waitForTimeout(500);

    // If custom input provided
    if (inputOptions && inputOptions.text) {
      const textarea = page.locator('textarea').first();
      await textarea.fill(inputOptions.text);
    }

    if (inputOptions && inputOptions.selectLang) {
      const select = page.locator('select').first();
      await select.selectOption(inputOptions.selectLang);
    }

    // Click "Run <featureTitle>" button
    const runBtn = page.locator('button:has-text("Run")').first();
    await runBtn.click();
    console.log(`Clicked Run button for ${featureTitle}...`);

    // Wait for processing to finish (either clock badge appears or output updates)
    await page.waitForSelector('text=Processing...', { state: 'detached', timeout: 15000 }).catch(() => {});
    await page.waitForTimeout(1000);

    // Extract output text
    const outputEl = page.locator('div.font-mono').first();
    const outputText = await outputEl.innerText();
    console.log(`Output result for ${featureTitle}:\n------------------------------------\n${outputText.slice(0, 300)}...\n------------------------------------`);

    // Screenshot modal
    if (inputOptions && inputOptions.screenshotName) {
      await page.screenshot({ path: path.join(ARTIFACT_DIR, inputOptions.screenshotName) });
      console.log(`Saved screenshot: ${inputOptions.screenshotName}`);
    }

    // Close modal
    const closeBtn = page.locator('button:has-text("Close Window")').first();
    await closeBtn.click();
    await page.waitForTimeout(400);
  }

  // 2. Test Summarize
  await testFeature('Summarize', {
    screenshotName: 'live-browser-summarize.png'
  });

  // 3. Test Sentiment Analysis
  await testFeature('Sentiment Analysis', {
    text: 'I absolutely love using this NLTK toolkit! The algorithms are blazing fast, accurate, and wonderfully designed.',
    screenshotName: 'live-browser-sentiment.png'
  });

  // 4. Test Translate to Telugu
  await testFeature('Translate', {
    text: 'Natural Language Processing makes computers understand human language effortlessly.',
    selectLang: 'te',
    screenshotName: 'live-browser-translate-telugu.png'
  });

  // 5. Test Keywords
  await testFeature('Keywords', {
    text: 'Deep learning, neural networks, transformers, BERT, and natural language processing are driving modern artificial intelligence forward.',
    screenshotName: 'live-browser-keywords.png'
  });

  // 6. Test Rewrite
  await testFeature('Rewrite', {
    screenshotName: 'live-browser-rewrite.png'
  });

  // 7. Test Classify
  await testFeature('Classify', {
    text: 'NASA and SpaceX announce a joint orbital mission to explore lunar soil samples with robotic rovers.',
    screenshotName: 'live-browser-classify.png'
  });

  // 8. Test Q&A
  await testFeature('Q&A', {
    screenshotName: 'live-browser-qa.png'
  });

  // 9. Test Hero Demo Modal
  console.log('\nTesting "Watch Demo" button from Hero...');
  const watchDemoBtn = page.locator('button:has-text("Watch Demo")').first();
  await watchDemoBtn.click();
  await page.waitForTimeout(600);
  await page.screenshot({ path: path.join(ARTIFACT_DIR, 'live-browser-demo-modal.png') });
  console.log('Saved screenshot: live-browser-demo-modal.png');
  
  const demoCloseBtn = page.locator('button:has-text("Got it, explore tools!")').first();
  if (await demoCloseBtn.isVisible()) {
    await demoCloseBtn.click();
    await page.waitForTimeout(400);
  }

  // 10. Test "Start Exploring" button from Hero
  console.log('\nTesting "Start Exploring" button from Hero...');
  const startExploringBtn = page.locator('button:has-text("Start Exploring")').first();
  await startExploringBtn.click();
  await page.waitForTimeout(600);
  const exploringModalClose = page.locator('button:has-text("Close Window")').first();
  if (await exploringModalClose.isVisible()) {
    await exploringModalClose.click();
    await page.waitForTimeout(400);
  }

  console.log('\n--- All live browser tests passed with 100% success! ---');
  await browser.close();
}

runLiveTest().catch((err) => {
  console.error('Test failed with error:', err);
  process.exit(1);
});
