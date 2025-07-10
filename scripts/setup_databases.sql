-- PostgreSQL setup script for Zero Vector 4
-- Run this as postgres superuser

-- Create user
CREATE USER zv4_user WITH PASSWORD 'zv4_dev_password_2024';

-- Create database
CREATE DATABASE zero_vector_4 OWNER zv4_user;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE zero_vector_4 TO zv4_user;

-- Connect to the database and grant schema privileges
\c zero_vector_4;
GRANT ALL ON SCHEMA public TO zv4_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO zv4_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO zv4_user;

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create vector extension for embeddings (if available)
-- CREATE EXTENSION IF NOT EXISTS vector;

COMMENT ON DATABASE zero_vector_4 IS 'Zero Vector 4 - Advanced Multi-Agent AI Society Platform';
