# ADR-006: Use Cloud-Native Task Queues, Not Celery

## Status
Accepted

## Date
{DATE}

## Context

The platform needs to run background jobs for scheduled data sync, anomaly detection, and forecasting. Options:

1. **Celery + Redis/RabbitMQ** - Traditional Python task queue
2. **Temporal.io** - Workflow orchestration platform
3. **Cloud-native task queues** - Cloud Tasks (GCP), SQS (AWS), Service Bus (Azure)
4. **Kubernetes CronJobs** - Container-based scheduled jobs

## Decision

We will use **cloud-native task queue services** specific to the home cloud, not Celery or other third-party frameworks.

## Rationale

### Why Cloud-Native Task Queues?

**No Infrastructure to Manage:**
- Fully managed by cloud provider
- No broker (Redis/RabbitMQ) to maintain
- No worker process management
- Pay-per-use pricing

**Better Cloud Integration:**
- Native IAM integration (no credentials in code)
- Built-in monitoring and logging
- Auto-scaling without configuration
- Dead-letter queues built-in

**Simpler Architecture:**
- Fewer moving parts
- Less operational complexity
- Easier debugging (cloud console)
- Lower cost (~$5/month vs $50+ for Redis)

**Home Cloud Specific:**

| Home Cloud | Task Queue | Scheduler | Notes |
|------------|------------|-----------|-------|
| **GCP** | **Cloud Tasks** | **Cloud Scheduler** | Serverless, HTTP-based |
| **AWS** | **SQS + Lambda** | **EventBridge Scheduler** | Event-driven |
| **Azure** | **Service Bus + Functions** | **Azure Functions Timer** | Integrated platform |

### Why Not Celery?

**Infrastructure Overhead:**
- Need to run Redis or RabbitMQ broker
- Need to run  Celery worker processes
- Monitoring and HA complexity
- Extra $30-50/month in costs

**Operational Burden:**
- Broker failures need handling
- Worker scaling management
- Memory leak monitoring
- Version upgrade complexity

**Not Cloud-Native:**
- Doesn't integrate with cloud IAM
- Separate monitoring setup needed
- Manual scaling configuration
- Deployment complexity

### Why Not Temporal.io?

**Over-Engineering for Our Use Case:**
- Temporal is for complex workflows with state
- Our jobs are simple: fetch data, run analysis, save results
- Temporal adds significant complexity
- Heavyweight deployment (needs database, workers, frontend)

**Cost:**
- Cloud hosting: $200+/month
- Self-hosting: Infrastructure + ops burden
- Overkill for scheduled jobs every 4 hours

**Learning Curve:**
- New concept (workflows, activities, sagas)
- Team would need training
- Longer development time

### Why Not Kubernetes CronJobs?

- Requires Kubernetes cluster (see ADR-004: we use serverless containers)
- More complex than cloud-native schedulers
- No built-in retry logic
- Manual monitoring setup

## Implementation

### GCP (Cloud Tasks + Cloud Scheduler)

```python
# Enqueue a task
from google.cloud import tasks_v2

client = tasks_v2.CloudTasksClient()
task = {
    "http_request": {
        "http_method": tasks_v2.HttpMethod.POST,
        "url": "https://backend.run.app/api/jobs/sync-costs",
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"project_id": "my-project"}).encode(),
    }
}
client.create_task(parent=queue_path, task=task)
```

**Scheduled Jobs:**
```yaml
# Cloud Scheduler config
- name: cost-sync
  schedule: "0 */4 * * *"  # Every 4 hours
  http_target:
    uri: https://backend.run.app/api/jobs/sync-costs
    http_method: POST
```

### AWS (SQS + EventBridge)

```python
# Enqueue a task
import boto3

sqs = boto3.client('sqs')
sqs.send_message(
    QueueUrl='https://sqs.us-east-1.amazonaws.com/123456789/cost-sync',
    MessageBody=json.dumps({"project_id": "my-project"})
)
```

**Scheduled Jobs:**
```json
// EventBridge rule
{
  "schedule": "rate(4 hours)",
  "target": {
    "arn": "arn:aws:lambda:us-east-1:123456789:function:cost-sync"
  }
}
```

### Azure (Service Bus + Functions)

```python
# Enqueue a task
from azure.servicebus import ServiceBusClient, ServiceBusMessage

client = ServiceBusClient.from_connection_string(conn_str)
sender = client.get_queue_sender("cost-sync")
message = ServiceBusMessage(json.dumps({"project_id": "my-project"}))
sender.send_messages(message)
```

**Scheduled Jobs:**
```python
# Azure Function with timer trigger
import azure.functions as func

def main(mytimer: func.TimerRequest) -> None:
    # Runs every 4 hours
    # 0 */4 * * *
    sync_costs()
```

## Consequences

### Positive

- ✅ **Zero infrastructure** - No broker, no workers to manage
- ✅ **Lower cost** - $5-10/month vs $50+ for Celery stack
- ✅ **Cloud-native** - IAM, monitoring, scaling built-in
- ✅ **Simpler** - Fewer moving parts, easier debugging
- ✅ **Reliable** - Cloud provider SLA (99.9%+)

### Negative

- ⚠️ **Cloud-specific** - Different implementation per cloud
- ⚠️ **Less control** - Can't customize queueing behavior
- ⚠️ **Vendor lock-in** - Tied to cloud provider's queue

### Mitigation

**Cloud-Specific Implementation:**
- MCP server pattern abstracts the difference
- Backend code uses interface, cloud implementation injected
- Easy to add new cloud support

**Vendor Lock-In:**
- Acceptable - follows "home cloud principle" (see ADR-002)
- If changing clouds, this is least of migration concerns
- Pattern is same across clouds, just different APIs

## Background Job Requirements

Our platform needs these background jobs:

| Job | Frequency | Duration | Cloud Service |
|-----|-----------|----------|---------------|
| Cost Data Sync | Every 4 hours | 2-5 min | Cloud Tasks/SQS |
| Resource Inventory | Every 6 hours | 5-10 min | Cloud Tasks/SQS |
| Anomaly Detection | Every 4 hours | 1-3 min | Cloud Tasks/SQS |
| Recommendation Refresh | Daily at 2 AM | 5-10 min | Cloud Scheduler/Event Bridge |
| Forecast Update | Daily at 3 AM | 10-15 min | Cloud Scheduler/EventBridge |

**Total job execution time**: ~30 minutes/day

Cloud-native queues are perfect for this workload (not high-frequency trading!).

## Cost Comparison

### Cloud-Native (Our Choice)

**GCP:**
- Cloud Tasks: Free tier covers our usage
- Cloud Scheduler: $0.10/job/month × 5 jobs = $0.50/month
- **Total: ~$1/month**

**AWS:**
- SQS: Free tier covers our usage
- EventBridge Scheduler: Free
- Lambda executions: ~$2/month
- **Total: ~$2/month**

### Celery Alternative

- Redis (Memorystore/ElastiCache): $15-30/month
- Worker compute (always-on):  $20-40/month
- Monitoring: $5-10/month
- **Total: $40-80/month**

**Cloud-native is 40-80x cheaper** for our workload!

## Alternatives Considered

| Alternative | Monthly Cost | Complexity  | Decision |
|-------------|--------------|-------------|----------|
| Celery + Redis | $40-80 | High | Rejected |
| Temporal.io | $200+ | Very High | Rejected (over-kill) |
| **Cloud Tasks/SQS** | **$1-5** | **Low** | **Accepted** ✅ |
| Kubernetes CronJobs | $100+ | High | Rejected (ADR-004) |

## Related Decisions

- [ADR-002: GCP as First Home Cloud](002-gcp-only-first.md) - Home cloud principle applies here
- [ADR-004: Serverless Containers](004-cloud-run-not-kubernetes.md) - Consistent serverless approach

## References

- [GCP Cloud Tasks](https://cloud.google.com/tasks/docs)
- [AWS SQS + EventBridge](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-tutorial.html)
- [Azure Service Bus](https://learn.microsoft.com/en-us/azure/service-bus-messaging/)

## Review

Revisit this if:
- Job frequency increases to > 100/minute sustained
- Complex workflow orchestration needed (multi-step, compensating transactions)
- Job execution time exceeds cloud limits (15min for Lambda, 60min for Cloud Run)
- Team grows and can afford dedicated infrastructure team
