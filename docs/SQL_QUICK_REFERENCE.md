# 🚀 SQL Quick Reference Card

## 💡 Copy-Paste LLM Prompt

```
Generate a SQL query to validate data quality. Requirements:
- Use {table_name} as the table name placeholder
- Return COUNT(*) as violation_count
- Use True/False for boolean columns (not 1/0)
- Example: WHERE active = True AND salary < 40000
- Focus on finding violations (rows that should NOT exist)
- Use clear, descriptive conditions

Context: [Describe your validation rule here]

Example context: "Find employees in Sales department who are active but have salary less than 40000"
```

## ✅ Correct Syntax Examples

### Basic Structure
```sql
SELECT COUNT(*) as violation_count
FROM {table_name}
WHERE [conditions]
```

### Boolean Columns
```sql
-- ✅ Correct
WHERE active = True AND status = 'active'

-- ⚠️ Works (auto-converted)
WHERE active = 1 AND status = 1

-- ❌ Wrong
WHERE active = 'true' AND status = '1'
```

### Common Patterns

**Salary Validation:**
```sql
SELECT COUNT(*) as violation_count
FROM {table_name}
WHERE department = 'Sales' AND active = True AND salary < 40000
```

**Email Validation:**
```sql
SELECT COUNT(*) as violation_count
FROM {table_name}
WHERE email NOT LIKE '%@%.%' OR email IS NULL
```

**Date Range:**
```sql
SELECT COUNT(*) as violation_count
FROM {table_name}
WHERE join_date < '2020-01-01' OR join_date > CURRENT_DATE
```

**Required Fields:**
```sql
SELECT COUNT(*) as violation_count
FROM {table_name}
WHERE name IS NULL OR TRIM(name) = ''
```

## 🚨 Common Mistakes

| ❌ Wrong | ✅ Correct |
|----------|------------|
| `FROM employees` | `FROM {table_name}` |
| `COUNT(*) as count` | `COUNT(*) as violation_count` |
| `active = 'true'` | `active = True` |
| `active = '1'` | `active = True` |

## 🎯 Expected Results

- **empty**: Expect 0 violations (most common)
- **non_empty**: Expect violations to exist
- **count_equals**: Expect specific number
- **count_between**: Expect range

---

**💡 Tip**: Use the "🧪 Test Query" button to verify your query works!
