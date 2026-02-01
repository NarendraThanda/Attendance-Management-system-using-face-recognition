# Deployment Guide: Streamlit Cloud

Your application uses **Streamlit** (Web UI) and **OpenCV** (Face Recognition).
These libraries are too large for **Vercel** (which has a 250MB limit).
**GitHub Pages** cannot run this because it does not support Python.

**The Solution: Streamlit Community Cloud**
This is a free service specifically for hosting Streamlit apps.

## Instructions

1.  **Push to GitHub**
    Ensure this folder is a GitHub repository.
    ```bash
    git add .
    git commit -m "Ready for deployment"
    git push origin master
    ```

2.  **Deploy on Streamlit Cloud**
    1.  Go to [share.streamlit.io](https://share.streamlit.io/)
    2.  Login with GitHub.
    3.  Click **"New app"**.
    4.  Select your repository: `Attendance-Management-system...`
    5.  Set **Main file path** to: `streamlit_app.py`
    6.  Click **"Deploy!"**.

3.  **Done!**
    Your app will be live. The camera will work in the browser.

## Note on Data
Streamlit Cloud is ephemeral. If the app restarts, the SQLite database `database.db` might reset.
For a permanent app, you would need to connect to a cloud database (like Google Sheets, Firestore, or Supabase), but for a demo, this current setup is fine.
