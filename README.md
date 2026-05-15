# \# 🔍 NicheSearch – Curated Niche Search Engine

# 

# A \*\*DevSecOps capstone project\*\* that delivers a secure, cost‑optimised, and beautifully minimalistic search engine for curated tech \& knowledge articles. Built with \*\*Django\*\* on \*\*AWS\*\*, featuring automated content ingestion, user bookmarks, profile management, and a relevance‑based page ranking algorithm.

# 

# !\[License](https://img.shields.io/badge/license-MIT-blue)

# !\[Django](https://img.shields.io/badge/Django-4.2-green)

# !\[AWS](https://img.shields.io/badge/AWS-Free%20Tier-orange)

# 

# \---

# 

# \## ✨ Features

# 

# \- \*\*🔎 Smart Search\*\* – Dynamic relevance scoring (term frequency, exact title matches, static boosts).

# \- \*\*📌 Bookmark Manager\*\* – Create, view, and delete saved links.

# \- \*\*👤 User Profiles\*\* – Update username, email, and upload a profile picture (stored on \*\*AWS S3\*\*).

# \- \*\*📰 Curated Content\*\* – Articles from Hacker News, Dev.to, Ars Technica, and \*\*1500+ Wikipedia summaries\*\* across 25 topics.

# \- \*\*📊 Django Admin\*\* – Manage users, results, and view analytics.

# \- \*\*🐳 Dockerised\*\* – Consistent environment with Gunicorn + Nginx.

# \- \*\*🔒 Enterprise Security\*\* – CSRF, XSS, HSTS, rate‑limiting, least‑privilege IAM roles, SSH hardening, UFW.

# \- \*\*📈 Monitoring\*\* – CloudWatch logs \& CPU alarms.

# \- \*\*🔄 CI/CD\*\* – GitHub Actions pipeline automates deployment to AWS EC2.

# \- \*\*💵 Cost‑Optimised\*\* – Entirely within AWS Free Tier (t2.micro, t3.micro RDS, S3, 20 GB EBS).

# 

# \---

# 

# \## 🏗️ Architecture

# 

# \### High‑Level Diagram

# 

# ```

# &#x20;                       ┌──────────────────────────────────────────────┐

# &#x20;                       │              GitHub Repository              │

# &#x20;                       │    (source code + CI/CD workflows)           │

# &#x20;                       └──────────────┬───────────────────────────────┘

# &#x20;                                      │  git push

# &#x20;                                      ▼

# &#x20;                        ┌─────────────────────────────┐

# &#x20;                        │    GitHub Actions Runner     │

# &#x20;                        │  (builds Docker image,        │

# &#x20;                        │   pushes via SCP through     │

# &#x20;                        │   bastion to private EC2)     │

# &#x20;                        └──────────────┬──────────────┘

# &#x20;                                       │ SSH via Bastion

# &#x20;                                       ▼

# ┌─────────────────────────────────────────────────────────────────────┐

# │                          AWS Cloud (us-east-1)                      │

# │                                                                      │

# │  ┌─────────────────────────────────────────────────────────────┐    │

# │  │                     VPC (10.0.0.0/16)                       │    │

# │  │                                                              │    │

# │  │   ┌─────────────────────┐      ┌───────────────────────┐    │    │

# │  │   │  Public Subnets     │      │  Private Subnets      │    │    │

# │  │   │  (10.0.1.0/24,      │      │                       │    │    │

# │  │   │   10.0.2.0/24)       │      │  App Subnets:         │    │    │

# │  │   │                     │      │  (10.0.10.0/24,       │    │    │

# │  │   │  ┌───────────────┐  │      │   10.0.11.0/24)       │    │    │

# │  │   │  │  NAT Instance │  │      │                       │    │    │

# │  │   │  │  (t2.micro)   │  │      │  ┌────────────────┐  │    │    │

# │  │   │  └──────┬────────┘  │      │  │  EC2 Instance  │  │    │    │

# │  │   │         │            │      │  │  (t2.micro)    │  │    │    │

# │  │   │  ┌──────▼────────┐  │      │  │  Ubuntu 22.04  │  │    │    │

# │  │   │  │ ALB (Public) │  │      │  │  Docker:        │  │    │    │

# │  │   │  │ HTTP/HTTPS   │  │      │  │  - Gunicorn     │  │    │    │

# │  │   │  └──────┬────────┘  │      │  │  - Django App   │  │    │    │

# │  │   │         │            │      │  │  Nginx reverse  │  │    │    │

# │  │   └─────────┼────────────┘      │  │  proxy          │  │    │    │

# │  │             │                    │  └───────▲────────┘  │    │    │

# │  │             │                    │          │            │    │    │

# │  │             └────────────────────┼──────────┘            │    │    │

# │  │                                 │                       │    │    │

# │  │                        ┌───────▼────────┐               │    │    │

# │  │                        │  RDS PostgreSQL│               │    │    │

# │  │                        │  (db.t3.micro) │               │    │    │

# │  │                        │  Private Subnet│               │    │    │

# │  │                        └────────────────┘               │    │    │

# │  │                                                          │    │    │

# │  │                        ┌────────────────┐               │    │    │

# │  │                        │   S3 Bucket    │               │    │    │

# │  │                        │ (media files)  │               │    │    │

# │  │                        └────────────────┘               │    │    │

# │  └──────────────────────────────────────────────────────────┘    │

# │                                                                    │

# │  ┌──────────────────────────────────────────────────────────┐    │

# │  │           CloudWatch Logs \& Alarms                       │    │

# │  │  - Application logs (via CloudWatch Agent)                │    │

# │  │  - EC2 CPU alarm (≥80%)                                  │    │

# │  └──────────────────────────────────────────────────────────┘    │

# └─────────────────────────────────────────────────────────────────────┘

# 

# &#x20;           │ Local Development Machine (Windows/Linux/macOS)

# &#x20;           │

# &#x20;           ├─ Django Management Command (run\_scraper.py)

# &#x20;           │   Uses BeautifulSoup + requests → scrapes HN, Dev.to, Ars Technica

# &#x20;           │   Saves directly to RDS (or local SQLite, then dump/load)

# &#x20;           │

# &#x20;           └─ Wikipedia Bulk Import (populate\_wikipedia.py)

# &#x20;               Uses wikipedia-api → fetches 1500+ summaries → stores in DB

# ```

# 

# \### How It Works

# 

# \- \*\*Local Scraping\*\* populates the cloud database with 1500+ articles before deployment.

# \- \*\*User Requests\*\* arrive at the public ALB, are forwarded to the private EC2 instance, Nginx proxies to Gunicorn/Django, which queries RDS and returns ranked results.

# \- \*\*CI/CD\*\* builds the Docker image on push, transfers it via the bastion (NAT), and redeploys the container.

# \- \*\*Security Groups\*\* enforce least‑privilege networking; IAM roles grant S3 and CloudWatch access without secrets.

# \- \*\*Backups\*\* run nightly via cron; logs are shipped to CloudWatch.

# 

# \---

# 

# \## 🛠️ Tech Stack

# 

# | Category            | Technology                                                                 |

# |---------------------|----------------------------------------------------------------------------|

# | Backend             | Django 4.2, Python 3.11                                                    |

# | Web Server          | Gunicorn (WSGI)                                                            |

# | Reverse Proxy       | Nginx                                                                      |

# | Database            | PostgreSQL (AWS RDS) / SQLite (local dev)                                  |

# | Storage             | AWS S3 (django‑storages + boto3)                                           |

# | Frontend            | Tailwind CSS (CDN), minimal HTML5 templates                                |

# | Scraping            | BeautifulSoup4, Requests, wikipedia‑api                                    |

# | Security            | django‑ratelimit, Django security middlewares, HSTS, SSH hardening, UFW    |

# | Containerisation    | Docker                                                                     |

# | Infrastructure      | Terraform (AWS VPC, EC2, RDS, S3, ALB, IAM)                               |

# | CI/CD               | GitHub Actions                                                             |

# | Monitoring          | AWS CloudWatch (logs, CPU alarms)                                          |

# | Backup              | Shell script + cron (pg\_dump, s3 sync)                                     |

# 

# \---

# 

# \## 📁 Project Structure

# 

# ```

# niche\_search\_project/

# ├── niche\_search/                 # Django project settings

# ├── search/                       # Main application

# │   ├── management/commands/      # run\_scraper.py, populate\_wikipedia.py

# │   ├── templates/                # Tailwind HTML templates

# │   ├── models.py                 # SearchResult, UserBookmark, UserProfile

# │   ├── views.py                  # Search, login, bookmarks, profile

# │   ├── urls.py

# │   ├── ranking.py                # Relevance scoring algorithm

# │   ├── signals.py                # Auto-create UserProfile

# │   └── admin.py                  # Admin dashboard registration

# ├── Dockerfile

# ├── requirements.txt

# ├── manage.py

# ├── .env.example                  # Template for environment variables

# ├── terraform/                    # Infrastructure as Code

# │   ├── main.tf

# │   ├── variables.tf

# │   ├── outputs.tf

# │   └── terraform.tfvars.example

# ├── .github/workflows/deploy.yml  # CI/CD pipeline

# ├── backup.sh                     # Database \& media backup script

# ├── logs/                         # Rotating Django logs

# └── cache/                        # File‑based cache (optional)

# ```

# 

# \---

# 

# \## 🚀 Getting Started

# 

# \### Prerequisites

# 

# \- \*\*Python 3.11+\*\* \& \*\*pip\*\*

# \- \*\*Git\*\*

# \- \*\*Docker\*\* (for building and running containers)

# \- \*\*AWS Account\*\* (free tier eligible) \& configured AWS CLI (optional)

# \- \*\*Terraform\*\* (if provisioning infrastructure)

# 

# \### 1. Clone the Repository

# 

# ```bash

# git clone https://github.com/your-username/niche\_search.git

# cd niche\_search\_project

# ```

# 

# \### 2. Local Development Setup

# 

# \#### a) Virtual environment \& dependencies

# 

# ```bash

# python -m venv venv

# source venv/bin/activate      # Linux/macOS

# venv\\Scripts\\activate        # Windows

# 

# pip install -r requirements.txt

# ```

# 

# \#### b) Environment variables

# 

# Copy the example file and adjust as needed:

# 

# ```bash

# cp .env.example .env

# ```

# 

# For local testing with \*\*SQLite\*\*, set:

# 

# ```env

# DJANGO\_SECRET\_KEY=your-secret-key

# DJANGO\_DEBUG=True

# DJANGO\_ALLOWED\_HOSTS=localhost,127.0.0.1

# USE\_SQLITE=True

# ```

# 

# (If you get django‑ratelimit errors, add `SILENCED\_SYSTEM\_CHECKS = \['django\_ratelimit.E003','django\_ratelimit.W001']` to `settings.py`.)

# 

# \#### c) Apply migrations \& create superuser

# 

# ```bash

# python manage.py migrate

# python manage.py createsuperuser

# ```

# 

# \#### d) Populate the database (Wikipedia articles)

# 

# ```bash

# python manage.py populate\_wikipedia

# ```

# 

# This fetches \~1500 summaries via the official Wikipedia API and stores them locally.

# 

# \#### e) Run the development server

# 

# ```bash

# python manage.py runserver

# ```

# 

# Visit \*\*http://127.0.0.1:8000\*\* – you should see the search page.

# 

# \### 3. Cloud Deployment (AWS)

# 

# \#### a) Provision infrastructure with Terraform

# 

# ```bash

# cd terraform

# terraform init

# terraform apply -var="db\_password=YourStrongPassword" -var="key\_name=your-ec2-key-pair"

# ```

# 

# Note the outputs: `alb\_dns`, `rds\_endpoint`, `s3\_bucket`.

# 

# \#### b) Configure the production `.env` on the EC2

# 

# SSH into the EC2 instance (via the bastion/NAT instance) and create `/opt/niche-search/.env` with:

# 

# ```env

# DJANGO\_SECRET\_KEY=...

# DJANGO\_DEBUG=False

# DJANGO\_ALLOWED\_HOSTS=\*

# RDS\_DB\_NAME=niche\_search

# RDS\_USERNAME=db\_admin

# RDS\_PASSWORD=YourStrongPassword

# RDS\_HOSTNAME=<rds-endpoint>

# RDS\_PORT=5432

# S3\_BUCKET\_NAME=<bucket-name>

# AWS\_REGION=us-east-1

# ```

# 

# \#### c) Build \& run the Docker container

# 

# ```bash

# cd /opt/niche-search

# docker build -t niche-search .

# docker run -d --name niche-search --restart unless-stopped \\

# &#x20;   -p 127.0.0.1:8000:8000 \\

# &#x20;   --env-file .env \\

# &#x20;   -v /opt/niche-search/logs:/app/logs \\

# &#x20;   niche-search

# ```

# 

# \#### d) Set up Nginx \& firewall

# 

# Nginx config (`/etc/nginx/sites-available/niche\_search`):

# 

# ```nginx

# server {

# &#x20;   listen 80;

# &#x20;   server\_name \_;

# 

# &#x20;   client\_max\_body\_size 10M;

# 

# &#x20;   location / {

# &#x20;       proxy\_pass http://127.0.0.1:8000;

# &#x20;       proxy\_set\_header Host $host;

# &#x20;       proxy\_set\_header X-Real-IP $remote\_addr;

# &#x20;       proxy\_set\_header X-Forwarded-For $proxy\_add\_x\_forwarded\_for;

# &#x20;       proxy\_set\_header X-Forwarded-Proto $scheme;

# &#x20;   }

# 

# &#x20;   location /static/ {

# &#x20;       alias /opt/niche-search/staticfiles/;

# &#x20;   }

# }

# ```

# 

# Enable site and reload Nginx:

# 

# ```bash

# sudo ln -s /etc/nginx/sites-available/niche\_search /etc/nginx/sites-enabled/

# sudo rm /etc/nginx/sites-enabled/default

# sudo nginx -t \&\& sudo systemctl restart nginx

# ```

# 

# Harden SSH (`/etc/ssh/sshd\_config`):

# 

# ```

# PermitRootLogin no

# PasswordAuthentication no

# PubkeyAuthentication yes

# AllowUsers ubuntu

# ```

# 

# Restart SSH: `sudo systemctl restart sshd`.

# 

# Enable UFW:

# 

# ```bash

# sudo ufw default deny incoming

# sudo ufw default allow outgoing

# sudo ufw allow from 10.0.1.0/24 to any port 22 proto tcp

# sudo ufw allow from 10.0.0.0/16 to any port 80 proto tcp

# sudo ufw enable

# ```

# 

# \#### e) Migrate \& load data on the cloud database

# 

# ```bash

# docker exec -it niche-search python manage.py migrate

# docker exec -it niche-search python manage.py createsuperuser

# \# Option A: re-run the Wikipedia command (skips existing)

# docker exec -it niche-search python manage.py populate\_wikipedia

# \# Option B: dump from local and load (see documentation)

# ```

# 

# \### 4. CI/CD with GitHub Actions

# 

# Add the following secrets to your GitHub repository:

# 

# \- `SSH\_KEY` – private key for EC2

# \- `BASTION\_IP` – public IP of the NAT instance

# \- `APP\_PRIVATE\_IP` – private IP of the Django EC2

# 

# Push to `main` – the pipeline builds the Docker image, transfers it via SCP, and restarts the container.

# 

# \### 5. Backup \& Monitoring

# 

# \- \*\*Backup\*\*: The script `/opt/backup.sh` runs nightly via cron, dumping the database and syncing S3 media locally.

# \- \*\*CloudWatch Logs\*\*: The CloudWatch agent streams `/opt/niche-search/logs/app.log` to CloudWatch Logs.

# \- \*\*CPU Alarm\*\*: An alarm triggers if CPU > 80% for two 5‑minute periods.

# 

# \---

# 

# \## 📖 Usage

# 

# \- \*\*Search\*\*: Enter a keyword (e.g., “machine learning”) and see relevance‑ranked results.

# \- \*\*Bookmark\*\*: Log in, click “Save” on any result; view/remove bookmarks from the “📌 Bookmarks” page.

# \- \*\*Profile\*\*: Upload a profile picture, update username and email.

# \- \*\*Admin\*\*: Visit `/admin` to manage all data.

# 

# \---

# 

# \## 🧠 Page Ranking Algorithm

# 

# The custom ranking function (`search/ranking.py`) scores each result using:

# 

# \- \*\*Exact phrase match\*\* in title → +3.0

# \- \*\*Term frequency\*\* in title (×2 weight)

# \- \*\*Term frequency\*\* in description

# \- \*\*Description length penalty\*\* (log‑normalised)

# \- \*\*Static rank\*\* from `SearchResult.rank` (optional)

# 

# Results are sorted by this score, so the most relevant articles appear first.

# 

# \---

# 

# \## 🤝 Contributing

# 

# This is a capstone project, but suggestions and improvements are welcome!  

# 1\. Fork the repository  

# 2\. Create a feature branch (`git checkout -b feature/amazing-feature`)  

# 3\. Commit your changes (`git commit -m 'Add some amazing feature'`)  

# 4\. Push to the branch (`git push origin feature/amazing-feature`)  

# 5\. Open a Pull Request

# 

# \---

# 

# \## 📝 License

# 

# Distributed under the MIT License. See `LICENSE` for more information.

# 

# \---

# 

# \## 🎓 Acknowledgements

# 

# \- Django documentation

# \- Wikipedia API (wikipedia‑api)

# \- AWS Free Tier

# \- Tailwind CSS

# \- Capstone supervisors and peers

# 

# \---

# 

# \*\*Built with ❤️ by Richard Pius\*\*  

# \*DevSecOps Capstone Project – 2026\*

# ```

