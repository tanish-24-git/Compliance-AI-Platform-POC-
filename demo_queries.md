# Demo SQL Queries for Live Demonstration

This file contains SQL queries to demonstrate the Compliance-First AI Content Generation Platform during live demos.

## 1. List All Active Rules

```sql
SELECT 
    id,
    rule_text,
    severity,
    version,
    is_active,
    created_at
FROM rules
WHERE is_active = TRUE
ORDER BY created_at DESC;
```

## 2. List All Violations

```sql
SELECT 
    v.id,
    v.submission_id,
    s.user_id,
    r.rule_text,
    v.severity,
    v.violated_text,
    v.context,
    v.detected_at
FROM violations v
JOIN submissions s ON v.submission_id = s.id
JOIN rules r ON v.rule_id = r.id
ORDER BY v.detected_at DESC
LIMIT 50;
```

## 3. Violation Details (User, Rule, Text, Timestamp)

```sql
SELECT 
    u.username,
    u.email,
    u.role,
    r.rule_text,
    r.severity AS rule_severity,
    v.violated_text,
    v.context,
    v.detected_at AS violation_timestamp,
    s.prompt AS original_prompt,
    s.compliance_status
FROM violations v
JOIN submissions s ON v.submission_id = s.id
JOIN users u ON s.user_id = u.id
JOIN rules r ON v.rule_id = r.id
ORDER BY v.detected_at DESC;
```

## 4. Rule Hit Frequency (Most Violated Rules)

```sql
SELECT 
    r.id AS rule_id,
    r.rule_text,
    r.severity,
    COUNT(v.id) AS violation_count
FROM rules r
LEFT JOIN violations v ON r.id = v.rule_id
WHERE r.is_active = TRUE
GROUP BY r.id, r.rule_text, r.severity
ORDER BY violation_count DESC;
```

## 5. Audit Logs (Recent Activity)

```sql
SELECT 
    a.id,
    u.username,
    u.role,
    a.action,
    a.entity_type,
    a.entity_id,
    a.details,
    a.created_at
FROM audit_logs a
JOIN users u ON a.user_id = u.id
ORDER BY a.created_at DESC
LIMIT 100;
```

## 6. Submission Success Rate

```sql
SELECT 
    compliance_status,
    COUNT(*) AS count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage
FROM submissions
WHERE status IN ('approved', 'rejected')
GROUP BY compliance_status;
```

## 7. HARD vs SOFT Violations Breakdown

```sql
SELECT 
    severity,
    COUNT(*) AS violation_count,
    COUNT(DISTINCT submission_id) AS affected_submissions
FROM violations
GROUP BY severity;
```

## 8. User Activity Summary

```sql
SELECT 
    u.username,
    u.role,
    COUNT(s.id) AS total_submissions,
    SUM(CASE WHEN s.compliance_status = 'approved' THEN 1 ELSE 0 END) AS approved,
    SUM(CASE WHEN s.compliance_status = 'rejected' THEN 1 ELSE 0 END) AS rejected
FROM users u
LEFT JOIN submissions s ON u.id = s.user_id
GROUP BY u.id, u.username, u.role;
```

## 9. Rule Version History

```sql
SELECT 
    id,
    rule_text,
    version,
    parent_rule_id,
    is_active,
    created_at,
    created_by
FROM rules
WHERE parent_rule_id IS NOT NULL OR id IN (SELECT parent_rule_id FROM rules WHERE parent_rule_id IS NOT NULL)
ORDER BY COALESCE(parent_rule_id, id), version;
```

## 10. Recent Submissions with Violation Count

```sql
SELECT 
    s.id,
    s.prompt,
    s.status,
    s.compliance_status,
    s.created_at,
    COUNT(v.id) AS violation_count
FROM submissions s
LEFT JOIN violations v ON s.id = v.submission_id
GROUP BY s.id
ORDER BY s.created_at DESC
LIMIT 20;
```

## 11. Content Chunks Analysis

```sql
SELECT 
    submission_id,
    source_type,
    COUNT(*) AS chunk_count,
    AVG(token_count) AS avg_tokens,
    SUM(token_count) AS total_tokens
FROM content_chunks
GROUP BY submission_id, source_type
ORDER BY submission_id DESC;
```

## 12. Super Admin Actions

```sql
SELECT 
    a.action,
    COUNT(*) AS action_count,
    MAX(a.created_at) AS last_performed
FROM audit_logs a
JOIN users u ON a.user_id = u.id
WHERE u.role = 'super_admin'
GROUP BY a.action
ORDER BY action_count DESC;
```

---

## How to Use These Queries

1. **Connect to PostgreSQL**:
   ```bash
   docker exec -it compliance-postgres psql -U compliance -d compliance_db
   ```

2. **Run any query** by copying and pasting from above

3. **For formatted output**, use:
   ```sql
   \x  -- Toggle expanded display
   ```

4. **Export results**:
   ```bash
   docker exec -it compliance-postgres psql -U compliance -d compliance_db -c "YOUR_QUERY" > output.txt
   ```
