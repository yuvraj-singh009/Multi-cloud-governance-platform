# AWS customer account connection

This implementation uses cross-account IAM roles. Each customer grants the platform a narrowly scoped read-only role; no customer access keys are requested.

## Platform operator (one-time)
1. Use a dedicated IAM user or role for the Render backend. Never use root credentials.
2. For Render without workload identity, create an access key for that dedicated IAM user and store it only in Render environment variables. Never commit it.
3. Give the platform principal permission to call sts:AssumeRole only on customer roles named CloudGovernanceReadOnlyRole.
4. Record the exact principal ARN. Customers need this value.
5. Generate a Fernet key locally: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())". Set CONNECTION_ENCRYPTION_KEY in Render.

## Customer onboarding
1. Sign in and create a pending AWS connection.
2. Save the generated External ID; it is displayed once.
3. In the customer's AWS account, create a CloudFormation stack from infrastructure/aws/customer-role-template.yaml.
4. Supply PlatformPrincipalArn and ExternalId.
5. Copy the CloudFormation output RoleArn.
6. Submit the Role ARN to the connection verify endpoint. The backend calls STS GetCallerIdentity and checks the 12-digit account ID before marking it connected.

## Render configuration
- AWS_CONNECTION_MODE=container
- AWS_REGION=us-east-1 (or another STS region)
- AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY only for the dedicated platform IAM principal when workload identity is unavailable
- CONNECTION_ENCRYPTION_KEY generated above
- AWS_ENDPOINT_URL empty in production

## Deployment warning
This increment provides account registration and role verification. Existing scanner functions still create their own default AWS clients; the scan pipeline has NOT yet been switched to pass the customer's assumed session into every scanner. Keep customer scan execution disabled until that next integration step is complete and tested. The encrypted External ID must remain backend-only.
