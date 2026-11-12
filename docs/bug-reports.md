# Bug reports — Swag Labs (saucedemo.com)

Defects found during exploratory testing. Every defect is covered by an automated regression test in
[`tests/test_known_defects.py`](../tests/test_known_defects.py), marked `xfail(strict=True)`: the test describes the
**correct** behaviour, so it starts failing the build as soon as the defect is fixed and the report can be closed.

> Swag Labs is a demo shop with intentionally broken demo accounts. The reports below are written as they would be
> for a real product.

**Environment:** https://www.saucedemo.com · Chromium, Firefox, WebKit (Playwright) · Windows 11 / Ubuntu 24.04
**Password for all accounts:** `secret_sauce`

| ID | Summary | Account | Severity | Priority |
|---|---|---|---|---|
| [BUG-01](#bug-01) | Item total shows floating-point noise | all accounts | Minor | High |
| [BUG-02](#bug-02) | All products show the same image | problem_user | Major | Medium |
| [BUG-03](#bug-03) | Sorting does not change the order | problem_user | Major | Medium |
| [BUG-04](#bug-04) | "Add to cart" does nothing for 3 of 6 products | problem_user | Critical | High |
| [BUG-05](#bug-05) | Last name input overwrites the first name | problem_user | Critical | High |
| [BUG-06](#bug-06) | Sorting shows "Sorting is broken!" alert | error_user | Major | Medium |
| [BUG-07](#bug-07) | "Finish" does not complete the order | error_user | Blocker | Highest |
| [BUG-08](#bug-08) | Inventory prices differ from the catalogue | visual_user | Critical | High |
| [BUG-09](#bug-09) | Login and navigation take ~5 seconds | performance_glitch_user | Major | Medium |

---

### BUG-01
**Item total on the checkout overview shows floating-point noise**

- **Steps:**
  1. Log in as `standard_user`.
  2. Add *Sauce Labs Bike Light* ($9.99) and *Sauce Labs Fleece Jacket* ($49.99) to the cart.
  3. Open the cart → *Checkout* → fill in any name and postal code → *Continue*.
- **Expected:** `Item total: $59.98`
- **Actual:** `Item total: $59.980000000000004`
- **Notes:** The sum depends on the order in which items were added (e.g. 5 items added in the order
  Bike Light, Bolt T-Shirt, Red T-Shirt, Backpack, Fleece Jacket give `$121.94999999999999`).
  The value is calculated with binary floating-point numbers and is not rounded before display.
  Tax and Total are rounded correctly.
- **Severity / Priority:** Minor / High — no money is lost, but a price shown this way undermines customer trust at the payment step.

### BUG-02
**All products show the same image**

- **Steps:** Log in as `problem_user`.
- **Expected:** Each of the 6 products shows its own photo.
- **Actual:** All 6 products show the same placeholder image (`/assets/sl-404-*.jpg`).
- **Severity / Priority:** Major / Medium

### BUG-03
**Sorting does not change the product order**

- **Steps:** Log in as `problem_user` → choose *Price (low to high)* in the sort dropdown.
- **Expected:** Products are ordered by ascending price.
- **Actual:** The order of products does not change.
- **Severity / Priority:** Major / Medium

### BUG-04
**"Add to cart" does nothing for half of the products**

- **Steps:** Log in as `problem_user` → click *Add to cart* on every product.
- **Expected:** The cart badge shows `6`.
- **Actual:** The badge shows `3`; for *Bolt T-Shirt*, *Fleece Jacket* and *Red T-Shirt* the button does not react.
  *Remove* also does not work for the added products.
- **Severity / Priority:** Critical / High — the customer cannot buy these products.

### BUG-05
**Typing the last name overwrites the first name**

- **Steps:** Log in as `problem_user` → add any product → *Cart* → *Checkout* → type `Anna` into *First Name*,
  then `Tester` into *Last Name*.
- **Expected:** First Name = `Anna`, Last Name = `Tester`.
- **Actual:** First Name = `Tester` (overwritten), Last Name stays empty → *Continue* shows
  `Error: Last Name is required`.
- **Severity / Priority:** Critical / High — checkout cannot be completed.

### BUG-06
**Sorting shows a JavaScript alert "Sorting is broken!"**

- **Steps:** Log in as `error_user` → choose any sort option.
- **Expected:** Products are sorted, no error.
- **Actual:** Browser alert: *"Sorting is broken! This error has been reported to Backtrace."*; products are not sorted.
- **Severity / Priority:** Major / Medium

### BUG-07
**"Finish" does not complete the order**

- **Steps:** Log in as `error_user` → add *Sauce Labs Backpack* → *Cart* → *Checkout* → fill in the form → *Continue* → *Finish*.
- **Expected:** "Checkout: Complete!" page with "Thank you for your order!".
- **Actual:** Nothing happens; the user stays on the overview page. Additionally, the *Last Name* field does not accept input,
  but the form can still be submitted without it.
- **Severity / Priority:** Blocker / Highest — no order can be placed.

### BUG-08
**Inventory prices differ from the catalogue**

- **Steps:** Log in as `visual_user`.
- **Expected:** Prices match the catalogue (e.g. *Sauce Labs Backpack* — $29.99).
- **Actual:** Prices are random and change with every session (e.g. `$63.71, $30.71, $81.99, $26.9, $0.7, $66.6`),
  some are shown with one decimal place; sorting by price therefore gives a wrong order.
- **Severity / Priority:** Critical / High — customers see wrong prices.

### BUG-09
**Login and page transitions take about 5 seconds**

- **Steps:** Log in as `performance_glitch_user`; then sort the products or return from the cart to the products page.
- **Expected:** Each transition completes within 2 seconds (response-time budget used in this project).
- **Actual:** Login ≈ 5.2 s, sorting ≈ 5.0 s, *Continue shopping* ≈ 5.0 s (measured with Playwright).
  `standard_user` completes the same steps in ~0.1 s.
- **Severity / Priority:** Major / Medium
