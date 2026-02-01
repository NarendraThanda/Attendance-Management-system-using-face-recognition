# Deployment Guide

You encountered a `250 MB` limit on Vercel. This is because **OpenCV** and **Streamlit** together are too large for Vercel's Serverless Functions.
Additionally, **GitHub Pages** cannot run this app because it only supports "Static Sites" (HTML/CSS), not Python applications.

## The Solution: Streamlit Community Cloud

The best (and free) place to deploy this app is **Streamlit Community Cloud**. It is optimized for exactly this kind of Python app and does not have the 250MB limit in the same way.

### Steps to Deploy

1.  **Push to GitHub**
    *   If you haven't already, push your code to a new GitHub repository:
        ```bash
        git init
        git add .
        git commit -m "Initial commit"
        # Create repo on GitHub.com called 'attendance-system'
        git remote add origin https://github.com/YOUR_USERNAME/attendance-system.git
        git push -u origin master
        ```

2.  **Sign up for Streamlit Cloud**
    *   Go to [share.streamlit.io](https://share.streamlit.io/).
    *   Sign in with your GitHub account.

3.  **Deploy**
    *   Click **"New app"**.
    *   Select your GitHub repository (`attendance-system`).
    *   Select the branch (`master` or `main`).
    *   Main file path: `streamlit_app.py`.
    *   Click **"Deploy!"**.

### Why this works
*   **No Size Limit**: It runs in a full container, not a tiny function.
*   **Camera Support**: Streamlit Cloud handles the SSL/HTTPS required for camera access.
*   **Free**: It is free for public repositories.

### Note on Persistence
Streamlit Cloud app restarts occasionally.
*   **Registered Students**: Will be saved to `data/attendance.db` *inside the container*.
*   **Warning**: If the app restarts (after a few days of inactivity), **YOU WILL LOSE DATA** unless you connect it to an external database (like Google Sheets or Firestore).
*   For a university project demo, this is usually acceptable.
