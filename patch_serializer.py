import re

filepath = "backend/users/serializers.py"
with open(filepath, "r") as f:
    content = f.read()

phone_replacement = """    phone_number = serializers.CharField(
        max_length=16,
        required=False,
        allow_null=True,
        allow_blank=True,
        validators=[PHONE_NUMBER_VALIDATOR],
    )
    address = serializers.CharField(
        max_length=500,
        required=False,
        allow_null=True,
        allow_blank=True,
    )"""

content = re.sub(
    r"    phone_number = serializers\.CharField\(\n        max_length=16,\n        required=False,\n        validators=\[PHONE_NUMBER_VALIDATOR\],\n    \)\n    address = serializers\.CharField\(\n        max_length=500,\n        required=False,\n    \)",
    phone_replacement,
    content
)

with open(filepath, "w") as f:
    f.write(content)
