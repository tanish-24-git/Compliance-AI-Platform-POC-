INSERT INTO users (user_id, username, role) 
VALUES ('00000000-0000-0000-0000-000000000001', 'mock_agent', 'AGENT')
ON CONFLICT (user_id) DO NOTHING;
