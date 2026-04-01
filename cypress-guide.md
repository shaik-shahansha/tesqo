# Cypress — Open Source Testing Framework Guide

> **Latest version:** v15.13.0 (April 2026) | **License:** MIT (fully open source) | **GitHub:** 49.6k ⭐ | 1.5M+ dependents

---

## Is Cypress Open Source?

**Yes — but partially.** Here's the split:

| Product | Cost | What it does |
|---|---|---|
| **Cypress App** | ✅ FREE / Open Source (MIT) | Write, record, run, debug tests locally |
| **Cypress Cloud** | 💰 Paid SaaS | CI recording, test replay, parallelization, analytics |
| **UI Coverage** | 💰 Premium | Visual test coverage across pages/components |
| **Cypress Accessibility** | 💰 Premium | Automated a11y checks |

**For local testing, unit tests, regression, and automation — the free Cypress App covers everything you need.** Cypress Cloud is only needed if you want hosted CI dashboards.

---

## Why Cypress is Different (and Easy)

- **Runs inside the browser** — not via WebDriver like Selenium. Faster, more reliable.
- **Auto-waiting** — no `sleep()` or manual waits. Cypress waits automatically for elements.
- **Time-travel debugging** — hover over any command in the log to see a DOM snapshot at that moment.
- **Built-in recording** — Cypress Studio lets you click through your app and generates test code.
- **JavaScript/TypeScript only** — NOT Python. This is the key trade-off vs Playwright.
- **Real browser** — tests run in Chrome, Firefox, Edge, Electron, WebKit.

---

## Installation (Node.js required)

```bash
# Prerequisites: Node.js 18+ installed
npm install cypress --save-dev

# Open Cypress interactive UI
npx cypress open

# Run all tests headlessly (CI mode)
npx cypress run

# Run a specific file
npx cypress run --spec "cypress/e2e/login.cy.js"

# Run with a specific browser
npx cypress run --browser firefox
```

---

## Project Structure (auto-generated)

```
my-project/
├── cypress/
│   ├── e2e/                    ← your test files go here
│   │   ├── login.cy.js
│   │   ├── search.cy.js
│   │   └── table_check.cy.js
│   ├── fixtures/               ← static test data (JSON)
│   │   └── users.json
│   ├── support/
│   │   ├── commands.js         ← custom reusable commands
│   │   └── e2e.js              ← global setup/hooks
│   └── screenshots/            ← auto-captured on failure
├── cypress.config.js           ← main config (env vars, base URL, etc.)
└── package.json
```

---

## cypress.config.js — Central Config + Env Variables

```js
// cypress.config.js
const { defineConfig } = require('cypress')

module.exports = defineConfig({
  e2e: {
    baseUrl: 'https://myapp.com',       // set once, use cy.visit('/login')
    viewportWidth: 1280,
    viewportHeight: 720,
    screenshotOnRunFailure: true,       // auto screenshot on failure ✅
    video: true,                        // record video of runs ✅
    setupNodeEvents(on, config) {},
  },
  env: {
    USERNAME: 'admin',                  // access via Cypress.env('USERNAME')
    PASSWORD: 'secret',
    API_URL: 'https://api.myapp.com',
  },
})
```

> **Tip for secrets:** Use `cypress.env.json` (gitignored) or OS env vars prefixed with `CYPRESS_`:
> ```bash
> CYPRESS_PASSWORD=mysecret npx cypress run
> ```

---

## Basic Test Cases

### 1. Navigate + Type + Click (Login)

```js
// cypress/e2e/login.cy.js
describe('Login', () => {
  it('logs in with valid credentials', () => {
    cy.visit('/login')                                    // navigate

    cy.get('#username').type(Cypress.env('USERNAME'))    // type
    cy.get('#password').type(Cypress.env('PASSWORD'))    // type

    cy.get('button[type="submit"]').click()              // click

    cy.url().should('include', '/dashboard')             // assert URL changed
    cy.get('.welcome-msg').should('be.visible')          // assert element visible
  })

  it('shows error on wrong password', () => {
    cy.visit('/login')
    cy.get('#username').type('admin')
    cy.get('#password').type('wrongpass')
    cy.get('button[type="submit"]').click()

    cy.get('.error-alert')
      .should('be.visible')
      .and('contain.text', 'Invalid credentials')        // assert text
  })
})
```

---

### 2. Exists / Visible / Enabled / Disabled Checks

```js
it('checks element states', () => {
  cy.visit('/form')

  cy.get('#submit-btn').should('exist')                  // exists in DOM
  cy.get('#submit-btn').should('be.visible')             // visible to user
  cy.get('#submit-btn').should('be.enabled')             // not disabled
  cy.get('#preview-btn').should('be.disabled')           // is disabled
  cy.get('.spinner').should('not.exist')                 // does NOT exist
  cy.get('#result').should('not.be.visible')             // hidden

  cy.get('#status-badge').should('have.text', 'Active')  // exact text
  cy.get('#info').should('contain', 'Welcome')           // partial text
  cy.get('#count').should('have.value', '42')            // input field value
})
```

---

### 3. Wait for Element / Page Load / Network

```js
it('waits properly', () => {
  cy.visit('/dashboard')

  // Wait for element to appear (auto-retry for up to 4s by default)
  cy.get('.data-table', { timeout: 10000 }).should('be.visible')

  // Wait for API call to finish before asserting
  cy.intercept('GET', '/api/users').as('getUsers')
  cy.visit('/users')
  cy.wait('@getUsers')                                   // wait for API
  cy.get('table tbody tr').should('have.length.gt', 0)

  // Wait for URL to change
  cy.location('pathname').should('eq', '/users')
})
```

---

### 4. Select, Checkbox, Radio, File Upload

```js
it('fills a complex form', () => {
  cy.visit('/form')

  cy.get('#country').select('India')                     // dropdown
  cy.get('#agree').check()                               // checkbox
  cy.get('input[value="monthly"]').check()               // radio button
  cy.get('#file-input').selectFile('cypress/fixtures/data.csv')  // file upload

  cy.get('input[type="range"]').invoke('val', 50).trigger('input') // slider
})
```

---

### 5. Table Row Scanning + Individual Value Check

```js
it('verifies all table rows have Active status', () => {
  cy.visit('/users')

  cy.get('table tbody tr').each(($row) => {
    cy.wrap($row).find('td:nth-child(3)').should('have.text', 'Active')
  })
})

it('finds a specific user and checks their role', () => {
  cy.visit('/users')

  cy.contains('tr', 'John Doe')                         // find row containing text
    .find('td.role')
    .should('have.text', 'Admin')
})
```

---

### 6. Table with Pagination (Next Button)

```js
it('checks all records across pages', () => {
  cy.visit('/records')

  function checkPageAndNext() {
    // Process current page rows
    cy.get('table tbody tr').each(($row) => {
      cy.wrap($row).find('.status').should('not.have.text', 'Error')
    })

    // Check if Next button exists and is enabled
    cy.get('body').then(($body) => {
      const nextBtn = $body.find('button.next-page:not([disabled])')
      if (nextBtn.length > 0) {
        cy.get('button.next-page').click()
        cy.get('table').should('be.visible')             // wait for reload
        checkPageAndNext()                               // recurse
      }
    })
  }

  checkPageAndNext()
})
```

---

### 7. Conditional Automation (Act on Web Data)

```js
it('activates all inactive users found in table', () => {
  cy.visit('/admin/users')

  cy.get('table tbody tr').each(($row) => {
    const statusText = $row.find('.status').text().trim()

    if (statusText === 'Inactive') {
      cy.wrap($row).find('button.activate').click()
      cy.get('.toast-success').should('be.visible')     // confirm action
      cy.get('.toast-success').should('not.exist')       // wait for it to disappear
    }
  })
})
```

---

### 8. Data-Driven Tests from JSON Fixture

```js
// cypress/fixtures/users.json
// [
//   { "username": "alice", "password": "pass1", "role": "Admin" },
//   { "username": "bob",   "password": "pass2", "role": "User" }
// ]

describe('Login for multiple users', () => {
  beforeEach(() => {
    cy.fixture('users').as('users')                      // load fixture
  })

  it('each user sees correct role after login', function () {
    this.users.forEach((user) => {
      cy.visit('/login')
      cy.get('#username').clear().type(user.username)
      cy.get('#password').clear().type(user.password)
      cy.get('button[type="submit"]').click()
      cy.get('.user-role').should('have.text', user.role)
      cy.get('#logout').click()
    })
  })
})
```

---

### 9. Custom Reusable Commands (like helper functions)

```js
// cypress/support/commands.js
Cypress.Commands.add('login', (username, password) => {
  cy.visit('/login')
  cy.get('#username').type(username)
  cy.get('#password').type(password)
  cy.get('button[type="submit"]').click()
  cy.url().should('include', '/dashboard')
})

// Use it in any test:
// cy.login(Cypress.env('USERNAME'), Cypress.env('PASSWORD'))
```

---

### 10. Screenshots + Video (Built-in)

```js
// Screenshots on failure: automatic (screenshotOnRunFailure: true in config)

// Manual screenshot anywhere:
it('captures screenshot at key moment', () => {
  cy.visit('/report')
  cy.get('.chart').should('be.visible')
  cy.screenshot('report-chart')                         // saves to cypress/screenshots/
})

// Video: automatically recorded for every `cypress run` (headless)
// Saved to: cypress/videos/
```

---

## Recording Tests (Cypress Studio)

1. Run `npx cypress open`
2. Open any test file or create a blank one
3. Click **"Studio"** or use `cy.studio()` in a test
4. Interact with your app — Cypress records every click, type, assertion
5. Click **Save** — code is written directly into your test file
6. Edit values to use `Cypress.env()` variables instead of hardcoded strings

---

## Batch Run Scripts (package.json)

```json
{
  "scripts": {
    "test":         "cypress run",
    "test:headed":  "cypress run --headed",
    "test:open":    "cypress open",
    "test:smoke":   "cypress run --spec 'cypress/e2e/smoke/**'",
    "test:login":   "cypress run --spec 'cypress/e2e/login.cy.js'",
    "test:firefox": "cypress run --browser firefox",
    "test:chrome":  "cypress run --browser chrome"
  }
}
```

Run with: `npm run test:smoke`

---

## What Cypress CANNOT Do (trade-offs)

| Limitation | Workaround |
|---|---|
| **JavaScript/TypeScript only** (no Python) | Use Playwright if Python required |
| **No multi-tab support** (natively) | Use `cy.origin()` for cross-origin, workaround for tabs |
| **No Excel data-driven input** natively | Use JSON fixtures or read CSV via `cy.task()` + Node.js |
| **Safari not fully supported** | WebKit via experimental flag |
| **Cannot control OS-level dialogs** | Stub `window.alert`, `window.confirm` |

---

## Cypress vs Playwright (Quick Comparison)

| Feature | Cypress (free) | Playwright (free) |
|---|---|---|
| Language | JS/TS only | Python, JS, Java, C# |
| Recording/Codegen | ✅ Cypress Studio | ✅ `playwright codegen` |
| Auto-wait | ✅ built-in | ✅ built-in |
| Excel data input | ❌ needs workaround | ✅ easy with openpyxl |
| Multi-browser | ✅ Chrome/FF/Edge/Electron | ✅ Chrome/FF/WebKit |
| Screenshots on fail | ✅ automatic | ✅ via conftest |
| Time-travel debug | ✅ excellent | ❌ not native |
| Python support | ❌ | ✅ |
| CI recording (free) | ❌ Cypress Cloud = paid | ✅ allure/html free |
| Ease for JS devs | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Ease for non-JS devs | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ (Python) |

---

## Verdict

**Cypress is excellent if your team uses JavaScript/TypeScript.** Its Studio recording, time-travel debugging, and automatic waiting make it one of the easiest tools to get started with. For Python-based teams, or if you need Excel-driven data and richer free reporting, **Playwright + pytest is a better fit.**
