import streamlit as st
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from github import Github, Auth, GithubException
import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import httpx
import jwt
from datetime import datetime, timedelta

load_dotenv()

# Environment variables
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
GITHUB_REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()
llm = ChatGroq(temperature=0, api_key=os.getenv("GROQ_API_KEY"), model="llama-3.3-70b-versatile")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class PullRequest(BaseModel):
    repository_url: str
    pr_number: int

TIMEOUT = 30  

async def fetch_pr_details(repo_url: str, pr_number: int):
    load_dotenv()
    Github_token = os.getenv("GITHUB_TOKEN")
    try:
        auth = Auth.Token(Github_token)
        g = Github(auth=auth, base_url="https://api.github.com")

        owner, repo_name = repo_url.strip('https://github.com/').split('/')
        repo = g.get_repo(f"{owner}/{repo_name}")

        pr = repo.get_pull(pr_number)

        if pr.is_merged():
            raise ValueError(f"The pull request #{pr_number} has already been merged and cannot be reviewed.")

        files = pr.get_files()  
        return files
    except GithubException as e:
        if e.status == 404:
            raise HTTPException(status_code=404, detail=f"Invalid pull request number #{pr_number}. PR not found in the repository.")
        else:
            raise HTTPException(status_code=500, detail=f"Error in fetching PR details: {str(e)}")
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch PR details: {str(e)}")

def clean_patch_content(patch):
    cleaned_patch = []
    for line in patch.splitlines():
        if line.startswith(('---', '+++', 'diff', '@@')):
            continue
        elif line.startswith('+') or line.startswith('-'):
            cleaned_patch.append(line[1:].strip())  
        else:
            cleaned_patch.append(line.strip())  
    return "\n".join(cleaned_patch)

def generate_code_suggestions(code_context):
    messages = f"""
    You are a code quality assistant. Please review the following Python code and provide suggestions for improvements, including:
    - Fixing any syntax or indentation errors
    - Suggesting improvements in code style, according to Python's PEP 8 guidelines
    - Identifying any security vulnerabilities or unsafe practices

    Here is the code:
    {code_context}

    Please provide specific suggestions for fixing any issues you find.
    """
    
    try:
        response = llm.predict(messages)  
        return response
    except AttributeError as e:
        raise ValueError(f"Error in generating response from Groq model: {str(e)}")

# Function to create JWT Token using PyJWT
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

# GitHub OAuth2 Flow
@app.get("/login/github")
async def github_login():
    github_oauth_url = f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&redirect_uri={GITHUB_REDIRECT_URI}"
    return {"url": github_oauth_url}

@app.get("/github/callback")
async def github_callback(code: str):
    # Exchange GitHub code for access token
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(
                "https://github.com/login/oauth/access_token",
                data={
                    "client_id": GITHUB_CLIENT_ID,
                    "client_secret": GITHUB_CLIENT_SECRET,
                    "code": code,
                    "redirect_uri": GITHUB_REDIRECT_URI,
                },
                headers={"Accept": "application/json"},
            )
        response_data = response.json()
        access_token = response_data.get("access_token")
        if access_token:
            # Create JWT for the user
            return {"access_token": create_access_token({"sub": access_token}), "token_type": "bearer"}
        else:
            raise HTTPException(status_code=400, detail="GitHub authentication failed.")
    except httpx.TimeoutException:
        raise HTTPException(status_code=408, detail="Request timed out while fetching GitHub access token.")
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Error in request: {str(e)}")

# Token-based authentication for FastAPI requests
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=403, detail="Invalid token")

@app.post("/review_pr/") 
async def review_pr(pr: PullRequest, current_user: dict = Depends(get_current_user)):
    try:
        files = await fetch_pr_details(pr.repository_url, pr.pr_number)
        code_example = "\n".join([clean_patch_content(file.patch) for file in files if file.filename.endswith('.py')])
        ai_suggestions = generate_code_suggestions(code_example)
        feedback = f"### AI Suggestions (Linting Issues and Code Improvements):\n{ai_suggestions}"
        return {"feedback": feedback}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to review pull request: {str(e)}")