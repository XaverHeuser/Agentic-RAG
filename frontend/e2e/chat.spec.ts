import { test, expect } from '@playwright/test';

test('should send a message and get a response', async ({ page }) => {
  await page.goto('http://localhost:3000');
  
  // Text input
  await page.fill('input[placeholder*="Frag etwas"]', 'Was ist JavaScript?');
  
  // click send
  await page.click('button:has-text("Senden")');

  // Wait for message
  const assistantMessage = page.locator('.prose'); 
  await expect(assistantMessage).toBeVisible({ timeout: 30000 });
  
  // Check if text has content
  const text = await assistantMessage.innerText();
  expect(text.length).toBeGreaterThan(10);
});