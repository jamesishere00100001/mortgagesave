# Mortgage Save web calculator. Served by our own nginx (rather than Railpack's
# default static server) so the security headers are ours to set.
# Build context: this folder (the service's root directory is /calculator).
# Everything in the folder is published except the build, test and server files.
FROM nginx:1.27-alpine
COPY nginx.conf start.sh /srv/
COPY . /srv/public/
RUN cd /srv/public && rm -f Dockerfile nginx.conf start.sh README.md build_guides.py *.test.mjs
CMD ["sh", "/srv/start.sh"]
