# Mortgage Save web calculator. Served by our own nginx (rather than Railpack's
# default static server) so the security headers are ours to set.
# Build context: this folder (the service's root directory is /calculator).
FROM nginx:1.27-alpine
COPY nginx.conf start.sh /srv/
COPY index.html calc.js simulator.js tools.js guide.js site.css robots.txt sitemap.xml og-image.png /srv/public/
COPY lump-sum-overpayment-calculator /srv/public/lump-sum-overpayment-calculator/
COPY mortgage-overpayment-allowance-calculator /srv/public/mortgage-overpayment-allowance-calculator/
COPY fixed-rate-ending-calculator /srv/public/fixed-rate-ending-calculator/
COPY overpay-mortgage-or-save-calculator /srv/public/overpay-mortgage-or-save-calculator/
CMD ["sh", "/srv/start.sh"]
