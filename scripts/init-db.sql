-- Enable required PostgreSQL extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE elastic_newsroom TO newsroom_user;
