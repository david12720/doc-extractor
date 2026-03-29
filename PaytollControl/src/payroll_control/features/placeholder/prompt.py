PROMPT = """Extract the following fields from this payroll document image:
- employee_name: Full name of the employee
- employee_id: ID number
- gross_salary: Gross salary amount

Return the data as a JSON array of objects with these exact keys.
Example: [{"employee_name": "ישראל ישראלי", "employee_id": "123456789", "gross_salary": "10000"}]
"""
