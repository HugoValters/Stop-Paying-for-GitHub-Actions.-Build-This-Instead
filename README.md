# 🚀 GitHub to GitLab: Automated CI/CD Migration & Self-Hosted Runner

[![YouTube Video](https://img.shields.io/badge/YouTube-Watch%20Tutorial-red?style=for-the-badge&logo=youtube)]([https://youtu.be/0eFLstXc7b0])
[![Medium Article](https://img.shields.io/badge/Medium-Read%20Article-black?style=for-the-badge&logo=medium)]([https://blog.valters.eu/stop-paying-for-github-actions-the-ultimate-gitlab-self-hosted-runner-migration-guide-d44077471075])

## 📌 The Problem
Relying entirely on a single platform for your CI/CD pipelines is a trap, especially with unpredictable pricing changes for self-hosted runners. This repository contains the resources and scripts needed to migrate your CI/CD infrastructure from GitHub to a fully self-hosted **GitLab Runner** environment, achieving complete redundancy and zero vendor lock-in.

## 📺 Full Video Tutorial
For a complete, step-by-step walkthrough, watch the setup process on my YouTube channel:  
👉 **[Stop Paying for GitHub Actions. Build This Instead.]([https://youtu.be/0eFLstXc7b0])**

---

## ⚡ Infrastructure Sponsor
Speed matters for CI/CD tasks (`npm install`, compilation, etc.). The infrastructure for this project is built on **Zone.eu**. They provide blazing-fast, European-based VPS instances with unmetered bandwidth and NVMe storage.

If you want to build your own HomeLab or CI/CD servers, check them out:  
🔗 **[Get your Zone.eu VPS here]([https://www.zone.eu/cloudserver-vps/?utm_source=youtube&utm_medium=referral&utm_campaign=valters])**

---

## 🛠️ Step 1: Install GitLab Runner

SSH into your VPS as the root user and install the GitLab Runner package:

```bash
# Become root
sudo su

# Download the GitLab repository script
curl -L "[https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh](https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh)" | sudo bash

# Install the runner
sudo apt-get install gitlab-runner
```

## ⚙️ Step 2: Register Runner & Install Docker

Register the runner with your GitLab instance using the token provided in your GitLab CI/CD settings. When prompted, select `docker` as the executor and `docker:stable` as the default image.

```bash
gitlab-runner register
```

Since we are using the Docker executor, install Docker and grant the runner permissions:

```bash
# Install Docker
sudo apt install docker.io

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add gitlab-runner user to the docker group
sudo usermod -aG docker gitlab-runner
```

## 🐍 Step 3: The Python Automation Sync Script

To automate the synchronization of your repositories from GitHub to GitLab, we use a custom Python script. 

### Prerequisites
Install Python and a virtual environment on your server:

```bash
sudo apt-get update
sudo apt install python3 python3-pip python3-venv
```

### Setup & Usage
1. Generate a **Personal Access Token** in both GitHub and GitLab.
2. Clone this repository or copy the `git.py` script to your server.
3. Replace the placeholder token variables inside the script with your actual API tokens.
4. Execute the script manually or set up a Cron job for automated daily syncing.

```bash
# Example execution
python3 git.py
```

*(Note: Never hardcode or commit your actual API tokens to public repositories! Use environment variables or an `.env` file in production).*

---

## 🤝 Connect with Me
If you are an Enterprise IT Architect, DevOps Engineer, or HomeLab enthusiast, let's connect!
* 🎥 **YouTube:** [Valters IT([https://youtube.com/@hugovalters])
* 𝕏 **X (Twitter):** [@hugovalters]([https://x.com/hugovalters])
* 📝 **Blog:** [https://blog.valters.eu]([https://blog.valters.eu)

**Keep building, and stay redundant! 🛠️**m
