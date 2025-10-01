from fastapi import FastAPI, Request
from config import PULL_URL
from pathlib import Path
import os
import subprocess


app = FastAPI()


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

@app.post("/webhook")
async def webhook(request: Request):

    payload = await request.json()
    repo_name = payload['repository']['name']
    clone_url = payload['repository']['clone_url']
    
    pull_repo(repo_name, clone_url)
    build_image()
    docker_down()
    redeploy()
    return {"message": "Webhook received"}

@app.get("/")
def home():
    return {"message": "Welcome to the CI/CD server"}