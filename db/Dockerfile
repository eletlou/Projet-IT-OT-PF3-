FROM mysql:8.0.35

# Initialise uniquement la structure et les referentiels minimums.
COPY db/01-schema.sql db/02-bootstrap.sql /docker-entrypoint-initdb.d/
