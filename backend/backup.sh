#!/bin/bash
DATE=$(date +%Y-%m-%d)
PGPASSWORD=$DB_PASSWORD pg_dump -U $DB_USER -h $DB_HOST $DB_NAME | gzip > /backups/db_$DATE.sql.gz