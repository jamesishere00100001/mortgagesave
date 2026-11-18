# Mortgage Save web calculator

Free UK mortgage overpayment calculator. Static page: `index.html` + `calc.js` (a port of the iOS app's `MortgageCalculator.swift`). No build step, no backend, no analytics.

- Tests: `node --test calc.test.mjs tools.test.mjs`
- Guide pages (one folder each, e.g. `lump-sum-overpayment-calculator/index.html`) share `site.css` and `guide.js`. Their maths is in `tools.js` and `simulator.js` (a port of the app's `RepaymentSimulator.swift`, monthly interest only). New pages need adding to `sitemap.xml` and to the Dockerfile `COPY` lines.
- Hosting: Railway service with root directory `/calculator`; the Dockerfile serves it with nginx (`nginx.conf` sets the security headers, including the CSP). A new external script, font or image host has to be added to the CSP there.
- If the maths changes here, change it in the app too, and re-run the tests.
