# AI Test Reliability Lab

## Goal

Can AI reliably generate security tests that discover genuine API
vulnerabilities, and can automated validation make those tests more accurate,
trustworthy, and cost-effective?

## First baseline

The first milestone is a handwritten authorization test running in Azure. It
checks that a VAmPI user can read their own private book and that a second user
receives a `404` without seeing its secret. This gives us a known result to
compare against when evaluating AI-generated tests.

## Next steps

1. Build a small set of reviewed examples with known outcomes, including
   allowed requests, blocked requests, and setup failures.
2. Review candidate AI-generated tests against those examples. Check that each
   test asks a clear question and that its result follows from the evidence.
3. Compare human review alone with human review plus automated checks. Track
   correct findings, false alarms, missed cases, repeatability, and the time
   and cost per confirmed finding.

## Azure deployment

The lab runs in North Europe under `rg-ai-test-lab`:

- `env-ai-test-lab` hosts both the server and the test job.
- `vampi-secure` runs VAmPI in secure mode with a private address. Initialize
  its SQLite database before testing a fresh instance.
- Azure Container Registry stores the test image. The Docker build installs
  Python dependencies from `uv.lock`.
- `job-ai-test-lab` uses its Azure identity to pull the image and runs pytest
  against VAmPI when started manually.

## Run the test

```sh
az containerapp job start -n job-ai-test-lab -g rg-ai-test-lab
az containerapp job execution list -n job-ai-test-lab -g rg-ai-test-lab -o table
```

Look for `Succeeded` in the run history and `1 passed` in the pytest logs.
In the Azure portal, open the job's **Execution history** for run status and
the environment's **Log Analytics** workspace for test output.

For local setup, run `uv sync --locked --python 3.11`.
