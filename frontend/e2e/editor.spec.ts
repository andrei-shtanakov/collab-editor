import { test, expect } from '@playwright/test';

test.describe('Code Editor', () => {
  test('loads the editor on homepage', async ({ page }) => {
    await page.goto('/');

    // Check header elements
    await expect(page.locator('h1')).toContainText('Collaborative Editor');
    await expect(page.getByRole('combobox')).toBeVisible(); // Language selector
    await expect(page.getByRole('button', { name: /Run/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /Create & Share/i })).toBeVisible();

    // Check editor loads (Monaco takes a moment)
    await expect(page.locator('.monaco-editor')).toBeVisible({ timeout: 10000 });
  });

  test('can select different languages', async ({ page }) => {
    await page.goto('/');

    const selector = page.getByRole('combobox');
    await expect(selector).toHaveValue('python');

    // Change to JavaScript
    await selector.selectOption('javascript');
    await expect(selector).toHaveValue('javascript');
  });

  test('shows output panel', async ({ page }) => {
    await page.goto('/');

    // Output panel should show placeholder
    await expect(page.getByText(/Click "Run" to execute/i)).toBeVisible();
  });
});

test.describe('Code Execution', () => {
  test('runs code and shows output', async ({ page }) => {
    await page.goto('/');

    // Wait for editor
    await expect(page.locator('.monaco-editor')).toBeVisible({ timeout: 10000 });

    // Initially should show "Click Run" placeholder
    await expect(page.getByText(/Click "Run" to execute/i)).toBeVisible();

    // Click Run
    await page.getByRole('button', { name: /Run/i }).click();

    // Should show either "Running..." or execution result
    // Wait for the output panel to show something other than placeholder
    await expect(page.getByText(/Click "Run" to execute/i)).not.toBeVisible({ timeout: 60000 });
  });

  test('shows JavaScript execution result', async ({ page }) => {
    await page.goto('/');

    // Select JavaScript (faster than Python/Pyodide)
    await page.getByRole('combobox').selectOption('javascript');

    // Wait for editor
    await expect(page.locator('.monaco-editor')).toBeVisible({ timeout: 10000 });

    // Run the code
    await page.getByRole('button', { name: /Run/i }).click();

    // Should show "Running..." then result
    // Wait for placeholder to disappear
    await expect(page.getByText(/Click "Run" to execute/i)).not.toBeVisible({ timeout: 10000 });
  });

  test('shows error for unsupported languages', async ({ page }) => {
    await page.goto('/');

    // Select Go (not supported for browser execution)
    await page.getByRole('combobox').selectOption('go');

    // Click Run
    await page.getByRole('button', { name: /Run/i }).click();

    // Should show error message
    await expect(page.getByText(/not supported/i)).toBeVisible();
  });
});

test.describe('Session Management', () => {
  test('creates a new session', async ({ page }) => {
    await page.goto('/');

    // Click Create & Share
    await page.getByRole('button', { name: /Create & Share/i }).click();

    // Wait for session creation
    await expect(page.getByText(/Copy Link/i)).toBeVisible({ timeout: 10000 });

    // URL should have session parameter
    await expect(page).toHaveURL(/session=/);

    // Should show connected status
    await expect(page.getByText('Connected')).toBeVisible();
  });

  test('can copy session link', async ({ page, context }) => {
    await page.goto('/');

    // Create session
    await page.getByRole('button', { name: /Create & Share/i }).click();
    await expect(page.getByText(/Copy Link/i)).toBeVisible({ timeout: 10000 });

    // Grant clipboard permissions
    await context.grantPermissions(['clipboard-write', 'clipboard-read']);

    // Click copy
    await page.getByRole('button', { name: /Copy Link/i }).click();

    // Should show "Copied!"
    await expect(page.getByText('Copied!')).toBeVisible();
  });

  test('can join existing session via URL', async ({ page, context }) => {
    // First create a session
    await page.goto('/');
    await page.getByRole('button', { name: /Create & Share/i }).click();
    await expect(page.getByText(/Copy Link/i)).toBeVisible({ timeout: 10000 });

    // Get session ID from URL
    const url = page.url();
    const sessionId = new URL(url).searchParams.get('session');
    expect(sessionId).toBeTruthy();

    // Open new page with same session
    const page2 = await context.newPage();
    await page2.goto(`/?session=${sessionId}`);

    // Should connect
    await expect(page2.getByText('Connected')).toBeVisible({ timeout: 10000 });
    await expect(page2.locator('.monaco-editor')).toBeVisible({ timeout: 10000 });
  });
});
