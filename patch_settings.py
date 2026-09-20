import re

filepath = "backend/config/settings.py"
with open(filepath, "r") as f:
    content = f.read()

# Add favorites throttle rate to DEFAULT_THROTTLE_RATES
throttle_addition = """        "auth_firebase": "10/min",
        "favorites": "60/min",
        "verify_email": "10/hour","""

content = re.sub(
    r'        "auth_firebase": "10/min",\n        "verify_email": "10/hour",',
    throttle_addition,
    content
)

with open(filepath, "w") as f:
    f.write(content)
