const { chromium } = require('playwright');
const path = require('path');

async function testTokenizerUI() {
  console.log('====================================================');
  console.log('STARTING END-TO-END BROWSER TEST FOR TOKENIZER TOOL');
  console.log('====================================================');

  let browser;
  try {
    browser = await chromium.launch({ channel: 'msedge', headless: true });
  } catch {
    browser = await chromium.launch({ headless: true });
  }

  const context = await browser.newContext({
    viewport: { width: 1280, height: 900 }
  });
  const page = await context.newPage();

  // 1. Navigate to frontend
  console.log('Navigating to http://localhost:5173 ...');
  await page.goto('http://localhost:5173', { waitUntil: 'networkidle' });

  // 2. Log in if redirected to /login
  if (page.url().includes('/login')) {
    console.log('Logging in with demo credentials...');
    await page.fill('#auth-email', 'demo@nltk.org');
    await page.fill('#auth-password', 'DemoPassword123!');
    await page.click('button[type="submit"]');
    await page.waitForURL('http://localhost:5173/', { timeout: 10000 });
    console.log('Logged in successfully!');
  }

  await page.waitForTimeout(600);

  // 3. Click on the "More Tools" card
  console.log('Locating and clicking "More Tools" card in FeatureGrid...');
  const card = page.locator('h3:has-text("More Tools")').first();
  await card.scrollIntoViewIfNeeded();
  await card.click();
  await page.waitForTimeout(600);

  // Verify modal is open by checking Close Window button and title
  const closeBtn = page.locator('button:has-text("Close Window")').first();
  await closeBtn.waitFor({ state: 'visible', timeout: 5000 });
  console.log('Interactive Modal opened for More Tools (Tokenizer).');

  const textarea = page.locator('textarea').first();
  const runBtn = page.locator('button:has-text("Run More Tools"), button:has-text("Run")').first();
  const outputEl = page.locator('div.font-mono').first();

  async function runAndVerify(inputString, validations, description) {
    console.log(`\n--- [TEST] ${description} ---`);
    console.log(`Setting input: ${JSON.stringify(inputString)}`);
    await textarea.fill(inputString);
    await page.waitForTimeout(200);

    await runBtn.click();
    console.log('Clicked Run button, waiting for result...');

    // Wait for processing spinner to detach
    await page.waitForSelector('text=Processing...', { state: 'detached', timeout: 8000 }).catch(() => {});
    await page.waitForTimeout(800);

    const outputText = await outputEl.innerText();
    console.log(`Output received:\n------------------------------------\n${outputText}\n------------------------------------`);

    for (const [key, expected] of Object.entries(validations)) {
      if (!outputText.includes(expected)) {
        throw new Error(`FAIL: Expected output to contain '${expected}', but got:\n${outputText}`);
      }
      console.log(`  ✓ Verified output contains: ${JSON.stringify(expected)}`);
    }
    return outputText;
  }

  // --- TEST CASE 1: Function-style word_tokenize ---
  await runAndVerify(
    'word_tokenize("Let\'s tokenize this sentence!")',
    {
      'Input Text': 'Input Text:\nLet\'s tokenize this sentence!',
      'Processing Method': 'Processing Method:\nNLTK word_tokenize',
      'Library Used': 'Library Used:\nNLTK',
      'Token Count': 'Token Count:\n6',
      'Sentence Count': 'Sentence Count:\n1',
      'Character Count': 'Character Count:\n29',
      'Token Let': '"Let"',
      'Token \'s': '"\'s"',
      'Token tokenize': '"tokenize"',
      'Token this': '"this"',
      'Token sentence': '"sentence"',
      'Token !': '"!"'
    },
    'Case 1: Function-style word_tokenize("Let\'s tokenize this sentence!")'
  );

  // --- TEST CASE 2: Normal Text "Hello world." ---
  await runAndVerify(
    'Hello world.',
    {
      'Input Text': 'Input Text:\nHello world.',
      'Processing Method': 'Processing Method:\nNLTK word_tokenize',
      'Library Used': 'Library Used:\nNLTK',
      'Token Count': 'Token Count:\n3',
      'Sentence Count': 'Sentence Count:\n1',
      'Character Count': 'Character Count:\n12',
      'Token Hello': '"Hello"',
      'Token world': '"world"',
      'Token dot': '"."'
    },
    'Case 2: Normal Text "Hello world."'
  );

  // --- TEST CASE 3: Dynamic change to "Hello! How are you?" ---
  await runAndVerify(
    'Hello! How are you?',
    {
      'Input Text': 'Input Text:\nHello! How are you?',
      'Token Count': 'Token Count:\n6',
      'Sentence Count': 'Sentence Count:\n2',
      'Character Count': 'Character Count:\n19'
    },
    'Case 3: Dynamic change to "Hello! How are you?"'
  );

  // --- TEST CASE 4: Dynamic change to "Natural Language Processing is interesting." ---
  await runAndVerify(
    'Natural Language Processing is interesting.',
    {
      'Input Text': 'Input Text:\nNatural Language Processing is interesting.',
      'Token Count': 'Token Count:\n6',
      'Sentence Count': 'Sentence Count:\n1',
      'Character Count': 'Character Count:\n43'
    },
    'Case 4: Dynamic change to "Natural Language Processing is interesting."'
  );

  // --- TEST CASE 5: Dynamic change to "I love NLP." ---
  await runAndVerify(
    'I love NLP.',
    {
      'Input Text': 'Input Text:\nI love NLP.',
      'Token Count': 'Token Count:\n4',
      'Sentence Count': 'Sentence Count:\n1',
      'Character Count': 'Character Count:\n11'
    },
    'Case 5: Dynamic change to "I love NLP."'
  );

  // --- TEST CASE 6: Function-style sent_tokenize ---
  await runAndVerify(
    'sent_tokenize("Let\'s test sentence one. Here is sentence two!")',
    {
      'Input Text': 'Input Text:\nLet\'s test sentence one. Here is sentence two!',
      'Processing Method': 'Processing Method:\nNLTK sent_tokenize',
      'Sentence Count': 'Sentence Count:\n2',
      'Token Count': 'Token Count:\n11'
    },
    'Case 6: Function-style sent_tokenize'
  );

  // --- TEST CASE 7: Unsupported Function Error Rejection ---
  console.log('\n--- [TEST] Case 7: Security check with os.system("rm -rf /") ---');
  await textarea.fill('os.system("rm -rf /")');
  await runBtn.click();
  await page.waitForTimeout(600);
  const errorAlert = page.locator('text=Unsupported NLP function');
  await errorAlert.waitFor({ state: 'visible', timeout: 5000 });
  const errorText = await errorAlert.innerText();
  console.log(`✓ Verified error alert appeared: "${errorText}"`);

  console.log('\n====================================================');
  console.log('ALL 7 E2E TOKENIZER TESTS PASSED WITH 100% SUCCESS!');
  console.log('====================================================');

  await browser.close();
}

testTokenizerUI().catch(err => {
  console.error('TEST FAILED:', err);
  process.exit(1);
});
