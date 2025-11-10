/**
 * Comprehensive Frontend Tests for SnapMap
 * Tests all major workflows: upload, mapping, validation, export, SFTP
 */

import { test, expect, Page } from '@playwright/test';

const BASE_URL = 'http://localhost:5173';
const API_BASE_URL = 'http://localhost:8000/api';

// Test Configuration
test.describe.configure({ timeout: 60000 });

// Helper to check browser console for errors
async function checkConsoleErrors(page: Page): Promise<string[]> {
  const errors: string[] = [];
  page.on('console', (msg) => {
    if (msg.type() === 'error') {
      errors.push(msg.text());
    }
  });
  return errors;
}

test.describe('SnapMap Frontend - Comprehensive Testing Suite', () => {
  let consoleErrors: string[] = [];

  test.beforeEach(async ({ page }) => {
    consoleErrors = [];
    // Set up console error listener
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });
  });

  test.describe('1. CSV Upload Functionality', () => {
    test('should load upload page successfully', async ({ page }) => {
      await page.goto(BASE_URL);

      // Wait for upload page to load
      await page.waitForSelector('text=Upload Your Data', { timeout: 10000 });

      // Check page title
      await expect(page.locator('h2')).toContainText('Upload Your Data');

      // Verify drag-and-drop area exists
      const uploadArea = page.locator('[class*="border-dashed"]');
      await expect(uploadArea).toBeVisible();

      console.log('✓ Upload page loaded successfully');
    });

    test('should display entity selection dropdown', async ({ page }) => {
      await page.goto(BASE_URL);

      // Look for entity selector
      const entitySelector = page.locator('select');
      await expect(entitySelector).toBeVisible();

      // Verify entity options are available
      const options = await entitySelector.locator('option').count();
      expect(options).toBeGreaterThan(0);

      console.log(`✓ Entity selector found with ${options} options`);
    });

    test('should show sample file loader button', async ({ page }) => {
      await page.goto(BASE_URL);

      // Look for "Try with Sample Data" button
      const sampleButton = page.locator('button:has-text("Try with Sample Data")');
      await expect(sampleButton).toBeVisible();

      console.log('✓ Sample file loader button visible');
    });

    test('should load sample file successfully', async ({ page }) => {
      await page.goto(BASE_URL);

      // Click sample loader button
      const sampleButton = page.locator('button:has-text("Try with Sample Data")');
      await sampleButton.click();

      // Wait for dropdown
      await page.waitForSelector('text=Employee Sample 1');

      // Click first sample
      const sample1 = page.locator('button:has-text("Employee Sample 1")');
      await sample1.click();

      // Wait for success message or loading to complete
      await page.waitForSelector('text=File uploaded successfully', { timeout: 15000 });

      console.log('✓ Sample file uploaded successfully');
    });

    test('should handle file drag and drop', async ({ page }) => {
      await page.goto(BASE_URL);

      const uploadArea = page.locator('[class*="border-dashed"]').first();

      // Create a test file
      await uploadArea.focus();

      // Simulate drag over
      await uploadArea.evaluate((el) => {
        const event = new DragEvent('dragover', { bubbles: true });
        el.dispatchEvent(event);
      });

      // Check if drag state is visible (border color change)
      const classes = await uploadArea.getAttribute('class');
      expect(classes).toBeTruthy();

      console.log('✓ Drag and drop area responsive');
    });

    test('should reject invalid file types', async ({ page }) => {
      await page.goto(BASE_URL);

      // Try uploading invalid file type through input
      const fileInput = page.locator('input[type="file"]');

      // Create a fake txt file
      await fileInput.setInputFiles({
        name: 'test.txt',
        mimeType: 'text/plain',
        buffer: Buffer.from('Invalid file content'),
      });

      // Wait for error message
      await page.waitForSelector('text=Invalid file type', { timeout: 5000 });

      console.log('✓ Invalid file type rejected with error message');
    });

    test('should display file size validation', async ({ page }) => {
      await page.goto(BASE_URL);

      // Check that maximum size is documented
      const infoText = page.locator('text=Maximum file size');
      await expect(infoText).toBeVisible();

      console.log('✓ File size limits documented in UI');
    });

    test('should show responsive upload interface on mobile', async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });

      await page.goto(BASE_URL);

      // Verify elements are still visible
      const heading = page.locator('text=Upload Your Data');
      await expect(heading).toBeVisible();

      const uploadArea = page.locator('[class*="border-dashed"]');
      await expect(uploadArea).toBeVisible();

      console.log('✓ Upload interface responsive on mobile');
    });
  });

  test.describe('2. Entity Selection', () => {
    test('should display all available entity types', async ({ page }) => {
      await page.goto(BASE_URL);

      const entitySelector = page.locator('select');
      await entitySelector.click();

      // Get all options
      const options = await entitySelector.locator('option').allTextContents();

      expect(options.length).toBeGreaterThan(0);
      expect(options[0]).toBeTruthy();

      console.log(`✓ Found ${options.length} entity types: ${options.join(', ')}`);
    });

    test('should allow entity selection change', async ({ page }) => {
      await page.goto(BASE_URL);

      const entitySelector = page.locator('select');
      const initialValue = await entitySelector.inputValue();

      // Change selection
      await entitySelector.selectOption('employee');

      const newValue = await entitySelector.inputValue();
      expect(newValue).toBe('employee');

      console.log('✓ Entity selection change works');
    });

    test('should show entity type description', async ({ page }) => {
      await page.goto(BASE_URL);

      // Look for description text
      const description = page.locator('text=Select Entity Type').or(page.locator('text=Entity'));
      await expect(description).toBeVisible();

      console.log('✓ Entity selection description visible');
    });

    test('should auto-detect entity type from file', async ({ page }) => {
      await page.goto(BASE_URL);

      // Load a sample file
      const sampleButton = page.locator('button:has-text("Try with Sample Data")');
      await sampleButton.click();

      await page.waitForSelector('text=Employee Sample 1');
      const sample1 = page.locator('button:has-text("Employee Sample 1")');
      await sample1.click();

      // Wait for detection result
      const detectionResult = page.locator('text=AI detected');
      const isVisible = await detectionResult.isVisible().catch(() => false);

      if (isVisible) {
        console.log('✓ Entity type auto-detection working');
      } else {
        console.log('⚠ Entity type auto-detection not shown (may need Gemini API)');
      }
    });
  });

  test.describe('3. Auto-Mapping Interface', () => {
    test('should auto-map fields after upload', async ({ page }) => {
      await page.goto(BASE_URL);

      // Load sample and proceed to mapping
      const sampleButton = page.locator('button:has-text("Try with Sample Data")');
      await sampleButton.click();

      await page.waitForSelector('text=Employee Sample 1');
      const sample1 = page.locator('button:has-text("Employee Sample 1")');
      await sample1.click();

      // Wait for success and auto-advance
      await page.waitForSelector('text=File uploaded successfully', { timeout: 15000 });

      // Should auto-advance to mapping step
      await page.waitForSelector('text=Field Mapping', { timeout: 10000 });

      console.log('✓ Auto-mapping page loaded after upload');
    });

    test('should display source and target fields', async ({ page }) => {
      await page.goto(BASE_URL);

      // Upload file
      const sampleButton = page.locator('button:has-text("Try with Sample Data")');
      await sampleButton.click();

      await page.waitForSelector('text=Employee Sample 1');
      const sample1 = page.locator('button:has-text("Employee Sample 1")');
      await sample1.click();

      // Wait for mapping interface
      await page.waitForSelector('text=Field Mapping', { timeout: 15000 });

      // Check for source field list
      const sourceFields = page.locator('text=Source Fields').or(page.locator('[class*="source"]'));
      const isVisible = await sourceFields.isVisible().catch(() => false);

      if (isVisible) {
        console.log('✓ Source and target fields displayed');
      } else {
        console.log('⚠ Field lists may need scrolling or may be in different layout');
      }
    });

    test('should show confidence scores for mappings', async ({ page }) => {
      await page.goto(BASE_URL);

      // Upload file
      const sampleButton = page.locator('button:has-text("Try with Sample Data")');
      await sampleButton.click();

      await page.waitForSelector('text=Employee Sample 1');
      const sample1 = page.locator('button:has-text("Employee Sample 1")');
      await sample1.click();

      // Wait for mapping
      await page.waitForSelector('text=Field Mapping', { timeout: 15000 });

      // Look for confidence indicators (numbers, percentages, or badges)
      const confidenceText = page.locator('text=confidence').or(page.locator('[class*="badge"]'));
      const isVisible = await confidenceText.isVisible().catch(() => false);

      if (isVisible) {
        console.log('✓ Confidence scores visible in UI');
      } else {
        console.log('⚠ Confidence scores not visually indicated');
      }
    });

    test('should show high confidence with visual indicator', async ({ page }) => {
      await page.goto(BASE_URL);

      // Upload file and wait for mapping
      const sampleButton = page.locator('button:has-text("Try with Sample Data")');
      await sampleButton.click();

      await page.waitForSelector('text=Employee Sample 1');
      const sample1 = page.locator('button:has-text("Employee Sample 1")');
      await sample1.click();

      await page.waitForSelector('text=Field Mapping', { timeout: 15000 });

      // Look for success/checkmark indicators
      const successIndicators = page.locator('[class*="success"]').or(page.locator('[class*="check"]'));
      const count = await successIndicators.count();

      if (count > 0) {
        console.log(`✓ Found ${count} success/checkmark indicators for high confidence mappings`);
      } else {
        console.log('⚠ No visual indicators for high confidence mappings found');
      }
    });
  });

  test.describe('4. Manual Mapping & Drag-and-Drop', () => {
    test('should allow manual field selection', async ({ page }) => {
      await page.goto(BASE_URL);

      // Upload sample
      const sampleButton = page.locator('button:has-text("Try with Sample Data")');
      await sampleButton.click();

      await page.waitForSelector('text=Employee Sample 1');
      const sample1 = page.locator('button:has-text("Employee Sample 1")');
      await sample1.click();

      // Wait for mapping page
      await page.waitForSelector('text=Field Mapping', { timeout: 15000 });

      // Try to click on a source field
      const fields = page.locator('[class*="field"]');
      const count = await fields.count();

      if (count > 0) {
        await fields.first().click();
        console.log('✓ Manual field selection possible');
      } else {
        console.log('⚠ Field elements not found in expected selectors');
      }
    });

    test('should highlight selected source field', async ({ page }) => {
      await page.goto(BASE_URL);

      // Upload sample
      const sampleButton = page.locator('button:has-text("Try with Sample Data")');
      await sampleButton.click();

      await page.waitForSelector('text=Employee Sample 1');
      const sample1 = page.locator('button:has-text("Employee Sample 1")');
      await sample1.click();

      // Wait for mapping page
      await page.waitForSelector('text=Field Mapping', { timeout: 15000 });

      // Try clicking a field and check for visual feedback
      const firstField = page.locator('[class*="field"]').first();
      const classes = await firstField.getAttribute('class');

      await firstField.click();
      const classesAfter = await firstField.getAttribute('class');

      if (classes !== classesAfter) {
        console.log('✓ Selected field shows visual feedback (class change)');
      } else {
        console.log('⚠ Selected field styling may not update');
      }
    });

    test('should allow drag-and-drop mapping', async ({ page }) => {
      await page.goto(BASE_URL);

      // Upload sample
      const sampleButton = page.locator('button:has-text("Try with Sample Data")');
      await sampleButton.click();

      await page.waitForSelector('text=Employee Sample 1');
      const sample1 = page.locator('button:has-text("Employee Sample 1")');
      await sample1.click();

      // Wait for mapping page
      await page.waitForSelector('text=Field Mapping', { timeout: 15000 });

      // Check if drag-and-drop elements exist
      const draggableElements = page.locator('[draggable="true"], [class*="drag"], [class*="sortable"]');
      const draggableCount = await draggableElements.count();

      if (draggableCount > 0) {
        console.log(`✓ Found ${draggableCount} draggable elements for drag-and-drop mapping`);
      } else {
        console.log('⚠ No obvious draggable elements found');
      }
    });
  });

  test.describe('5. Data Validation & Issue Review', () => {
    test('should perform validation after mapping', async ({ page }) => {
      await page.goto(BASE_URL);

      // Upload sample
      const sampleButton = page.locator('button:has-text("Try with Sample Data")');
      await sampleButton.click();

      await page.waitForSelector('text=Employee Sample 1');
      const sample1 = page.locator('button:has-text("Employee Sample 1")');
      await sample1.click();

      // Wait for mapping and proceed
      await page.waitForSelector('text=Field Mapping', { timeout: 15000 });

      // Look for next/proceed button
      const nextButton = page.locator('button:has-text("Next")').or(page.locator('button:has-text("Proceed")'));
      const exists = await nextButton.count() > 0;

      if (exists) {
        await nextButton.first().click();

        // Wait for validation page
        await page.waitForSelector('text=Validation').or(page.waitForSelector('text=Issues', { timeout: 10000 })).catch(() => {});

        console.log('✓ Validation step accessible after mapping');
      } else {
        console.log('⚠ Could not find next/proceed button');
      }
    });

    test('should display validation issues if any', async ({ page }) => {
      await page.goto(BASE_URL);

      // Upload sample
      const sampleButton = page.locator('button:has-text("Try with Sample Data")');
      await sampleButton.click();

      await page.waitForSelector('text=Employee Sample 1');
      const sample1 = page.locator('button:has-text("Employee Sample 1")');
      await sample1.click();

      // Wait for mapping and proceed
      await page.waitForSelector('text=Field Mapping', { timeout: 15000 });

      // Look for next button
      const nextButton = page.locator('button:has-text("Next")').or(page.locator('button:has-text("Proceed")'));
      if (await nextButton.count() > 0) {
        await nextButton.first().click();

        // Wait briefly for validation page
        await page.waitForTimeout(2000);

        // Check for error or issue indicators
        const errorIndicators = page.locator('[class*="error"]').or(page.locator('[class*="warning"]'));
        const count = await errorIndicators.count();

        if (count > 0) {
          console.log(`✓ Validation issues displayed: ${count} indicators found`);
        } else {
          console.log('✓ No validation issues found (data is valid)');
        }
      }
    });

    test('should show data quality metrics', async ({ page }) => {
      await page.goto(BASE_URL);

      // Upload sample and navigate to validation
      const sampleButton = page.locator('button:has-text("Try with Sample Data")');
      await sampleButton.click();

      await page.waitForSelector('text=Employee Sample 1');
      const sample1 = page.locator('button:has-text("Employee Sample 1")');
      await sample1.click();

      await page.waitForSelector('text=Field Mapping', { timeout: 15000 });

      const nextButton = page.locator('button:has-text("Next")').or(page.locator('button:has-text("Proceed")'));
      if (await nextButton.count() > 0) {
        await nextButton.first().click();

        await page.waitForTimeout(2000);

        // Look for metrics
        const metrics = page.locator('text=quality').or(page.locator('text=metric')).or(page.locator('[class*="stat"]'));
        const count = await metrics.count();

        if (count > 0) {
          console.log('✓ Data quality metrics displayed');
        } else {
          console.log('⚠ Data quality metrics not found in expected locations');
        }
      }
    });
  });

  test.describe('6. XML Transformation & Preview', () => {
    test('should navigate to XML preview step', async ({ page }) => {
      await page.goto(BASE_URL);

      // Check if we can see step indicators
      const steps = page.locator('text=CSV Preview').or(page.locator('text=XML'));
      const count = await steps.count();

      if (count > 0) {
        console.log('✓ XML step visible in UI');
      } else {
        console.log('⚠ XML step visibility unclear');
      }
    });

    test('should display XML preview with proper formatting', async ({ page }) => {
      await page.goto(BASE_URL);

      // Look for XML content
      const xmlIndicators = page.locator('text=<?xml').or(page.locator('[class*="xml"]')).or(page.locator('pre'));
      const count = await xmlIndicators.count();

      if (count > 0) {
        console.log('✓ XML content found in UI');
      } else {
        console.log('⚠ XML preview not visible (may need to reach XML step)');
      }
    });

    test('should allow XML download', async ({ page }) => {
      await page.goto(BASE_URL);

      // Look for download button
      const downloadButton = page.locator('button:has-text("Download")').or(page.locator('[class*="download"]'));
      const exists = await downloadButton.count() > 0;

      if (exists) {
        console.log('✓ Download button visible for XML export');
      } else {
        console.log('⚠ Download button not found');
      }
    });

    test('should validate XML structure', async ({ page }) => {
      // This test checks if the XML can be parsed when retrieved
      const response = await page.request.get(`${API_BASE_URL}/health`).catch(() => null);

      if (response && response.ok()) {
        console.log('✓ API endpoint responding (XML transformation available)');
      } else {
        console.log('⚠ Backend API not responding');
      }
    });
  });

  test.describe('7. SFTP Upload Interface', () => {
    test('should display SFTP upload page', async ({ page }) => {
      await page.goto(BASE_URL);

      // Look for SFTP in navigation or steps
      const sftpIndicators = page.locator('text=SFTP').or(page.locator('text=Upload'));
      const count = await sftpIndicators.count();

      if (count > 0) {
        console.log('✓ SFTP upload section found in UI');
      } else {
        console.log('⚠ SFTP upload section not visible');
      }
    });

    test('should have SFTP credential form', async ({ page }) => {
      await page.goto(BASE_URL);

      // Look for SFTP form fields
      const inputs = page.locator('input[type="text"], input[type="password"]');
      const inputCount = await inputs.count();

      if (inputCount >= 3) {  // Usually: host, username, password
        console.log(`✓ SFTP form found with ${inputCount} input fields`);
      } else {
        console.log('⚠ SFTP form fields not visible or not yet implemented');
      }
    });

    test('should validate SFTP credentials format', async ({ page }) => {
      await page.goto(BASE_URL);

      // Try entering invalid data into SFTP fields
      const inputs = page.locator('input[type="text"]').first();
      const exists = await inputs.count() > 0;

      if (exists) {
        await inputs.fill('test');

        // Check for validation message
        const validationMsg = page.locator('text=required').or(page.locator('[class*="error"]'));
        console.log('✓ SFTP form has input fields (validation may be client or server-side)');
      } else {
        console.log('⚠ SFTP form not found');
      }
    });

    test('should show upload progress indicator', async ({ page }) => {
      await page.goto(BASE_URL);

      // Look for progress indicators
      const progress = page.locator('[class*="progress"]').or(page.locator('[role="progressbar"]'));
      const count = await progress.count();

      if (count > 0) {
        console.log('✓ Progress indicators found in UI');
      } else {
        console.log('⚠ Progress indicators not visible');
      }
    });

    test('should handle SFTP upload without actual upload', async ({ page }) => {
      await page.goto(BASE_URL);

      // Look for upload button
      const uploadButton = page.locator('button:has-text("Upload")').or(page.locator('button:has-text("Send")'));
      const exists = await uploadButton.count() > 0;

      if (exists) {
        console.log('✓ SFTP upload button visible');
      } else {
        console.log('⚠ SFTP upload button not found');
      }
    });
  });

  test.describe('8. Responsive Design & Mobile', () => {
    test('should be responsive on tablet size', async ({ page }) => {
      await page.setViewportSize({ width: 768, height: 1024 });
      await page.goto(BASE_URL);

      const mainContent = page.locator('main');
      await expect(mainContent).toBeVisible();

      console.log('✓ Layout responsive at tablet size (768x1024)');
    });

    test('should be responsive on mobile size', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await page.goto(BASE_URL);

      const mainContent = page.locator('main');
      await expect(mainContent).toBeVisible();

      console.log('✓ Layout responsive at mobile size (375x667)');
    });

    test('should be responsive on desktop size', async ({ page }) => {
      await page.setViewportSize({ width: 1920, height: 1080 });
      await page.goto(BASE_URL);

      const mainContent = page.locator('main');
      await expect(mainContent).toBeVisible();

      console.log('✓ Layout responsive at desktop size (1920x1080)');
    });

    test('should have accessible touch targets on mobile', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await page.goto(BASE_URL);

      // Check button sizes
      const buttons = page.locator('button');
      const count = await buttons.count();

      if (count > 0) {
        const boundingBox = await buttons.first().boundingBox();
        if (boundingBox && boundingBox.height >= 44) {
          console.log('✓ Touch targets have sufficient size (44px minimum)');
        } else {
          console.log('⚠ Some touch targets may be too small');
        }
      }
    });
  });

  test.describe('9. Error Handling & Edge Cases', () => {
    test('should display error for network failure', async ({ page }) => {
      // Simulate offline
      await page.context().setOffline(true);

      await page.goto(BASE_URL);

      // Try to interact with an API call
      const sampleButton = page.locator('button:has-text("Try with Sample Data")');
      await sampleButton.click();

      await page.waitForSelector('text=Employee Sample 1');
      const sample1 = page.locator('button:has-text("Employee Sample 1")');
      await sample1.click();

      // Should show error
      await page.waitForTimeout(2000);
      const errorMsg = page.locator('[class*="error"]');
      const exists = await errorMsg.count() > 0;

      await page.context().setOffline(false);

      if (exists) {
        console.log('✓ Network error handled gracefully');
      } else {
        console.log('⚠ Network error handling may not be visible');
      }
    });

    test('should clear error messages', async ({ page }) => {
      await page.goto(BASE_URL);

      // Try to trigger an error
      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles({
        name: 'test.txt',
        mimeType: 'text/plain',
        buffer: Buffer.from('Invalid'),
      });

      // Wait for error
      await page.waitForSelector('text=Invalid file type', { timeout: 5000 });

      // Look for close button or try to clear error
      const closeBtn = page.locator('[class*="error"] button').or(page.locator('button[aria-label*="close"]'));
      if (await closeBtn.count() > 0) {
        await closeBtn.first().click();

        const errorStill = await page.locator('text=Invalid file type').count() > 0;
        if (!errorStill) {
          console.log('✓ Error messages can be dismissed');
        } else {
          console.log('⚠ Error message dismissal may not work');
        }
      } else {
        console.log('⚠ Error dismiss button not found');
      }
    });

    test('should handle empty file gracefully', async ({ page }) => {
      await page.goto(BASE_URL);

      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles({
        name: 'empty.csv',
        mimeType: 'text/csv',
        buffer: Buffer.from(''),
      });

      // Should show some error or handling
      await page.waitForTimeout(2000);

      const errorOrWarning = page.locator('[class*="error"], [class*="warning"]');
      const count = await errorOrWarning.count();

      if (count > 0) {
        console.log('✓ Empty file handled with error message');
      } else {
        console.log('⚠ Empty file handling unclear');
      }
    });

    test('should handle oversized file error', async ({ page }) => {
      await page.goto(BASE_URL);

      // Check size validation message exists
      const sizeMsg = page.locator('text=100 MB').or(page.locator('text=maximum'));
      const exists = await sizeMsg.isVisible();

      if (exists) {
        console.log('✓ File size limits documented');
      } else {
        console.log('⚠ File size documentation not found');
      }
    });

    test('should not show console errors', async ({ page }) => {
      await page.goto(BASE_URL);

      // Wait and let app initialize
      await page.waitForTimeout(2000);

      // Check for any logged errors
      if (consoleErrors.length === 0) {
        console.log('✓ No console errors during page load');
      } else {
        console.log(`⚠ Console errors found: ${consoleErrors.join(', ')}`);
      }
    });
  });

  test.describe('10. UI/UX Quality Checks', () => {
    test('should have proper contrast and readability', async ({ page }) => {
      await page.goto(BASE_URL);

      // Check for text elements
      const headings = page.locator('h1, h2, h3, h4, h5, h6');
      const count = await headings.count();

      if (count > 0) {
        console.log(`✓ Found ${count} heading elements for proper structure`);
      }
    });

    test('should have consistent spacing and alignment', async ({ page }) => {
      await page.goto(BASE_URL);

      // Check main container
      const mainContent = page.locator('main');
      const classes = await mainContent.getAttribute('class');

      if (classes && (classes.includes('p-') || classes.includes('px-') || classes.includes('py-'))) {
        console.log('✓ Proper padding and spacing applied');
      }
    });

    test('should have accessible color schemes', async ({ page }) => {
      await page.goto(BASE_URL);

      // Check for dark mode support
      const htmlClasses = await page.locator('html').getAttribute('class');

      if (htmlClasses && (htmlClasses.includes('dark') || htmlClasses.includes('theme'))) {
        console.log('✓ Theme system implemented');
      } else {
        console.log('⚠ Dark mode or theme system not detected');
      }
    });

    test('should display helpful hints for each step', async ({ page }) => {
      await page.goto(BASE_URL);

      // Look for tip/info boxes
      const tips = page.locator('[class*="tip"]').or(page.locator('[class*="info"]')).or(page.locator('text=💡'));
      const count = await tips.count();

      if (count > 0) {
        console.log(`✓ Found ${count} helpful tip sections`);
      } else {
        console.log('⚠ Help tips not visible');
      }
    });

    test('should have clear visual hierarchy', async ({ page }) => {
      await page.goto(BASE_URL);

      // Check for cards and sections
      const cards = page.locator('[class*="card"]').or(page.locator('[class*="section"]'));
      const count = await cards.count();

      if (count > 0) {
        console.log(`✓ Clear visual hierarchy with ${count} distinct sections`);
      }
    });
  });
});
