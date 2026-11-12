# 🛒 Swag Labs — UI Test Automation

[![UI Tests](https://github.com/Geektasilla/swag-labs-playwright-pytest/actions/workflows/tests.yml/badge.svg)](https://github.com/Geektasilla/swag-labs-playwright-pytest/actions/workflows/tests.yml)
[![Allure Report](https://img.shields.io/badge/Allure-live%20report-FF6C37)](https://geektasilla.github.io/swag-labs-playwright-pytest/)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-2EAD33?logo=playwright&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?logo=pytest&logoColor=white)

End-to-end UI tests for the [Swag Labs](https://www.saucedemo.com) demo shop, written with **Python, Playwright and Pytest**.

**47 scenarios × 3 browsers** run on every push and nightly in GitHub Actions.
Results are published as an **[Allure report →](https://geektasilla.github.io/swag-labs-playwright-pytest/)**

## What is covered

| Area | Checks |
|---|---|
| **Login** | all demo accounts, locked-out user, 4 invalid-credential cases, dismissing the error, protected pages, logout |
| **Inventory** | product names & prices against the catalogue, unique images, 4 sort orders, cart badge & button state, product details page, reset app state |
| **Cart** | listed products, removing, persistence after reload, continue shopping |
| **Checkout** | full purchase, **subtotal / 8 % tax / total calculated with `Decimal`** for 1–6 products, required fields, cancel |
| **Known defects** | 9 bugs found during exploratory testing — see below |

## Bugs found 🐞

Exploratory testing of all demo accounts revealed **9 defects**, documented as formal bug reports with steps,
expected/actual result, severity and priority: **[docs/bug-reports.md](docs/bug-reports.md)**.

The most interesting one affects the regular `standard_user`: the checkout shows
`Item total: $59.980000000000004` — prices are summed as floating-point numbers and not rounded.

Each defect has a regression test marked `xfail(strict=True)`. The test asserts the *correct* behaviour, so:
- while the bug exists, it is reported as an **expected failure** (grouped as "Known application defects" in Allure);
- when the bug gets fixed, the test **unexpectedly passes and fails the build** — a reminder to close the bug report.

## Framework design

```
├── config/settings.py        # test settings (pydantic-settings, overridable via env)
├── pages/                    # Page Object Model
│   ├── components/header.py  # shared header: cart, burger menu
│   ├── base_page.py          # common base + money parsing to Decimal
│   ├── login_page.py
│   ├── inventory_page.py
│   ├── product_page.py
│   ├── cart_page.py
│   └── checkout_page.py      # info / overview / complete steps
├── tests/
│   ├── data.py               # expected catalogue, tax rate, customer data
│   ├── test_login.py
│   ├── test_inventory.py
│   ├── test_cart.py
│   ├── test_checkout.py
│   └── test_known_defects.py
├── docs/bug-reports.md
└── conftest.py               # fixtures, cookie login, screenshots on failure
```

- **Page Object Model** with a reusable header component; tests read like user stories.
- **Stable locators:** `get_by_test_id()` on the app's `data-test` attributes and role-based locators — no CSS chains.
- **Web-first assertions** (`expect(...)`) that retry automatically — no `sleep()` anywhere.
- **Fast login via session cookie:** the login form is tested once in `test_login.py`; all other tests start
  already logged in, which keeps them fast and focused on the feature under test.
- **Money as `Decimal`**, so price and tax checks are exact.
- **Parallel runs** with `pytest-xdist`, one retry in CI for network hiccups of the public site.
- **Debugging:** Playwright traces and screenshots of failed tests are kept as CI artifacts; screenshots are also attached to Allure.
- **Allure steps** on every page action, tests grouped by feature, custom categories for known defects.

## CI/CD

GitHub Actions ([`tests.yml`](.github/workflows/tests.yml)):

1. **Lint** — `ruff`
2. **Test** — Chromium, Firefox and WebKit in parallel jobs
3. **Report** — results of all browsers are merged into one Allure report and published to GitHub Pages

The suite also runs **nightly**, so regressions of the live site are noticed even without code changes.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install

pytest                              # all tests, Chromium, headless
pytest -m smoke                     # critical path only
pytest --browser firefox -n auto    # another browser, in parallel
pytest --headed --slowmo 500        # watch the browser

pytest --alluredir=allure-results && allure serve allure-results   # Allure report (needs Allure CLI)
```

The tests use the public demo accounts shown on the saucedemo.com login page; no secrets are required.
