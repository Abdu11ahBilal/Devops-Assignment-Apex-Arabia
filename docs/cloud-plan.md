# Cost-aware cloud path — proposal only

No cloud resources were provisioned for this assessment. No paid account, production system or customer data is required to reproduce the local deployment.

## Small pilot

For a low-traffic pilot, start with one appropriately sized Linux VM running the same Compose stack and persistent block storage. Measure memory/CPU before choosing instance size; the local assessment is not a load test. Add HTTPS through a reverse proxy, authentication, security updates and off-host encrypted database backups. Keep PostgreSQL private, restrict administration to a controlled access path, and inject secrets through a managed secret service rather than repository files.

A single VM is a cost-conscious pilot, not high availability. Its outage takes down both application and database. Document that trade-off and do not imply a volume snapshot alone satisfies recovery requirements.

## Cost model

Estimate monthly cost as:

`compute instance-hours × hourly rate + storage GB-month × storage rate + backup retention + data transfer + public IP + logs + registry/storage costs`

Select region, currency, architecture and workload assumptions in the [AWS Pricing Calculator](https://calculator.aws/). Do not assume free-tier eligibility. Also price recurring load-balancer, NAT gateway and managed-database charges before adding them; for a small pilot these can materially change the budget.

Apply resource tags, a fixed monthly budget, actual/forecast notifications and a teardown checklist. [AWS Budgets](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html) notifications can be delayed and are not an instantaneous hard spending cap. Limit log retention and remove idle resources.

## Growth path

Once availability/load requirements justify additional cost: separate the database into a private managed PostgreSQL service with tested backups, run multiple API instances behind a load balancer, replace local environment-file secrets with managed retrieval, and add deployment approvals and metrics. An orchestrator is an option after those needs are established; Kubernetes is not required for this assessment.

Local evidence demonstrates packaging and operational judgement, not successful AWS deployment or production capacity.
