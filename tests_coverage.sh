coverage erase
coverage run --source polymorph run_tests.py
# Deleting htmlcov directory if exists
[ -e htmlcov ] && rm -r htmlcov
echo "[+] Converting results to html..."
coverage html
echo "[+] Opening your browser..."
firefox htmlcov/index.html &
