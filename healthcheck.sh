#альтернативный запуск через скрипт python
#curl -s 'http://localhost:8080/healthcheck' | \
#     python healthcheck.py

curl -s 'http://localhost:8080/healthcheck' | \
    python -c "
import sys
import json

JSON = json.load(sys.stdin)
result = 0
for value in JSON.values():
    if value != [True, ]:
        result += 1
if result:
    print(1)
else:
    print(0)
"
