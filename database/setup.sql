CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password  TEXT NOT NULL,
    role TEXT CHECK (role IN('Admin','Manager','Salesperson')) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE leads (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    status TEXT CHECK (status IN ('New', 'Contacted', 'Qualified', 'Converted')) NOT NULL DEFAULT 'New',
    assigned_to INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE activities (
    id SERIAL PRIMARY KEY,
    lead_id INTEGER REFERENCES leads(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    activity_type TEXT CHECK (activity_type IN ('Call', 'Email', 'Meeting')) NOT NULL,
    summary TEXT NOT NULL,
    activity_date DATE NOT NULL DEFAULT CURRENT_DATE
);

