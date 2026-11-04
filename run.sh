# Point at a local service account key (kept out of git in secrets/, see .gitignore)
export GOOGLE_APPLICATION_CREDENTIALS="${GOOGLE_APPLICATION_CREDENTIALS:-$(pwd)/secrets/creds.json}"
python main.py
