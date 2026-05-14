CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    task_code TEXT UNIQUE NOT NULL,
    original_request TEXT NOT NULL,
    intent TEXT NOT NULL,
    entities JSONB NOT NULL,
    risk_score INTEGER NOT NULL,
    risk_reason TEXT NOT NULL,
    steps JSONB NOT NULL,
    employee_team TEXT NOT NULL,
    status TEXT DEFAULT 'Pending',
    whatsapp_message TEXT,
    email_message TEXT,
    sms_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS status_history (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES tasks(id),
    old_status TEXT,
    new_status TEXT NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);