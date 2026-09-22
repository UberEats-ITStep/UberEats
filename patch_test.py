import re

filepath = "backend/users/tests.py"
with open(filepath, "r") as f:
    content = f.read()

replacement = """        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should now allow blank fields as requested"""

content = re.sub(
    r"        self\.assertEqual\(response\.status_code, status\.HTTP_400_BAD_REQUEST\)\n        self\.assertEqual\(str\(response\.data\['phone_number'\]\[0\]\), 'This field may not be blank\.'\)\n        self\.assertEqual\(str\(response\.data\['address'\]\[0\]\), 'This field may not be blank\.'\)",
    replacement,
    content
)

with open(filepath, "w") as f:
    f.write(content)
