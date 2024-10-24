psql -c "CREATE DATABASE stock_analytics"
psql stock_analytics -c "CREATE EXTENSION IF NOT EXISTS \"vector\""