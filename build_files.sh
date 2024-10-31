python3.12 -m pip install -r requirements.txt

python3.12 manage.py collectstatic --noinput --clear
export PATH="/python312/bin:$PATH"
export $(grep -v '^#' .env | xargs)