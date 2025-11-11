# How to Run the SnapMap Frontend Tests

This document explains how to execute the comprehensive test suite created for SnapMap frontend.

---

## Prerequisites

### System Requirements
- Node.js 16+ (for npm)
- npm or yarn
- 2GB RAM minimum
- 500MB disk space for dependencies

### Services Running
Before running tests, ensure:
1. **Backend API:** Running on `http://localhost:8000`
2. **Frontend App:** Available on `http://localhost:5173` (test will start it)
3. **Vector DB:** Already built with `python build_vector_db.py`

### Quick Service Check
```bash
# Check backend
curl http://localhost:8000/api/health

# Check if frontend repo has sample files
ls frontend/public/samples/

# Both should return successful responses
```

---

## Installation

### Step 1: Install Playwright
```bash
cd frontend

# Install Playwright and dependencies
npm install -D @playwright/test

# This will take 2-5 minutes
```

### Step 2: Verify Installation
```bash
# Check Playwright installed correctly
npx playwright --version
# Should output: Version X.X.X (e.g., 1.40.0)
```

---

## Running Tests

### Option A: Basic Test Run (Recommended for First Time)
```bash
cd frontend

# Run all tests with default settings
npx playwright test tests/e2e/comprehensive-frontend-tests.spec.ts
```

**Expected Output:**
```
Running 60 tests...
✓ Upload page loads successfully
✓ Display entity selection dropdown
✓ Show sample file loader button
...
60 passed, 0 failed (3-5 minutes)

View full report: npx playwright show-report
```

---

### Option B: Run Specific Feature Tests

**CSV Upload Tests Only:**
```bash
npx playwright test --grep "CSV Upload"
```

**Entity Selection Tests:**
```bash
npx playwright test --grep "Entity Selection"
```

**Auto-Mapping Tests:**
```bash
npx playwright test --grep "Auto-Mapping"
```

**Manual Mapping Tests:**
```bash
npx playwright test --grep "Manual Mapping"
```

**Validation Tests:**
```bash
npx playwright test --grep "Validation"
```

**XML Tests:**
```bash
npx playwright test --grep "XML"
```

**SFTP Tests:**
```bash
npx playwright test --grep "SFTP"
```

**Responsive Design Tests:**
```bash
npx playwright test --grep "Responsive"
```

**Error Handling Tests:**
```bash
npx playwright test --grep "Error"
```

**UI/UX Tests:**
```bash
npx playwright test --grep "UI/UX"
```

---

### Option C: Watch Mode (See Tests Running in Browser)

```bash
# Run tests in headed mode (browser visible)
npx playwright test --headed

# This opens a browser window showing each test step
# Slower but helps understand what's being tested
```

**Tips:**
- Watch the browser as tests run
- Pause on failures to inspect
- Great for visual verification
- Takes longer but more informative

---

### Option D: Debug Mode (Interactive Debugging)

```bash
# Run tests with Playwright Inspector
npx playwright test --debug

# This pauses on each step for manual inspection
# Inspector window opens with step-by-step controls
```

**Inspector Features:**
- Step through tests one action at a time
- Inspect elements in the DOM
- View network requests
- Check console logs
- Modify selectors and re-run

**Great for:**
- Understanding why a test failed
- Debugging selector issues
- Learning how tests work
- Troubleshooting element visibility

---

### Option E: Single Browser Only

```bash
# Test only in Chromium (faster)
npx playwright test --project=chromium

# Test only in Firefox (for comparison)
npx playwright test --project=firefox
```

---

### Option F: Run with Specific Configuration

```bash
# Force parallelization (faster on multi-core)
npx playwright test --workers=4

# Run serially (slower but isolates issues)
npx playwright test --workers=1

# Set timeout for slow connections
npx playwright test --timeout=120000

# Run only failed tests from last run
npx playwright test --last-failed
```

---

## Understanding Test Results

### Success Output
```
✓ Feature Test 1
✓ Feature Test 2
✓ Feature Test 3

60 passed in 3 minutes
```

### Failure Output
```
✗ Feature Test that Failed
  Error: timeout 5000ms exceeded

Details:
  Test failed at step: "await page.locator('...').click()"
  Expected element not found
  Selector: button:has-text("Upload")
```

### Skipped Tests
```
⊗ Feature Test Skipped
  Skipped: Optional feature not implemented
```

---

## Viewing Test Results

### Interactive HTML Report
```bash
# Generate and open HTML report of last run
npx playwright show-report

# Opens browser with:
# - Test summary
# - Individual test details
# - Screenshots of failures
# - Videos of failed tests
# - Execution timeline
```

### View in Different Format
```bash
# List format (console output)
npx playwright test --reporter=list

# JSON format (for CI/CD integration)
npx playwright test --reporter=json

# HTML (default)
npx playwright test --reporter=html
```

---

## Troubleshooting

### Issue: "Port 5173 already in use"
```bash
# Solution 1: Kill existing process
# On Windows:
netstat -ano | findstr :5173
taskkill /PID <PID> /F

# Solution 2: Use different port
npm run dev -- --port 5174
# Update BASE_URL in test file
```

### Issue: "Cannot find element"
```bash
# This means UI changed or selector is wrong
# Solutions:
1. Run with --debug to inspect element
2. Check if backend is running
3. Check if sample files exist
4. Verify CSS classes haven't changed
```

### Issue: "Timeout waiting for network"
```bash
# Increase timeout:
npx playwright test --timeout=60000

# Or check:
1. Is backend running?
2. Is network connection good?
3. Is backend slow?
4. Run locally vs over network?
```

### Issue: "Sample files not found"
```bash
# Verify files exist:
ls frontend/public/samples/

# Should show:
# - employee_sample_1.csv
# - employee_sample_2.csv
# - candidate_sample.csv
# - position_sample.csv
# - user_sample.csv
# - candidate_certification_sample.csv
```

### Issue: "Backend API not responding"
```bash
# Check backend is running:
curl http://localhost:8000/api/health

# If fails, start backend:
cd backend
python -m uvicorn main:app --reload --port 8000

# Check vector DB built:
ls backend/data/
# Should contain chroma/ directory
```

---

## Continuous Integration (CI/CD)

### GitHub Actions Example
```yaml
name: Frontend Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - uses: actions/setup-node@v3
        with:
          node-version: 18

      - name: Install dependencies
        run: cd frontend && npm install

      - name: Install Playwright
        run: cd frontend && npx playwright install

      - name: Start backend
        run: |
          cd backend
          pip install -r requirements.txt
          python build_vector_db.py
          python -m uvicorn main:app --port 8000 &

      - name: Run tests
        run: cd frontend && npx playwright test tests/e2e/comprehensive-frontend-tests.spec.ts

      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: frontend/playwright-report/
```

---

## Performance Testing

### Measure Test Duration
```bash
# Run and time
time npx playwright test

# Output:
# real    3m 45s
# user    2m 30s
# sys     0m 45s
```

### Profile Tests
```bash
# Generate Chrome DevTools timeline
npx playwright test --reporter=json > results.json

# Use Chrome DevTools to analyze
```

---

## Advanced Options

### Run Tests on Multiple Browsers (Default)
```bash
npx playwright test
# Runs on: Chromium, Firefox, WebKit (if available)
```

### Update Snapshots (if UI changed intentionally)
```bash
npx playwright test --update-snapshots
```

### Keep Browser Open After Test (Good for Debugging)
Edit `playwright.config.ts`:
```typescript
use: {
  // ...
  headless: false,
  slowMo: 1000, // Slow down by 1000ms
}
```

---

## Test Maintenance

### When Tests Fail
1. Review the failure message
2. Check what changed in UI
3. Run with `--headed` to see the issue
4. Update selectors or expectations
5. Commit changes with explanation

### When Adding New Tests
1. Copy structure from existing test
2. Update selectors for new elements
3. Set appropriate timeout values
4. Run test before committing

### When UI Changes
1. Run tests to identify what broke
2. Update selectors in test file
3. Verify fix with `--headed` mode
4. Re-run full test suite

---

## Expected Results Summary

### Happy Path (All Tests Pass)
```
CSV Upload: 7 tests ✓
Entity Selection: 4 tests ✓
Auto-Mapping: 5 tests ✓
Manual Mapping: 4 tests ✓
Validation: 3 tests ✓
XML: 4 tests ✓
SFTP: 5 tests ✓
Responsive: 5 tests ✓
Error Handling: 5 tests ✓
UI/UX: 5 tests ✓

Total: 60 tests passed, 0 failed
Duration: 3-5 minutes
Status: READY FOR PRODUCTION
```

### With Issues (Some Tests Fail)
1. Review failures in report
2. Check error messages
3. Investigate root cause
4. Fix code or tests
5. Re-run to verify

---

## Getting Test Results

### Test Report Location
```
frontend/playwright-report/
├── index.html (Open in browser)
├── test-results.json
├── blob_<number>.txt (screenshots)
└── video-<number>.webm (failed test videos)
```

### Download Report
```bash
# After tests complete, report is in:
ls frontend/playwright-report/

# Share with team:
# 1. Open index.html in browser
# 2. Export as PDF if needed
# 3. Share screenshots/videos of failures
```

---

## Best Practices

### Before Running Tests
- [ ] Backend is running and healthy
- [ ] Vector DB has been built
- [ ] Sample files are in place
- [ ] Port 5173 is available
- [ ] No other instances running

### While Running Tests
- [ ] Monitor console for errors
- [ ] Note any timeouts or flakiness
- [ ] Check network conditions
- [ ] Keep system responsive

### After Running Tests
- [ ] Review results report
- [ ] Document any failures
- [ ] File issues for problems
- [ ] Update code/tests as needed

---

## Performance Benchmarks

### Typical Run Times
- All 60 tests: 3-5 minutes
- Single test: 10-30 seconds
- CSV Upload tests (7): 1-2 minutes
- With debug mode: 5-10 minutes

### Factors Affecting Speed
- Backend response time (+30% if slow)
- Network latency (+20% if remote)
- System CPU load (×2 if overloaded)
- Browser startup time (first run)

---

## Test Files Reference

| File | Purpose | Location |
|------|---------|----------|
| Test Suite | 60+ automated tests | `frontend/tests/e2e/comprehensive-frontend-tests.spec.ts` |
| Config | Playwright settings | `frontend/playwright.config.ts` |
| Report | Testing findings | `FRONTEND_TESTING_REPORT.md` |
| Summary | Executive summary | `TESTING_FINDINGS_SUMMARY.md` |
| This Guide | How to run tests | `RUN_TESTS_INSTRUCTIONS.md` |

---

## Quick Reference Commands

```bash
# Install and run (first time)
cd frontend && npm install -D @playwright/test && npx playwright test tests/e2e/comprehensive-frontend-tests.spec.ts

# Run all tests
npx playwright test tests/e2e/comprehensive-frontend-tests.spec.ts

# Run with UI visible
npx playwright test --headed

# Debug mode
npx playwright test --debug

# View results
npx playwright show-report

# Run specific tests
npx playwright test --grep "CSV Upload"

# Just Chromium (faster)
npx playwright test --project=chromium

# Single worker (more stable)
npx playwright test --workers=1

# Update if UI changed
npx playwright test --update-snapshots
```

---

## Support & Issues

### Common Questions

**Q: Why did tests fail?**
A: Check the HTML report for screenshots/videos. Most failures are due to:
1. Backend not running
2. Changed CSS selectors
3. Timing issues (increase timeout)
4. Network connectivity

**Q: How do I fix a failing test?**
A: Run with `--debug` or `--headed` to see what's wrong. Update selectors/expectations and re-run.

**Q: Can I run tests on CI/CD?**
A: Yes! Use the GitHub Actions example above. Tests run in Docker on Linux.

**Q: Do tests require real SFTP server?**
A: No, tests only verify UI is present and form validates. They don't upload for real.

---

## Summary

### To Get Started
1. Install Playwright: `npm install -D @playwright/test`
2. Run tests: `npx playwright test tests/e2e/comprehensive-frontend-tests.spec.ts`
3. View results: `npx playwright show-report`

### To Understand Results
1. Read `TESTING_FINDINGS_SUMMARY.md` for overview
2. Read `FRONTEND_TESTING_REPORT.md` for details
3. Review test code to understand what's tested

### Next Steps
1. Run tests and review results
2. Address any failures
3. Plan fixes based on recommendations
4. Re-run after fixes to verify

---

**Document Version:** 1.0
**Created:** November 6, 2025
**Last Updated:** November 6, 2025
**Status:** Complete and Ready to Use

For detailed testing information, see `FRONTEND_TESTING_REPORT.md`
For executive summary, see `TESTING_FINDINGS_SUMMARY.md`
