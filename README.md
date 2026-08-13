# 🚀 PyPulse

<div align="center">

### A tiny Flask app with a *real* Jenkins CI/CD pipeline behind it

[![Live Demo](https://img.shields.io/badge/🌐_Live_Demo-pypulse--pi.vercel.app-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://pypulse-pi.vercel.app)
[![Python](https://img.shields.io/badge/Python-3.14-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.3-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Jenkins](https://img.shields.io/badge/Jenkins-CI%2FCD-D24939?style=for-the-badge&logo=jenkins&logoColor=white)](https://www.jenkins.io/)
[![AWS](https://img.shields.io/badge/AWS-EC2-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white)](https://aws.amazon.com/ec2/)

[![License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen?style=flat-square&logo=pytest)](test_app.py)
[![Deploy](https://img.shields.io/badge/deploy-automated-success?style=flat-square&logo=jenkins)](Jenkinsfile)
[![Uptime](https://img.shields.io/badge/managed_by-systemd-orange?style=flat-square&logo=linux)](pypulse.service)

</div>

---

## ✨ What is this?

**PyPulse** is a deliberately small Flask app — the point was never the app itself, it's the **full CI/CD pipeline** wrapped around it:

```
git push  →  GitHub Webhook  →  Jenkins (Build → Test → Deploy)  →  Live on AWS EC2, managed by systemd
```

Every push to `main` is automatically built, tested, and deployed — with **zero manual steps**. A permanent demo is also mirrored on Vercel, since the EC2 instance runs on an AWS free trial and won't live forever. 🌱

🔗 **Try it live:** [pypulse-pi.vercel.app](https://pypulse-pi.vercel.app) · [/health](https://pypulse-pi.vercel.app/health)

---

## 🏗️ Architecture

```mermaid
flowchart TD
    Dev["👨‍💻 Developer<br/>git push"] --> GH["📦 GitHub<br/>IrfanPasha05/pypulse"]
    GH -- "🔔 webhook" --> Jenkins

    subgraph Jenkins["⚙️ Jenkins Pipeline (on EC2)"]
        direction LR
        Build["🔨 Build<br/>venv + pip install"] --> Test["✅ Test<br/>pytest"] --> Deploy["🚀 Deploy<br/>SSH + systemctl restart"]
    end

    Deploy -- "ssh" --> EC2

    subgraph EC2["☁️ AWS EC2 (Ubuntu 22.04)"]
        direction LR
        Systemd["🔁 systemd<br/>pypulse.service"] --> Gunicorn["🦄 gunicorn"] --> Flask["🌶️ Flask app<br/>:5000"]
    end

    GH -. "also deploys to" .-> Vercel["▲ Vercel<br/>permanent demo"]

    style Dev fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    style GH fill:#f5f5f5,stroke:#24292e,stroke-width:2px
    style Jenkins fill:#fff3e0,stroke:#d24939,stroke-width:2px
    style EC2 fill:#fff8e1,stroke:#ff9900,stroke-width:2px
    style Vercel fill:#f3e5f5,stroke:#6b21a8,stroke-width:2px
    style Build fill:#e8f5e9,stroke:#2e7d32
    style Test fill:#e8f5e9,stroke:#2e7d32
    style Deploy fill:#e8f5e9,stroke:#2e7d32
```

---

## 🧰 Tech Stack

| Layer | Tool | Purpose |
|---|---|---|
| 🌶️ App | Flask + gunicorn | Web app + production WSGI server |
| ✅ Testing | pytest | Automated route tests, gate before deploy |
| ⚙️ CI/CD | Jenkins (self-hosted on EC2) | Build → Test → Deploy automation |
| 📦 Source control | GitHub | Code + webhook trigger source |
| 🔁 Process manager | systemd | Keeps the app alive across crashes/reboots |
| ☁️ Infrastructure | AWS EC2 (Ubuntu 22.04) | Where Jenkins *and* the app run |
| ▲ Permanent demo | Vercel | Serverless mirror, independent of EC2 |

---

## 📸 Screenshots

<table>
<tr>
<td width="50%">

**Jenkins Dashboard**
![Jenkins Dashboard](screenshots/01-jenkins-dashboard.png)
*Publicly reachable on the EC2 public IP — build history for the `pypulse` job.*

</td>
<td width="50%">

**systemd Managing the App**
![systemd status](screenshots/02-systemd-status.png)
*`pypulse.service` — active, auto-restarting, survives reboots.*

</td>
</tr>
<tr>
<td width="50%">

**App Live on EC2**
![App live response](screenshots/03-app-live-response.png)
*JSON response served by gunicorn, deployed by Jenkins.*

</td>
<td width="50%">

**GitHub Webhook Configured**
![Webhook created](screenshots/04-github-webhook-created.png)
*Push events on `main` notify Jenkins directly.*

</td>
</tr>
<tr>
<td width="50%">

**Webhook Delivery — 200 OK**
![Webhook ping 200](screenshots/05-webhook-ping-200.png)
*GitHub successfully reaching Jenkins on the EC2 public IP.*

</td>
<td width="50%">

**Auto-Triggered Build**
![Auto triggered build](screenshots/06-auto-triggered-build.png)
*Build #8 — started automatically on push, no manual click.*

</td>
</tr>
<tr>
<td width="50%">

**Vercel — Live Home Route**
![Vercel home](screenshots/07-vercel-live-home.png)
*Permanent HTTPS demo, independent of EC2.*

</td>
<td width="50%">

**Vercel — Health Check**
![Vercel health](screenshots/08-vercel-live-health.png)
*`/health` confirming the serverless deploy works end to end.*

</td>
</tr>
</table>

---

## ⚙️ The Pipeline in Detail

### 🔨 Build
```groovy
stage('Build') {
    steps {
        sh '''
            python3 -m venv venv
            . venv/bin/activate
            pip install -r requirements.txt
        '''
    }
}
```
Runs on the Jenkins host. Fails fast if a dependency is broken — before wasting time on Test or Deploy.

### ✅ Test
```groovy
stage('Test') {
    steps {
        sh '''
            . venv/bin/activate
            pytest
        '''
    }
}
```
Runs `test_app.py` against `/` and `/health`. Broken code never reaches Deploy.

### 🚀 Deploy
```groovy
stage('Deploy') {
    steps {
        sshagent(credentials: ['pypulse-ec2-ssh']) {
            sh '''
                set -e
                timeout 60 ssh -o StrictHostKeyChecking=no ${EC2_USER}@${EC2_IP} "
                    set -e
                    if [ ! -d ${APP_DIR} ]; then
                        git clone https://github.com/IrfanPasha05/pypulse.git ${APP_DIR}
                    fi
                    cd ${APP_DIR}
                    git pull origin main
                    source venv/bin/activate
                    pip install -r requirements.txt
                    sudo systemctl restart pypulse
                "
            '''
        }
    }
}
```
SSHes into EC2 via a Jenkins-stored credential, pulls latest code, and hands the process off to **systemd** — no fragile `nohup`/background-process juggling.

---

## 🐛 Real Bugs Hit Along the Way

> Because a pipeline that "just worked" wouldn't have taught me anything.

| # | Bug | Root Cause | Fix |
|---|---|---|---|
| 1 | `ensurepip is not available` | Jenkins host missing `python3-venv` | `sudo apt install python3.14-venv` |
| 2 | `No such DSL method 'sshagent'` | SSH Agent plugin not installed | Installed plugin + restarted Jenkins |
| 3 | `Could not find specified credentials` | Credential ID referenced but never created | Added SSH credential in Jenkins store |
| 4 | Pipeline "succeeds" but app unreachable | `git pull` assumed repo already existed on server; no `set -e` to catch the silent failure | Self-healing clone-or-pull + `set -e` |
| 5 | Deploy hangs forever, no error | Backgrounded process (`nohup ... &`) chained with `&&` kept the SSH session open | Separated commands, `setsid`, `timeout 60` — then replaced entirely with **systemd** |

---

## 🗺️ Roadmap

- [ ] Containerize with Docker, deploy via Jenkins to ECR/ECS
- [ ] Add a staging environment before production deploy
- [ ] Basic monitoring/alerting on the systemd service
- [ ] Move Jenkins off a free-tier EC2 box onto something persistent

---

## 📄 License

MIT — do whatever you want with this, just don't blame me for the SSH hangs. 😄

---

<div align="center">

**Built while learning DevOps, one broken pipeline at a time.** 🛠️

[Live Demo](https://pypulse-pi.vercel.app) · [Report an Issue](../../issues)

</div>
