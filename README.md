# News Digest Aggregator

A full-stack web application designed to deliver personalized news feeds. Users can authenticate securely via GitHub, customize their preferred news sections, manage custom topics, and enjoy a streamlined reading experience tailored to their interests.

## Tech Stack

* **Frontend:** React, Vite, JavaScript
* **Backend:** Python, FastAPI, SQLAlchemy, PyJWT
* **Database:** PostgreSQL (with relational many-to-many and one-to-many schema design)
* **Authentication:** GitHub OAuth 2.0 & JSON Web Tokens (JWT with HS256 signing)

---

## Current Features

* **GitHub Authentication:** Secure login flow leveraging GitHub OAuth and token-based session management (`JWT`).
* **Personalized Preferences:**
  * Select and toggle favorite news sections.
  * Add and delete custom free-text topics (e.g., specific events, names, or technologies).
* **Dynamic Navigation:** The application interface adapts to show only the user's preferred sections when logged in, falling back to a full view otherwise.
* **Persistent Settings:** Fully synchronized backend routes ensuring user sections and custom topics are saved securely in PostgreSQL across sessions.

---

## Future Roadmap

* **Cloud Deployment:** Host the application live using platforms like Render/Railway (backend), Vercel (frontend), and Neon/Supabase (PostgreSQL).
* **Saved Articles / Bookmarks:** Allow users to bookmark specific articles for later reading.
* **Automated Article Ingestion:** Integrate background workers or RSS feed parsers to automatically pull fresh news articles into the database.
* **UI Enhancements:** Implement dark mode support and optimize the responsive design for mobile devices.

---

## Getting Started Locally

### Backend Setup
1. Navigate to the backend directory and create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate

2. Install dependencies:
    ```bash
    pip install -r requirements.txt

3. Configure your `.env` file with your database URL, GitHub credentials, and `JWT_SECRET`.

4. Start the FastAPI server:
    ```bash
    uvicorn main:app --reload

### Frontend Setup
1. Navigate to the frontend directory and run
    ```bash
    npm install

2. Start the development server:
    ```bash
    npm run dev
