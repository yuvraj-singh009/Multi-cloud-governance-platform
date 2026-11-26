# Cloud Governance & Cost Optimization Platform

A multi-tenant AWS cloud governance platform that helps users discover cloud infrastructure, review security and compliance risks, and identify resources that may be creating avoidable monthly costs. Users connect an AWS account through a cross-account IAM role; the platform assumes that role with a unique External ID and performs read-only resource discovery.

> **Live application:** [Open the Cloud Governance Platform](https://cloud-governance-platform.vercel.app)  
> **Repository:** [cloud-governance-platform](https://github.com/yuvraj-singh009/cloud-governance-platform)

---

## 1. About the Project

Cloud Governance & Cost Optimization Platform provides a central dashboard for AWS resource inventory, scan history, security findings, and estimated savings.

A user signs in, registers an AWS account, and supplies its 12-digit account ID and preferred starting region. The backend generates a unique External ID. The user creates a read-only IAM role in their AWS account that trusts the platform's dedicated IAM principal and requires that External ID. After the user submits the role ARN, the backend calls AWS STS to assume the role and confirms that the returned AWS account ID matches the account they registered.

Once verified, the user can start a scan. The scanner discovers enabled AWS regions and collects EC2 instances, EBS volumes, RDS database instances, security groups, Elastic IP addresses, and S3 buckets. Resource snapshots and scan history are stored in Supabase. After a successful scan, the Flask auditor evaluates the snapshots against the implemented governance rules and stores policy findings and configurable cost-waste estimates. The React dashboard displays the inventory, resource distribution, scan history, violations, and potential monthly savings.

### What the application currently checks

- **EC2:** resource inventory and missing mandatory tags.
- **EBS:** unattached volumes.
- **Security Groups:** rules that expose SSH to the internet.
- **Elastic IPs:** unassociated addresses.
- **S3:** bucket configuration checks for public exposure.
- **RDS:** publicly accessible database instances.

Cost values are configurable estimates (currently INR-based defaults), not a replacement for AWS Cost Explorer or an actual AWS bill.

### End-to-end workflow

```text
User
 |
 v
React dashboard (Vercel)
 |  Supabase Auth session / Bearer token
 v
FastAPI Scanner API (Render)
 |
 |-- Create AWS connection
 |     |-- Generate External ID
 |     |-- Store encrypted External ID in Supabase
 |     |-- Verify submitted customer Role ARN with AWS STS
 |
 |-- Start scan for a verified account
       |
       |-- Platform IAM principal calls sts:AssumeRole
       |      using customer Role ARN + External ID
       |
       |-- Assumed customer-role session (temporary credentials)
       |      |-- Discover enabled regions
       |      |-- Scan EC2, EBS, RDS, Security Groups, Elastic IPs
       |      |-- Scan S3 buckets
       |
       v
Supabase PostgreSQL
 |-- cloud_accounts
 |-- scan_jobs
 |-- resource_snapshots
 |-- policy_violations
 |-- cost_estimates
 |
 v
Flask Auditor API (Render)
 |-- Evaluate governance rules
 |-- Calculate configurable estimated waste
 |-- Save findings and estimates in Supabase
 |
 v
React dashboard displays results
```

A scan with collection errors is recorded as failed/partial in the scan history while successfully collected resource snapshots may still be saved. The auditor is triggered automatically only when the scan completes without collection errors.

---

## 2. Technology Stack and Where It Is Used

This section is intended as a codebase recall guide: technology, purpose, and the main location where it appears.

| Technology | Purpose in this project | Main location |
|---|---|---|
| **React 19** | Builds the single-page dashboard and its forms, tables, and views. | `frontend/src/`, especially `frontend/src/pages/Dashboard.jsx` |
| **JavaScript (ES modules)** | Frontend application logic and API calls. | `frontend/src/` |
| **Vite** | Frontend development server and production build tool. | `frontend/vite.config.js`, `frontend/package.json` |
| **React Router** | Client-side page navigation. | `frontend/package.json` and frontend routing code |
| **Recharts** | Resource distribution chart. | `frontend/src/pages/Dashboard.jsx` |
| **Lucide React** | Dashboard icons. | `frontend/package.json` and frontend UI components |
| **Axios** | Sends authenticated HTTP requests from React to FastAPI. | `frontend/src/services/api.js` |
| **Supabase JavaScript SDK** | Frontend authentication and authenticated reads of dashboard data. | `frontend/src/services/`, `frontend/package.json` |
| **Python 3.12** | Runtime for scanner and auditor services. | `scanner-service/`, `auditor-service/`, Dockerfiles |
| **FastAPI** | Scanner REST API, account onboarding, role verification, and scan endpoints. | `scanner-service/app/main.py`, `scanner-service/app/api/` |
| **Uvicorn** | ASGI server for FastAPI locally and on Render/container deployments. | `scanner-service/requirements.txt`, service start command |
| **Flask** | Internal compliance auditor REST API. | `auditor-service/app/main.py` |
| **Gunicorn** | Production WSGI server for the Flask auditor container. | `auditor-service/Dockerfile` |
| **REST APIs / JSON** | Communication between React, FastAPI, AWS APIs, and the internal auditor service. | `frontend/src/services/api.js`, `scanner-service/app/api/`, `auditor-service/app/main.py` |
| **Boto3** | AWS SDK used for STS AssumeRole, identity verification, region discovery, and resource discovery. | `scanner-service/app/services/aws_session.py`, `scanner-service/app/services/scan_service.py`, `scanner-service/app/scanners/` |
| **Botocore** | AWS SDK core and client configuration/retry behavior used with Boto3. | Python requirements and AWS session code |
| **AWS IAM** | Platform principal and customer read-only role/trust relationship. | `infrastructure/aws/customer-role-template.yaml`, `docs/aws-cross-account-setup.md` |
| **AWS STS** | Assumes the customer's IAM role using the unique External ID and returns temporary credentials. | `scanner-service/app/services/aws_session.py` |
| **AWS EC2 / EBS / VPC / RDS / S3** | Cloud resource types discovered and evaluated by the scanner. | `scanner-service/app/scanners/` |
| **Supabase Auth** | User sign-in and access-token validation. | Frontend Supabase client and `scanner-service/app/auth.py` |
| **Supabase PostgreSQL** | Stores connected accounts, scan jobs, resource snapshots, policy violations, and cost estimates. | `scanner-service/app/database.py`, `auditor-service/app/database.py`, `database/migrations/` |
| **Row Level Security (RLS)** | Restricts user-facing database access to the authenticated user's records. | `database/migrations/` |
| **Cryptography / Fernet** | Encrypts the External ID before it is stored; the plaintext External ID is used server-side for role assumption. | `scanner-service/app/api/aws_connections.py`, `scanner-service/app/services/scan_service.py` |
| **Pydantic** | Validates scanner API request payloads. | `scanner-service/app/api/aws_connections.py` |
| **HTTPX** | Calls the internal Flask auditor endpoint from the scanner service. | `scanner-service/app/services/auditor_client.py` |
| **Docker** | Packages frontend, scanner, and auditor services into containers. | `frontend/Dockerfile`, `scanner-service/Dockerfile`, `auditor-service/Dockerfile` |
| **Docker Compose** | Runs the three application services together locally; LocalStack is available under the `local` profile. | `docker-compose.yml` |
| **Nginx** | Serves the built React frontend container. | `frontend/Dockerfile`, `frontend/nginx.conf` |
| **LocalStack** | Optional local AWS-compatible environment for development/testing. | `docker-compose.yml` |
| **GitHub Actions** | Runs scanner tests, auditor tests, frontend tests/build, and Docker image builds. This workflow is CI; hosting deployments are configured separately. | `.github/workflows/ci.yml` |
| **Pytest / pytest-cov** | Python test execution and coverage. | Service `tests/` folders and `.github/workflows/ci.yml` |
| **Vitest / Testing Library** | Frontend component and behavior tests. | `frontend/package.json`, frontend tests |
| **Vercel** | Hosts the React frontend. | Vercel project configuration; frontend source is in `frontend/` |
| **Render** | Hosts the Scanner Service and Auditor Service. | Render service configuration; source folders are `scanner-service/` and `auditor-service/` |

### Main repository folders

```text
cloud-governance-platform/
├── frontend/                  # React + Vite dashboard
│   └── src/
│       ├── pages/              # Dashboard and page components
│       └── services/           # Supabase client and FastAPI API helpers
├── scanner-service/            # FastAPI + Boto3 AWS scanner
│   └── app/
│       ├── api/                # Scan, resource, AWS connection endpoints
│       ├── scanners/            # EC2, EBS, S3, RDS, SG, Elastic IP scanners
│       ├── services/            # AWS sessions, scan orchestration, auditor client
│       ├── auth.py              # Supabase token and account ownership checks
│       └── database.py          # Supabase server client
├── auditor-service/            # Flask governance/compliance auditor
│   └── app/
│       ├── policies/            # Individual resource governance rules
│       ├── finops/              # Monthly waste estimation
│       ├── reports/             # Report generation
│       ├── services/            # Audit orchestration
│       └── main.py              # Internal audit and report endpoints
├── database/
│   └── migrations/              # Supabase schema changes
├── infrastructure/
│   └── aws/                     # Customer IAM role CloudFormation template
├── docs/                        # Setup and architecture notes
├── .github/workflows/           # GitHub Actions CI
├── docker-compose.yml           # Local multi-service environment
└── README.md
```

---

## 3. How to Use the Live Application (Customer Guide)

These steps describe what a new user needs to do to connect their own AWS account.

### Before starting

The user needs:

1. A working account on the Cloud Governance Platform.
2. Access to the AWS account they want to connect.
3. Permission in that AWS account to create IAM roles and policies (or an AWS administrator who can do it).
4. The platform operator must already have configured the backend AWS credentials and environment variables in Render, as described in the operator setup below.

**Never enter AWS root credentials, IAM access keys, or IAM secret keys into the dashboard.** The customer connection uses an IAM role and temporary STS credentials.

### Step 1 — Sign in

1. Open the [Cloud Governance Platform](https://cloud-governance-platform.vercel.app).
2. Create an account or sign in using the authentication options shown.
3. Open the dashboard after successful sign-in.

### Step 2 — Create an AWS connection in the dashboard

In **Connect an AWS Account**, fill in:

| Dashboard field | What to enter | Where to find it |
|---|---|---|
| **Account display name** | A friendly label, e.g. `Production AWS` or `My Test Account`. | Choose any name; it is only a label in the dashboard. |
| **12-digit AWS Account ID** | The 12-digit ID of the AWS account to scan. | AWS Console → account menu in the top-right → Account ID. |
| **AWS Region** | The initial/default region for the connection, e.g. `ap-south-1` for Mumbai. | Choose the region where you want the scan to start. The scanner then discovers the account's other enabled regions. |

Click **Create AWS Connection**.

The dashboard creates a pending connection and displays a generated **External ID**. Copy and securely retain it immediately. The backend displays this value only once during connection creation. It is not the AWS account ID, IAM user name, or access key.

If the External ID is lost before the role is configured, disconnect that pending connection and create a new one to generate a new External ID.

### Step 3 — Create the customer IAM role in AWS

Sign in to the AWS Console for the same account ID entered in the dashboard.

1. Open **IAM → Roles → Create role**.
2. Choose **Custom trust policy**.
3. Configure the trust relationship so that only the platform's dedicated IAM principal can assume this role, and only when it supplies the External ID from Step 2.
4. Attach a read-only discovery permissions policy to the role.
5. Name the role (the included CloudFormation template uses `CloudGovernanceReadOnlyRole`).
6. Create the role and copy its Role ARN.

#### 3A. Trust policy — who can assume the customer role

Replace:
- `PLATFORM_PRINCIPAL_ARN` with the exact IAM user or IAM role ARN used by the platform backend.
- `PASTE_EXTERNAL_ID_FROM_DASHBOARD` with the External ID generated for this connection.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "PLATFORM_PRINCIPAL_ARN"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "PASTE_EXTERNAL_ID_FROM_DASHBOARD"
        }
      }
    }
  ]
}
```

The platform principal ARN is **not** the customer's role ARN. The platform operator must provide the exact principal ARN. Do not guess it. The principal ARN is also the identity whose credentials are configured for the Scanner Service in Render.

#### 3B. Customer role permissions policy — what the scanner can read

Attach this customer-side permissions policy to the role. It grants discovery/read actions only; it does not grant create, update, delete, or remediation permissions.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:Describe*",
        "rds:Describe*",
        "s3:ListAllMyBuckets",
        "s3:GetBucketLocation",
        "s3:GetBucketPolicy",
        "s3:GetBucketPolicyStatus",
        "s3:GetBucketPublicAccessBlock",
        "s3:GetBucketAcl"
      ],
      "Resource": "*"
    }
  ]
}
```

This policy matches the permissions in the repository's customer-role CloudFormation template. If the project adds more AWS service checks in the future, review and extend the policy only for the required read actions.

#### 3C. Optional: create the role using the included CloudFormation template

The repository includes a template at `infrastructure/aws/customer-role-template.yaml`. In the customer's AWS account:

1. Open **CloudFormation → Create stack → With new resources (standard)**.
2. Upload or provide the template from the repository.
3. Set `PlatformPrincipalArn` to the exact platform backend IAM user/role ARN.
4. Set `ExternalId` to the value copied from the dashboard.
5. Create the stack.
6. Open the stack's **Outputs** tab and copy `RoleArn`.

The template creates a role named `CloudGovernanceReadOnlyRole`, adds the External ID trust condition, and attaches the read-only discovery policy above.

### Step 4 — Verify the role in the dashboard

1. Return to the Cloud Governance dashboard.
2. Paste the customer role's full ARN into **IAM Role ARN**.
3. Click **Verify AWS Role**.
4. The backend attempts STS AssumeRole using the configured platform identity and the stored External ID.
5. It checks the account ID returned by AWS STS against the account ID entered in Step 2.

The connection should change from **Pending** to **Connected** after successful verification.

A role ARN looks like:

```text
arn:aws:iam::123456789012:role/CloudGovernanceReadOnlyRole
```

The 12-digit account number in the ARN must be the same AWS account ID registered in the dashboard.

### Step 5 — Run a cloud scan

1. In **Connected Cloud Accounts**, select the verified account.
2. Click **Start Cloud Scan**.
3. Wait for the scan request to finish.
4. Review the resource inventory, resource distribution, scan history, security/compliance findings, and potential monthly savings.

The scanner uses the selected account's verified role. It discovers enabled AWS regions and scans regional services in those regions. S3 bucket discovery is performed globally and bucket locations are resolved.

If a service or region cannot be scanned (for example, due to a missing permission or an AWS API error), the scan records the collection error. Successfully discovered resource snapshots may still be stored, but the scan is not treated as a clean completed scan.

### Step 6 — Disconnect an account

Use **Disconnect** in the connected accounts table to remove the platform's saved connection record. Existing scan history is retained. This does not delete the IAM role from the customer's AWS account. To revoke platform access completely, the customer must also delete the customer IAM role or remove its trust relationship in AWS IAM.

---

## 4. Platform Operator Setup (Maintainers)

This section is for the person deploying and operating the platform, not an ordinary dashboard user.

### 4.1 Platform AWS identity

The platform operator must create a dedicated IAM user or role for the Scanner Service. Do not use AWS root credentials.

The platform principal needs permission to call `sts:AssumeRole` on the customer roles created for this application. For a role naming convention of `CloudGovernanceReadOnlyRole`, an example identity policy is:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "sts:AssumeRole",
      "Resource": "arn:aws:iam::*:role/CloudGovernanceReadOnlyRole"
    }
  ]
}
```

Restrict this resource pattern further if the deployment has a known set of customer accounts. Each customer role must separately trust the exact platform principal ARN and require the unique External ID.

For Render deployments using static IAM user credentials, store the dedicated platform IAM user's access key and secret key only as Render environment variables. Never commit them or put them in frontend variables.

### 4.2 Render services

Deploy two separate services from the repository:

| Render service | Root directory | Runtime/start command |
|---|---|---|
| Scanner Service | `scanner-service` | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Auditor Service | `auditor-service` | `gunicorn --bind 0.0.0.0:$PORT app.main:app` |

Configure the Scanner Service environment variables:

| Variable | Purpose |
|---|---|
| `SUPABASE_URL` | Supabase project URL. |
| `SUPABASE_SECRET_KEY` | Backend-only Supabase secret/service key used by the server client. Never expose it in the frontend. |
| `AWS_ACCESS_KEY_ID` | Dedicated platform IAM user's access key when using static credentials on Render. |
| `AWS_SECRET_ACCESS_KEY` | Matching secret key; keep private. |
| `AWS_CONNECTION_MODE` | Set to `container` for Render. |
| `AWS_REGION` | AWS region used for the platform's STS client, e.g. `ap-south-1`. |
| `CONNECTION_ENCRYPTION_KEY` | Fernet key used to encrypt External IDs at rest. |
| `AUDITOR_URL` | Internal or public base URL of the deployed Auditor Service. |
| `INTERNAL_SERVICE_TOKEN` | Shared secret used to authenticate scanner-to-auditor requests. |

Configure the Auditor Service environment variables:

| Variable | Purpose |
|---|---|
| `SUPABASE_URL` | Same Supabase project URL. |
| `SUPABASE_SECRET_KEY` | Backend-only Supabase secret/service key. |
| `INTERNAL_SERVICE_TOKEN` | Must match the Scanner Service value. |
| `COST_EBS_GB_MONTH_INR` | Configurable EBS monthly cost assumption used by the estimator. |
| `COST_ELASTIC_IP_MONTH_INR` | Configurable Elastic IP monthly cost assumption used by the estimator. |

Generate a Fernet encryption key locally with:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Set the generated value as `CONNECTION_ENCRYPTION_KEY` in the Scanner Service environment. Keep the key stable: changing it makes previously encrypted External IDs unreadable unless those connections are recreated.

### 4.3 Vercel frontend

Deploy the `frontend/` directory as the Vercel project root. Configure:

| Variable | Purpose |
|---|---|
| `VITE_SUPABASE_URL` | Supabase project URL. |
| `VITE_SUPABASE_PUBLISHABLE_KEY` | Supabase publishable/anon key intended for browser use. |
| `VITE_API_BASE_URL` | Base URL of the deployed Scanner Service. |

Only public/publishable frontend configuration belongs in `VITE_*` variables. Never put the Supabase secret key, AWS access key, AWS secret key, Fernet key, or internal service token in Vercel frontend environment variables.

### 4.4 Supabase database

1. Create/configure the Supabase project.
2. Apply the SQL migrations in `database/migrations/` in filename order.
3. Confirm the application tables and RLS policies are present.
4. Configure the same Supabase project URL and backend secret key in both Render services.
5. Configure the Supabase URL and publishable key in Vercel.

The AWS cross-account connection migrations add connection status, role ARN, encrypted External ID, verification timestamp, and the supported connection type. Do not skip migrations when setting up a new environment.

### 4.5 GitHub Actions CI

The workflow in `.github/workflows/ci.yml` runs on pushes to `main` and `develop`, pull requests targeting `main`, and manual dispatch. It:

- Installs Python dependencies and runs scanner tests.
- Installs Python dependencies and runs auditor tests.
- Installs frontend dependencies, runs Vitest, and builds the Vite frontend.
- Builds Docker images for the scanner, auditor, and frontend.

GitHub Actions is the project's CI workflow. Vercel and Render deployments are configured separately through their connected GitHub repository and deployment branch settings.

---

## 5. Run Locally

### Prerequisites

- Git
- Python 3.12
- Node.js 22 and npm
- Docker Desktop / Docker Engine with Docker Compose
- A Supabase project and its required environment variables
- AWS credentials/profile for local AWS testing, or a connected customer role for the multi-tenant flow

### Clone the repository

```bash
git clone https://github.com/yuvraj-singh009/cloud-governance-platform.git
cd cloud-governance-platform
```

### Configure environment

Create a local `.env` file based on the variable names in the deployment section. Use your own credentials and local values. Do not copy real credentials into source control.

For the frontend, configure the Vite variables in the frontend build environment or your local Vite environment file.

### Start with Docker Compose

```bash
docker compose up --build
```

The compose file exposes:

- Frontend: http://localhost:5173
- FastAPI Scanner: http://localhost:8000
- FastAPI Swagger docs: http://localhost:8000/docs
- Flask Auditor: internal container port 5000 (not published to the host by default)

LocalStack is optional and is defined under the `local` Compose profile. To include it:

```bash
docker compose --profile local up --build
```

### Run services separately (development)

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Scanner:

```bash
cd scanner-service
python -m venv .venv
# Activate the virtual environment, then:
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Auditor:

```bash
cd auditor-service
python -m venv .venv
# Activate the virtual environment, then:
pip install -r requirements.txt
flask --app app.main run --host 0.0.0.0 --port 5000
```

---

## 6. Security Notes

- Use a dedicated least-privilege platform IAM identity; never use root credentials.
- Customer accounts grant access through a role trust policy, not by sharing customer access keys.
- The unique External ID helps prevent the confused-deputy problem and is required by the trust policy.
- The backend encrypts the External ID before storing it in Supabase.
- Temporary STS credentials are used for customer-account scans.
- Keep AWS credentials, Supabase secret keys, Fernet keys, and internal service tokens in server-side secret stores only.
- The customer discovery role is read-only. It does not provide resource remediation permissions.
- Disconnecting an account in the dashboard removes the platform connection record; it does not delete the IAM role in the customer's AWS account.
- Rotate any credential that has accidentally been committed to a repository or shared publicly.

---

## 7. Tests and Build Commands

Scanner tests:

```bash
cd scanner-service
pytest -v
```

Auditor tests:

```bash
cd auditor-service
pytest -v
```

Frontend tests and production build:

```bash
cd frontend
npm run test
npm run build
```

The GitHub Actions workflow runs these checks and builds the Docker images on its configured events.

---

## 8. Current Scope

Implemented in the current application:

- User sign-in and dashboard access.
- Multi-tenant AWS account registration.
- Unique External ID generation and encrypted storage.
- Cross-account IAM role verification through AWS STS.
- Multi-region resource discovery for EC2, EBS, RDS, Security Groups, and Elastic IPs.
- Global S3 bucket discovery.
- Resource snapshots and scan history in Supabase.
- Implemented governance checks and findings.
- Configurable INR-based potential waste estimates.
- React dashboard and deployed frontend/backend services.

The repository also contains LocalStack support for local development. The current live customer integration is AWS cross-account role based. Do not describe Azure or Google Cloud scanning as implemented unless those integrations are added and tested.

---

## Author

**Yuvraj Singh**

- GitHub: [yuvraj-singh009](https://github.com/yuvraj-singh009)
- Project: [Cloud Governance & Cost Optimization Platform](https://github.com/yuvraj-singh009/cloud-governance-platform)
