# Generative AI Code Review and Assistance Bot

## Overview

This project implements a **Generative AI-powered Code Review Bot** that integrates with GitHub repositories. The bot reviews pull requests (PRs) and provides detailed feedback on code quality, suggesting improvements based on Python’s PEP8 guidelines, identifying potential security vulnerabilities, and offering overall code optimizations. 

The bot leverages GitHub’s API for accessing PRs, **LangChain Groq** for AI-based code reviews, and **FastAPI** for building the backend service.

---

## Features

- **GitHub OAuth2 Integration**: Secure user authentication using GitHub OAuth2 for accessing repositories and PRs.
- **Pull Request Review**: The bot fetches details of a PR and reviews Python code for style and security improvements.
- **AI-Generated Feedback**: Provides suggestions to improve code based on PEP8 guidelines and identifies security vulnerabilities.
- **JWT Authentication**: Uses JWT tokens to manage user sessions securely.
- **Error Handling**: Detailed error handling for various cases, including API failures and timeouts.

---

## Technologies

- **FastAPI**: Backend web framework.
- **GitHub API**: For interacting with GitHub repositories and fetching PR data.
- **OAuth2**: For secure user authentication with GitHub.
- **JWT**: For session management and token-based authentication.
- **LangChain Groq**: AI model used to generate code suggestions.
- **Python**: Backend logic and API development.
- **httpx**: For handling HTTP requests asynchronously.
- **dotenv**: For managing environment variables.

---

## Setup

### Prerequisites

Before running the project, make sure you have the following:

1. **Python 3.8+** installed on your system.
2. **GitHub OAuth App Credentials**:
    - GitHub **Client ID** and **Client Secret** from your GitHub OAuth application.
    - GitHub **Personal Access Token** to authenticate API requests.

3. **Environment Variables**:
    - `GITHUB_CLIENT_ID`
    - `GITHUB_CLIENT_SECRET`
    - `GITHUB_REDIRECT_URI`
    - `GITHUB_TOKEN` (Personal Access Token for accessing repositories)
    - `JWT_SECRET_KEY` (Secret key for JWT token encoding)
    - `GROQ_API_KEY` (API key for interacting with the LangChain Groq model)

### Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/your-username/Generative-AI-Code-Review-and-Assistance-Bot.git
   cd Generative-AI-Code-Review-and-Assistance-Bot

2. **Install Dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

3. **Set up Environment Variables**:
Create a .env file in the root of the project and add the following:
- GITHUB_CLIENT_ID=<your-client-id>
- GITHUB_CLIENT_SECRET=<your-client-secret>
- GITHUB_REDIRECT_URI=<your-redirect-uri>
- GITHUB_TOKEN=<your-github-token>
- JWT_SECRET_KEY=<your-jwt-secret-key>
- GROQ_API_KEY=<your-groq-api-key>

4. **Run the FastAPI Server**:

    ```bash
    uvicorn main:app --reload
    ```

5. **Run the streamlit**:

    ```bash
    uvicorn main:app --reload
    ```

### Setting Up GitHub OAuth

To allow the application to authenticate users via GitHub, you'll need to set up an OAuth application on GitHub.

#### Steps for creating OAuth credentials:
1. Go to GitHub and visit GitHub Developer Settings.

2. Create a New OAuth App:
   - Name: Choose a name for your app (e.g., "Generative AI Code Review").
   - Homepage URL: Provide a homepage URL for your app. This can be your GitHub repo or a project website.
   - Authorization callback URL: This is the URL where GitHub will redirect after successful authentication.    should be your application’s callback URL (http://localhost:8000/github/callback or your deployed URL).
3. Save the application. After creating it, GitHub will provide a Client ID and Client Secret. These credentials will be used to set up the OAuth flow.

4. Update your .env file:
    - Add the GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, and GITHUB_REDIRECT_URI to your .env file.

### Web App Functionality
Once your FastAPI server is running, the bot will be able to handle requests for code reviews through the following workflow:

1. Login with GitHub:
    - Users are redirected to GitHub's OAuth2 login page by visiting /login/github. After a successful login, GitHub will redirect to your app's /github/callback endpoint, where the OAuth flow completes and the user is authenticated.
2. Review a Pull Request:
    - Once logged in, users can submit pull requests for review by using the /review_pr/ endpoint, sending the repository URL and PR number as the payload.
    - The bot will fetch the PR details, process the code changes, and return AI-generated code suggestions based on the code style and security guidelines.

3. UI Workflow Example:
Login Page:
![Screenshot 2025-02-16 095421](https://github.com/user-attachments/assets/59da7bf4-fb7d-4ad7-9cda-65855e144118)

Here is an example screenshot of the login page with GitHub OAuth integration.
![Screenshot 2025-02-16 091808](https://github.com/user-attachments/assets/491318d0-005e-4602-be91-944a3a5e7e49)

![Screenshot 2025-02-16 091920](https://github.com/user-attachments/assets/d9a00d7d-d709-4284-82c4-917c94ddc0c7)

PR Review Page:
![Screenshot 2025-02-16 092011](https://github.com/user-attachments/assets/f3ae2e16-7f11-467b-a12d-1447151d76f2)

![Screenshot 2025-02-16 093917](https://github.com/user-attachments/assets/d9ddd98d-2d4c-43f4-8b42-0c80c81010f6)

![Screenshot 2025-02-16 093926](https://github.com/user-attachments/assets/fa0d18d0-0e53-4e4c-b3b2-b1d0e46bd99f)

![Screenshot 2025-02-16 093946](https://github.com/user-attachments/assets/1ca353e1-aba5-4d17-960a-5613b74440f0)

