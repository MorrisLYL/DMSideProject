-- init.sql: Create file_data table
CREATE TABLE IF NOT EXISTS file_data (
    id SERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'Uploading',
    text_content TEXT
);
