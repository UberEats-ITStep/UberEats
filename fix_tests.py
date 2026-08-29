import sys

filepath = 'backend/orders/tests.py'
with open(filepath, 'r') as f:
    content = f.read()

# Replace delivery_address with street and building
content = content.replace("'delivery_address': 'Kyiv, Main street 1',", "'street': 'Main street', 'building': '1',")

with open(filepath, 'w') as f:
    f.write(content)
