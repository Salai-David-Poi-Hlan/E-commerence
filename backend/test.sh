for i in 1 2 3 4 5 6; do
    curl -s -o /dev/null -w "%{http_code}\n" -X POST http://localhost:8000/api/register/ \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"$i\",\"email\":\"u$i@example.com\",\"password\":\"c0rrect-horse-battery\"}"
done