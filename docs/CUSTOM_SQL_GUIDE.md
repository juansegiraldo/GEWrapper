# 🔍 Custom SQL Query Guide for Data Validation

## Overview
This guide helps you write effective SQL queries for data validation using the GEWrapper application. The queries should identify data quality violations and return a count of problematic records.

## 🎯 Basic Query Structure

All custom SQL queries should follow this pattern:

```sql
SELECT COUNT(*) as violation_count
FROM {table_name}
WHERE [your_validation_conditions]
```

## 🔧 Key Requirements

### 1. Table Name Placeholder
- **Always use**: `{table_name}` as the table name
- **Never use**: actual table names like `employees` or `data_table`

### 2. Return Column
- **Always return**: `violation_count` column
- **Use**: `COUNT(*) as violation_count`

### 3. Boolean Column Syntax
- **✅ Recommended**: `active = True` / `active = False`
- **⚠️ Works**: `active = 1` / `active = 0` (automatically converted)
- **❌ Avoid**: `active = 'true'` / `active = 'false'` (string comparison)

## 💡 LLM Prompt for SQL Generation

Use this prompt with any LLM (ChatGPT, Claude, etc.) to generate custom SQL queries:

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

## 🔧 Common Validation Patterns

### Salary Validation
```sql
SELECT COUNT(*) as violation_count
FROM {table_name}
WHERE department = 'Sales' AND active = True AND salary < 40000
```

### Date Range Validation
```sql
SELECT COUNT(*) as violation_count
FROM {table_name}
WHERE join_date < '2020-01-01' OR join_date > CURRENT_DATE
```

### Email Format Validation
```sql
SELECT COUNT(*) as violation_count
FROM {table_name}
WHERE email NOT LIKE '%@%.%' OR email IS NULL
```

### Age Range Validation
```sql
SELECT COUNT(*) as violation_count
FROM {table_name}
WHERE age < 18 OR age > 65
```

### Required Field Validation
```sql
SELECT COUNT(*) as violation_count
FROM {table_name}
WHERE name IS NULL OR TRIM(name) = ''
```

### Cross-Column Validation
```sql
SELECT COUNT(*) as violation_count
FROM {table_name}
WHERE start_date >= end_date AND start_date IS NOT NULL AND end_date IS NOT NULL
```

### Duplicate Detection
```sql
SELECT COUNT(*) as violation_count
FROM {table_name}
WHERE email IN (
    SELECT email 
    FROM {table_name} 
    GROUP BY email 
    HAVING COUNT(*) > 1
)
```

## 🚨 Common Mistakes to Avoid

### ❌ Wrong Boolean Syntax
```sql
-- Don't do this:
WHERE active = 'true' AND status = '1'

-- Do this instead:
WHERE active = True AND status = 'active'
```

### ❌ Missing Table Placeholder
```sql
-- Don't do this:
FROM employees

-- Do this instead:
FROM {table_name}
```

### ❌ Wrong Return Column
```sql
-- Don't do this:
SELECT COUNT(*) as count

-- Do this instead:
SELECT COUNT(*) as violation_count
```

### ❌ Complex Aggregations
```sql
-- Don't do this (too complex):
SELECT SUM(CASE WHEN salary < 40000 THEN 1 ELSE 0 END) as violation_count

-- Do this instead:
SELECT COUNT(*) as violation_count
WHERE salary < 40000
```

## 🎯 Best Practices

### 1. Keep It Simple
- Focus on one validation rule per query
- Use clear, readable conditions
- Avoid complex subqueries when possible

### 2. Handle NULL Values
- Always consider NULL values in your conditions
- Use `IS NULL` or `IS NOT NULL` appropriately
- Example: `WHERE (email IS NULL OR email NOT LIKE '%@%.%')`

### 3. Use Descriptive Names
- Name your expectations clearly
- Example: "Sales Active Employee Salary Validation"
- Include the business rule in the description

### 4. Test Your Queries
- Use the "🧪 Test Query" button to verify results
- Check that the violation count makes sense
- Review the failing records to ensure accuracy

## 🔄 Migration from Old Syntax

If you have existing queries using `active = 1`, they will work but consider updating them:

### Old Style (Still Works)
```sql
SELECT COUNT(*) as violation_count
FROM {table_name}
WHERE department = 'Sales' AND active = 1 AND salary < 40000
```

### New Style (Recommended)
```sql
SELECT COUNT(*) as violation_count
FROM {table_name}
WHERE department = 'Sales' AND active = True AND salary < 40000
```

## 📊 Understanding Results

### Expected Result Types
- **empty**: Expect 0 violations (query should return 0)
- **non_empty**: Expect violations to exist (query should return > 0)
- **count_equals**: Expect specific number of violations
- **count_between**: Expect violations within a range

### Example: Salary Validation
- **Query**: Finds Sales employees with salary < 40000
- **Expected Result**: `empty` (should be 0 violations)
- **If Result**: 1 violation found
- **Meaning**: Frank Miller has salary 35000, which violates the rule

## 🎉 Success Tips

1. **Start Simple**: Begin with basic conditions and add complexity
2. **Test Incrementally**: Test each part of your WHERE clause
3. **Use the LLM Prompt**: Let AI help you write the initial query
4. **Review Failing Records**: Always check what records are actually failing
5. **Document Your Rules**: Keep notes on what each validation checks

## 🆘 Getting Help

If you're stuck:
1. Use the LLM prompt above with ChatGPT/Claude
2. Check the "Common Validation Patterns" section
3. Use the "🧪 Test Query" button to debug
4. Review the "Common Mistakes" section
5. Start with a simple query and build up complexity

---

**Happy Data Validating! 🎯**