#!/bin/bash
set -e

DB_NAME=$2
DB_USER=$3
DB_PASS=$4

# Default OS user handling
if [ -z "$DB_USER" ]; then
    DB_USER=$(whoami)
    USE_LOCAL_OS_USER=true
else
    USE_LOCAL_OS_USER=false
fi

function setup() {
    if [ -z "$DB_NAME" ]; then
      echo "Usage: $0 setup <db_name> [db_user] [db_password]"
      exit 1
    fi

    echo "==> Checking for PostgreSQL..."
    if ! command -v psql &> /dev/null; then
      echo "PostgreSQL is not installed. Please install it first."
      exit 1
    fi

    # Initialize DB if not already
    if ! sudo -u postgres psql -tAc "SELECT 1" &> /dev/null; then
        echo "==> Initializing database..."
        sudo postgresql-setup --initdb
    fi

    echo "==> Starting PostgreSQL..."
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
    sleep 2

    # Create database if missing
    DB_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='${DB_NAME}'")
    if [ "$DB_EXISTS" != "1" ]; then
        echo "Creating database ${DB_NAME}..."
        sudo -u postgres psql -c "CREATE DATABASE ${DB_NAME};"
    else
        echo "Database ${DB_NAME} already exists."
    fi

    # Create user/role if missing
    USER_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='${DB_USER}'")
    if [ "$USER_EXISTS" != "1" ]; then
        if [ "$USE_LOCAL_OS_USER" = true ]; then
            echo "Creating PostgreSQL role for OS user ${DB_USER}..."
            sudo -u postgres psql -c "CREATE ROLE ${DB_USER} LOGIN;"
        else
            echo "Creating user ${DB_USER} with password..."
            sudo -u postgres psql -c "CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASS}';"
        fi
    else
        echo "User ${DB_USER} already exists."
    fi

    # Grant privileges and set schema ownership
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};"
    sudo -u postgres psql -d "${DB_NAME}" -c "ALTER SCHEMA public OWNER TO ${DB_USER};"
    sudo -u postgres psql -d "${DB_NAME}" -c "GRANT USAGE ON SCHEMA public TO ${DB_USER};"
    sudo -u postgres psql -d "${DB_NAME}" -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ${DB_USER};"
    sudo -u postgres psql -d "${DB_NAME}" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO ${DB_USER};"

    # Create pgvector extension (superuser required)
    echo "==> Creating pgvector extension (superuser required)..."
    sudo -u postgres psql -d "${DB_NAME}" -c "CREATE EXTENSION IF NOT EXISTS vector;"

    echo "==> Done."
    echo "__________Connect info__________:"
    if [ "$USE_LOCAL_OS_USER" = true ]; then
        echo "postgresql:///${DB_NAME}"
    else
        echo "postgresql://${DB_USER}:${DB_PASS}@localhost:5432/${DB_NAME}"
    fi
}

function delete() {
    if [ -z "$DB_NAME" ]; then
      echo "Usage: $0 rm <db_name> [db_user]"
      exit 1
    fi

    echo "==> Dropping database ${DB_NAME} (if exists)..."
    sudo -u postgres psql -c "DROP DATABASE IF EXISTS ${DB_NAME};"

    if [ "$USE_LOCAL_OS_USER" = false ]; then
        echo "==> Dropping user ${DB_USER} (if exists)..."
        sudo -u postgres psql -c "DROP ROLE IF EXISTS ${DB_USER};"
    fi

    echo "==> Done."
}

# Command dispatch
COMMAND=$1
case "$COMMAND" in
    setup)
        setup
        ;;
    rm)
        delete
        ;;
    *)
        echo "Usage: $0 {setup|rm} <db_name> [db_user] [db_password]"
        exit 1
        ;;
esac