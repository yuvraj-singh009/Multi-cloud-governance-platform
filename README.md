# Multi-Cloud Cost & Resource Governance Platform

A cloud governance and FinOps platform designed to discover cloud resources, identify configuration risks, estimate potential infrastructure waste, and provide controlled remediation workflows.

## Overview

The platform connects to AWS accounts and collects infrastructure information through the AWS SDK. It evaluates resources against configurable compliance policies and presents findings through a React dashboard.

It helps cloud engineers identify:

- Unattached EBS volumes
- Unassociated Elastic IP addresses
- Security groups exposing SSH to the internet
- Missing mandatory resource tags
- Publicly accessible RDS configurations
- Potentially exposed S3 configurations

The platform also calculates configurable estimates of potential monthly infrastructure waste.

## Architecture

React.js Dashboard  
↓  
FastAPI Cloud Scanner  
↓  
AWS SDK (boto3)  
↓  
AWS Infrastructure  

FastAPI → Supabase PostgreSQL → Flask Compliance Auditor → Policy Findings and Cost Estimates

## Technology Stack

**Frontend**
- React.js
- JavaScript
- Recharts
- Axios

**Backend**
- Python
- FastAPI
- Flask
- REST APIs
- boto3

**Cloud and Infrastructure**
- Amazon Web Services
- AWS EC2
- AWS EBS
- Amazon S3
- AWS IAM
- AWS Security Groups
- Amazon RDS
- Docker
- Docker Compose
- LocalStack

**Database and Authentication**
- Supabase
- PostgreSQL
- Row Level Security

**Automation**
- GitHub Actions
- Pytest
- Vitest

## Key Features

- AWS resource discovery
- Resource inventory dashboard
- Configurable compliance policies
- Security misconfiguration detection
- Estimated monthly waste calculations
- Scan history and audit findings
- CSV and PDF reporting
- Controlled remediation workflow
- Docker-based application setup
- Automated testing and CI

## Project Structure

```text
cloud-governance-platform/
├── frontend/
├── scanner-service/
├── auditor-service/
├── supabase/
├── .github/
├── docker-compose.yml
├── .env.example
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.12 or compatible version
- Node.js 22 or compatible version
- Docker Desktop
- AWS CLI
- Supabase project

### Configuration

Clone the repository:

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd cloud-governance-platform
```

Copy the environment template:

```bash
cp .env.example .env
```

Configure the Supabase credentials, internal service token, AWS connection settings, and frontend variables.

For local AWS development, configure a dedicated AWS CLI profile:

```bash
aws configure --profile finops-dev
aws sts get-caller-identity --profile finops-dev
```

### Start the application

```bash
docker compose up --build -d
```

### Application URLs

- Frontend: http://localhost:5173
- FastAPI: http://localhost:8000
- API documentation: http://localhost:8000/docs

## Security

- AWS access is based on IAM permissions.
- The scanner uses read-only access for resource discovery.
- Backend service credentials are not exposed to React.
- Account ownership is verified before account operations.
- Remediation actions require authorization and approval.
- Audit logs record remediation activity.

## Cost Estimation

Cost estimates are based on configurable pricing assumptions. They are indicative estimates of potential waste, not actual AWS billing data.

## Current Scope and Limitations

The initial implementation focuses on AWS resource governance. Azure and Google Cloud adapters are planned extensions rather than implemented integrations.

LocalStack is used for local development and testing. Real AWS integration requires a configured AWS identity and appropriate IAM permissions.

## Testing

Run the backend test suites:

```bash
pytest -v
```

Run frontend tests:

```bash
npm run test
```

Build the frontend:

```bash
npm run build
```

## Future Enhancements

- Azure and Google Cloud integrations
- Advanced FinOps pricing analysis
- CloudWatch utilization-based idle-resource detection
- Scheduled account scans
- Expanded compliance policies
- Role-based governance workflows
- Infrastructure-as-code deployment

## Author

Yuvraj Singh

GitHub: YOUR_GITHUB_PROFILE_URL

LinkedIn: YOUR_LINKEDIN_PROFILE_URL