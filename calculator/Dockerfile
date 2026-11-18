# Mortgage Save web calculator. Served by our own nginx (rather than Railpack's
# default static server) so the security headers are ours to set.
# Build context: this folder (the service's root directory is /calculator).
FROM nginx:1.27-alpine
COPY nginx.conf start.sh /srv/
COPY index.html calc.js /srv/public/
CMD ["sh", "/srv/start.sh"]
