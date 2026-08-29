import sys

filepath = 'backend/orders/models.py'
with open(filepath, 'r') as f:
    content = f.read()

import re

# We will replace the conflict block with the merged code.
merged_code = """    delivery_latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
    )
    delivery_longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
    )

    street = models.CharField(max_length=255)
    building = models.CharField(max_length=20)

    apartment = models.CharField(max_length=20, blank=True, default='')
    entrance = models.CharField(max_length=20, blank=True, default='')
    floor = models.PositiveSmallIntegerField(null=True, blank=True)

    delivery_notes = models.TextField(max_length=500, blank=True, default='')
    contact_phone = models.CharField(max_length=20, blank=True, default='')
"""

# The conflict block regex:
conflict_regex = re.compile(r'<<<<<<< HEAD\n.*?\n=======\n.*?\n>>>>>>> dev\n', re.DOTALL)
new_content = conflict_regex.sub(merged_code, content)

with open(filepath, 'w') as f:
    f.write(new_content)
