import streamlit as st
import requests
from authlib.integrations.requests_client import OAuth2Session
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# GitHub OAuth credentials from environment variables
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
OAUTH2_TOKEN_URL = "http://127.0.0.1:8000/github/callback"  # Backend callback URL

# Streamlit UI
st.title('Generative AI Code Review Bot')

# OAuth2 flow to authenticate the user
def github_oauth_flow():
    client = OAuth2Session(GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET)
    
    # Construct GitHub OAuth URL with the redirect URI
    authorization_url, state = client.create_authorization_url(
        "https://github.com/login/oauth/authorize",
        redirect_uri="http://127.0.0.1:8501/github/callback"  # Ensure this matches backend callback
    )
    
    st.write(f"Please [login with GitHub]({authorization_url})")
    
    # Fetch the token after authorization
    code = st.text_input("Enter the authorization code from GitHub:")
    if code:
        # Backend will exchange the code for a JWT token
        response = requests.get(f"{OAUTH2_TOKEN_URL}?code={code}")
        if response.status_code == 200:
            token = response.json().get("access_token")
            return token
        else:
            st.error("GitHub authentication failed.")
    return None

# Authenticate user and manage session
if 'token' not in st.session_state:
    st.session_state['token'] = None  # Initialize token if not in session state

# OAuth flow - login or authenticated state
if st.session_state['token'] is None:
    # Execute OAuth flow if not authenticated
    token = github_oauth_flow()

    if token:
        st.session_state['token'] = token  # Save the token in session state
        st.success("You have successfully logged in with GitHub!")
        st.experimental_rerun()  # Rerun the app to switch to the chatbot interface
else:
    # If authenticated, show PR review UI
    st.success("You are authenticated with GitHub. Welcome to the Code Review Bot!")
    
    # Get input for repository and PR number
    repository_url = st.text_input("Enter GitHub Repository URL (e.g., https://github.com/user/repo)")
    pr_number = st.number_input("Enter Pull Request Number", min_value=1)

    if st.button("Review Pull Request"):
        if repository_url and pr_number:
            try:
                # Make request to backend for PR review
                response = requests.post(
                    "http://127.0.0.1:8000/review_pr/", 
                    json={"repository_url": repository_url, "pr_number": pr_number},
                    headers={"Authorization": f"Bearer {st.session_state['token']}"}
                )
                if response.status_code == 200:
                    review_feedback = response.json().get("feedback")
                    st.write("### Code Review Feedback:")
                    st.write(review_feedback)
                else:
                    st.error(f"Error: {response.json().get('detail')}")
            except requests.exceptions.RequestException as e:
                st.error(f"Failed to connect to the server: {e}")
        else:
            st.error("Please provide both repository URL and PR number.")
