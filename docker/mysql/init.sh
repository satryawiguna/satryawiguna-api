#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# MySQL Initialization Script
# Runs ONCE on first container creation (when data volume is empty).
#
# Creates:
#   - satryawiguna_dev  (dev database)
#   - satryawiguna      (prod database)
#   - root_dev user     (scoped to satryawiguna_dev only)
#
# Passwords come from .env.mysql via the MySQL container's environment:
#   MYSQL_ROOT_PASSWORD → used for root user (already set by MySQL image)
#   MYSQL_DEV_PASSWORD  → password for root_dev user
# ─────────────────────────────────────────────────────────────────────────────
set -e

mysql -u root -p"${MYSQL_ROOT_PASSWORD}" <<-EOSQL
    -- ── Databases ─────────────────────────────────────────────────────────
    CREATE DATABASE IF NOT EXISTS \`satryawiguna_dev\`
        CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

    CREATE DATABASE IF NOT EXISTS \`satryawiguna\`
        CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

    -- ── Dev user (scoped to satryawiguna_dev only) ─────────────────────────
    CREATE USER IF NOT EXISTS 'root_dev'@'%'
        IDENTIFIED BY '${MYSQL_DEV_PASSWORD}';

    GRANT ALL PRIVILEGES ON \`satryawiguna_dev\`.* TO 'root_dev'@'%';

    -- ── Ensure root has explicit remote access to prod DB ──────────────────
    GRANT ALL PRIVILEGES ON \`satryawiguna\`.* TO 'root'@'%';

    FLUSH PRIVILEGES;
EOSQL

echo "✅ MySQL databases and users initialized."
