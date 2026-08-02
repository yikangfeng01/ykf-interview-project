-- ykf-interview-project-db initialization
-- Run: psql -d ykf-interview-project-db -f data/init.sql

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    token VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'draft',
    template_id INTEGER REFERENCES templates(id),
    created_by VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Migration: add description column if table already exists
ALTER TABLE projects ADD COLUMN IF NOT EXISTS description TEXT;

-- Standalone public variable pool (must be before signature_variables for FK reference)
CREATE TABLE IF NOT EXISTS public_variables (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    value TEXT DEFAULT '',
    var_type VARCHAR(50) NOT NULL DEFAULT 'signature',
    page INTEGER DEFAULT 1,
    x FLOAT DEFAULT 0,
    y FLOAT DEFAULT 0,
    width FLOAT DEFAULT 120,
    height FLOAT DEFAULT 40,
    font_size INTEGER DEFAULT 12,
    font_color VARCHAR(20) DEFAULT '#000000',
    required BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(name)
);

CREATE TABLE IF NOT EXISTS signature_variables (
    id SERIAL PRIMARY KEY,
    template_id INTEGER NOT NULL REFERENCES templates(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    value TEXT DEFAULT '',
    var_type VARCHAR(50) NOT NULL DEFAULT 'signature',
    page INTEGER DEFAULT 1,
    x FLOAT DEFAULT 0,
    y FLOAT DEFAULT 0,
    width FLOAT DEFAULT 120,
    height FLOAT DEFAULT 40,
    font_size INTEGER DEFAULT 12,
    font_color VARCHAR(20) DEFAULT '#000000',
    required BOOLEAN DEFAULT true,
    public_variables_id INTEGER REFERENCES public_variables(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(template_id, name)
);

-- Migration: add public_variables_id FK if signature_variables table already exists
ALTER TABLE signature_variables ADD COLUMN IF NOT EXISTS public_variables_id INTEGER REFERENCES public_variables(id) ON DELETE CASCADE;

-- Project-scoped template and variable tables (independent from global tables)
CREATE TABLE IF NOT EXISTS project_templates (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    description TEXT,
    public_template_id INTEGER REFERENCES templates(id) ON DELETE CASCADE
);

-- Migration: drop is_public column if exists (replaced by checking public_template_id IS NOT NULL)
ALTER TABLE project_templates DROP COLUMN IF EXISTS is_public;

CREATE TABLE IF NOT EXISTS project_template_variables (
    id SERIAL PRIMARY KEY,
    template_id INTEGER NOT NULL REFERENCES project_templates(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    value TEXT DEFAULT '',
    var_type VARCHAR(50) NOT NULL DEFAULT 'signature',
    page INTEGER DEFAULT 1,
    x FLOAT DEFAULT 0,
    y FLOAT DEFAULT 0,
    width FLOAT DEFAULT 120,
    height FLOAT DEFAULT 40,
    font_size INTEGER DEFAULT 12,
    font_color VARCHAR(20) DEFAULT '#000000',
    required BOOLEAN DEFAULT true,
    public_variables_id INTEGER REFERENCES public_variables(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(template_id, name)
);

-- Migration: add public_variables_id FK if project_template_variables table already exists
ALTER TABLE project_template_variables ADD COLUMN IF NOT EXISTS public_variables_id INTEGER REFERENCES public_variables(id) ON DELETE CASCADE;
