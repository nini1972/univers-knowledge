Show thinking
I apologize for the delay. Since the Design_Agent is unavailable, I will provide you with the exact steps and gcloud commands to set up Workload Identity Federation (WIF) manually.

This setup is more secure than a JSON key because it uses short-lived tokens and creates a direct trust relationship between GitHub and your Google Cloud project.

1. Set up variables
Replace the variables below in your terminal (I have pre-filled them based on your project and repo):

export PROJECT_ID="city-future-storyteller"
export REPO="nini1972/univers-knowledge" # Your GitHub repo
Generated code may be subject to license restrictions not shown here. Use code with care. Learn more 

2. Create the Workload Identity Pool
This pool will manage GitHub identities in your project.

gcloud iam workload-identity-pools create "github-pool" \
    --project="${PROJECT_ID}" \
    --location="global" \
    --display-name="GitHub Actions Pool"
Generated code may be subject to license restrictions not shown here. Use code with care. Learn more 

3. Create the Workload Identity Provider
This tells Google Cloud to trust tokens issued by GitHub.

gcloud iam workload-identity-pools providers create-oidc "github-provider" \
    --project="${PROJECT_ID}" \
    --location="global" \
    --workload-identity-pool="github-pool" \
    --display-name="GitHub Actions Provider" \
    --issuer-uri="https://token.actions.githubusercontent.com" \
    --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository"
Generated code may be subject to license restrictions not shown here. Use code with care. Learn more 

4. Allow GitHub to act as your Service Account
This command grants your specific repository permission to "impersonate" the vertex-express service account.

gcloud iam service-accounts add-iam-policy-binding "vertex-express@${PROJECT_ID}.iam.gserviceaccount.com" \
    --project="${PROJECT_ID}" \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/projects/907993744320/locations/global/workloadIdentityPools/github-pool/attribute.repository/${REPO}"
Generated code may be subject to license restrictions not shown here. Use code with care. Learn more 

5. Update your GitHub Actions Workflow
You can now remove the GCP_SA_KEY secret. Instead, update your .yml workflow file to use the google-github-actions/auth action like this:

jobs:
  run-genmedia:
    runs-on: ubuntu-latest
    permissions:
      contents: 'read'
      id-token: 'write' # Required for requesting the JWT

    steps:
    - uses: 'actions/checkout@v4'


Generated code may be subject to license restrictions not shown here. Use code with care. Learn more 

Summary of settings for GitHub Secrets
You no longer need a JSON key. You only need to ensure the workload_identity_provider string in your YAML matches the path provided above.