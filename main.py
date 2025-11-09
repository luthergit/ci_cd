import os
import subprocess
import smtplib
import traceback

from fastapi import FastAPI, Request, BackgroundTasks
from pathlib import Path
from config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, ALERT_FROM, ALERT_TO
from email.message import EmailMessage


app = FastAPI()

def send_email(subject: str, body: str):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = ALERT_FROM
    msg['To'] = ALERT_TO
    msg.set_content(body)
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        if SMTP_USER and SMTP_PASSWORD:
            server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)

def pull_repo(project_name, clone_url):
    project_dir = Path.home()  
    # Create the directory
    project_dir.mkdir(exist_ok=True, parents=True)
    
    print(f"Project directory created: {project_dir}")

    # Change to the directory (convert Path to string)
    os.chdir(str(project_dir))
    # repo_name = os.path.basename(PULL_URL).replace('.git', '')
    repo_name = project_name

    # subprocess.run(["git", "clone", PULL_URL])
    # subprocess.run(["git", "clone", clone_url])

    # os.chdir(str(repo_name))

    p = Path(repo_name)
    if p.exists():
        os.chdir(str(p))
        subprocess.run(["git", "pull"])
    else:
        os.chdir(str(project_dir))
        subprocess.run(["git", "clone", clone_url])
        os.chdir(str(repo_name))

def build_image():
    subprocess.run(["docker", "compose", "build"])

def docker_down():
    subprocess.run(["docker", "compose", "down"])

def redeploy():
    subprocess.run(["docker", "compose", "up", "-d"])

def run_pipeline(repo_name:str, clone_url: str):
    try:
        pull_repo(repo_name, clone_url)
        build_image()
        docker_down()
        redeploy()

    except Exception:
        error = traceback.format_exc()
        send_email(
            subject=f"Error in CI/CD pipeline for {repo_name}",
            body=f"Repository: {repo_name}\nClone URL: {clone_url}\n\nTraceback:\n{error}"
        )

@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):

    payload = await request.json()
    repo_name = payload['repository']['name']
    clone_url = payload['repository']['clone_url']
    background_tasks.add_task(run_pipeline, repo_name, clone_url)

    return {"message": "Webhook received and pipeline scheduled"}

@app.get("/")
def home():
    return {"message": "Welcome to the CI/CD server"}