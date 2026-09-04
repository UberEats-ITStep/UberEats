import re

filepath = 'backend/ai/services.py'
with open(filepath, 'r') as f:
    content = f.read()

# Replace the RequestException logging to also log response body
new_except = """        except requests.exceptions.RequestException as e:
            error_body = e.response.text if e.response is not None else "No response body"
            logger.error(f"Groq network error: {str(e)} | Body: {error_body}")
            raise GroqAPIException()"""

content = re.sub(r'        except requests\.exceptions\.RequestException as e:\n            logger\.error\(f"Groq network error: \{str\(e\)\}"\)\n            raise GroqAPIException\(\)', new_except, content)

with open(filepath, 'w') as f:
    f.write(content)

