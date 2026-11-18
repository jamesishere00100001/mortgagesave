# Mortgage Save web calculator

Free UK mortgage overpayment calculator. Static page: `index.html` + `calc.js` (a port of the iOS app's `MortgageCalculator.swift`). No build step, no backend, no analytics.

- Tests: `node --test calc.test.mjs`
- Hosting: Railway service with root directory `/calculator`; the Dockerfile serves it with nginx (`nginx.conf` sets the security headers, including the CSP). A new external script, font or image host has to be added to the CSP there.
- If the maths changes here, change it in the app too, and re-run the tests.
