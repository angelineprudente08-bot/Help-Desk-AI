# Setting up "Sign in with Google"

The button works once the app has a Google Client ID and Client Secret.
Until then, clicking it shows a message and email/password sign-in keeps working.

1. Go to https://console.cloud.google.com/ and create a project (any name, e.g. HelpDesk AI).
2. APIs & Services > OAuth consent screen: choose **External**, enter the app name and your email, save.
   While the app is in "Testing", add the Gmail accounts that may sign in under **Test users**.
3. APIs & Services > Credentials > Create credentials > **OAuth client ID**
   - Application type: **Web application**
   - Authorized redirect URIs: add both
     - `http://127.0.0.1:5000/login/google/callback`
     - `http://localhost:5000/login/google/callback`
4. Download the JSON from Google and save it as `google_oauth.json` next to run.py, or copy `google_oauth.example.json` to `google_oauth.json`
   and paste the Client ID and Client Secret in.
   (Alternatively set the environment variables GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET.)
5. Restart the app: `venv\Scripts\python.exe run.py`

Notes
- Someone signing in with Google for the first time gets a new **requester** account.
- If the Gmail address already belongs to an account (for example a technician), they sign in to that account.
- Keep google_oauth.json private; do not upload it to GitHub.
