# AWS Deployment Guide

This guide walks you through deploying the AI Cloud Cost Monitoring platform to Amazon Web Services using ECS Fargate or AWS App Runner as the home cloud.

> [!NOTE]
> This is a **template guide**. The platform is currently optimized for GCP deployment. AWS deployment patterns are provided here for reference and future implementation.

## Table of Contents

- [Service Stack Mapping](#service-stack-mapping)
- [Prerequisites](#prerequisites)
- [Infrastructure Overview](#infrastructure-overview)
- [Deployment Pattern](#deployment-pattern)
- [Configuration](#configuration)
- [Cost Estimates](#cost-estimates)

---

## Service Stack Mapping

### GCP → AWS Service Equivalents

| Component | GCP Service | AWS Service | Notes |
|-----------|-------------|-------------|-------|
| **Containers** | Cloud Run | **ECS Fargate** or **App Runner** | App Runner simpler, Fargate more control |
| **Relational DB** | Cloud SQL PostgreSQL | **RDS PostgreSQL** or **Aurora PostgreSQL** | Aurora recommended for prod |
| **Analytics DB** | BigQuery | **Athena + S3** or **Redshift Serverless** | Athena for cost, Redshift for performance |
| **Object Storage** | Cloud Storage | **S3** | Direct equivalent |
| **Secrets** | Secret Manager | **Secrets Manager** | Direct equivalent |
| **Task Queue** | Cloud Tasks | **SQS + Lambda** | SQS for queues, Lambda for workers |
| **Scheduler** | Cloud Scheduler | **EventBridge Scheduler** | Direct equivalent (formerly CloudWatch Events) |
| **Cache (optional)** | Memorystore Redis | **ElastiCache Redis** | Direct equivalent |
| **Container Registry** | GCR / Artifact Registry | **ECR** | Elastic Container Registry |
| **VPC Connector** | VPC Connector | **VPC** | Native VPC support |

---

## Prerequisites

### Required Tools

- **AWS CLI** v2 - [Install](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- **Terraform** v1.6+ - [Install](https://www.terraform.io/downloads)
- **Docker** - [Install](https://docs.docker.com/get-docker/)
- **Git** - [Install](https://git-scm.com/downloads)

### Required Permissions

IAM user/role with:
- `AmazonECS_FullAccess` (ECS Fargate deployment)
- `AmazonRDSFullAccess` (Database)
- `AmazonS3FullAccess` (Object storage)
- `SecretsManagerReadWrite` (Secrets)
- `AmazonSQSFullAccess` + `AWSLambda_FullAccess` (Task queue)
- `AmazonElastiCacheFullAccess` (Optional Redis cache)

### AWS Account Requirements

- AWS Account with billing enabled
- VPC with public and private subnets
- Route53 hosted zone (optional, for custom domain)

---

## Infrastructure Overview

### Architecture on AWS

```
Internet
    ↓
Application Load Balancer (ALB)
    ↓
ECS Fargate (Frontend + Backend containers)
    ↓
├── RDS PostgreSQL (VPC, private subnet)
├── Athena + S3 (Analytics queries)
├── SQS + Lambda (Background tasks)
├── Secrets Manager (Credentials)
└── ElastiCache Redis (Optional cache)
```

---

## Deployment Pattern

### 1. Initial Setup

```bash
# Configure AWS CLI
aws configure

# Set region
export AWS_REGION=us-east-1
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
```

### 2. Infrastructure Deployment (via Terraform)

**Terraform structure** (to be created):

```hcl
# terraform/aws/main.tf

# VPC and Networking
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  # ... VPC configuration
}

# RDS PostgreSQL
resource "aws_db_instance" "postgres" {
  engine         = "postgres"
  engine_version = "16"
  instance_class = "db.t3.micro"  # MVP
  # ...
}

# S3 for Athena results
resource "aws_s3_bucket" "analytics" {
  # ...
}

# Secrets Manager
resource "aws_secretsmanager_secret" "auth0_client_secret" {
  # ...
}

# ECS Fargate cluster
resource "aws_ecs_cluster" "main" {
  name = "ai-cost-monitoring"
  # ...
}

# Application Load Balancer
resource "aws_lb" "main" {
  # ...
}

# SQS Queue for background tasks
resource "aws_sqs_queue" "tasks" {
  # ...
}

# EventBridge Scheduler for scheduled jobs
resource "aws_scheduler_schedule" "cost_sync" {
  # ...
}
```

### 3. Container Deployment

```bash
# Build and push to ECR
aws ecr create-repository --repository-name ai-cost-monitoring-frontend
aws ecr create-repository --repository-name ai-cost-monitoring-backend

# Login to ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Build and push
docker build -t $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/ai-cost-monitoring-frontend:latest ./frontend
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/ai-cost-monitoring-frontend:latest

# Deploy to ECS Fargate (via Terraform or AWS CLI)
# Task definitions, services, and ALB target groups
```

---

## Configuration

### Environment Variables

Key differences from GCP:

```bash
# AWS-specific
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=123456789012

# Database (RDS)
DATABASE_HOST=<rds-endpoint>.rds.amazonaws.com
DATABASE_PORT=5432

# Analytics (Athena)
ATHENA_DATABASE=ai_cost_monitoring
ATHENA_OUTPUT_BUCKET=s3://ai-cost-monitoring-athena-results

# Secrets Manager
SECRETS_MANAGER_PREFIX=ai-cost-monitoring/

# Task Queue (SQS)
SQS_QUEUE_URL=https://sqs.us-east-1.amazonaws.com/123456789012/ai-cost-monitoring-tasks

# Cache (ElastiCache) - optional
REDIS_HOST=<elasticache-endpoint>.cache.amazonaws.com
REDIS_PORT=6379
```

---

## Cost Estimates

### MVP Deployment (Single Tenant)

| Service | Configuration | Monthly Cost |
|---------|---------------|--------------|
| **ECS Fargate** | 0.5 vCPU, 1GB RAM, 2 tasks | ~$30 |
| **RDS PostgreSQL** | db.t3.micro | ~$15 |
| **Athena + S3** | ~100GB storage, 10GB scanned/month | ~$5 |
| **SQS + Lambda** | 1M requests, 10K Lambda executions | ~$2 |
| **Secrets Manager** | 5 secrets | ~$2 |
| **Data Transfer** | 10GB/month | ~$1 |
| **Total (MVP)** | | **~$55-75/month** |

### Production Deployment

| Service | Configuration | Monthly Cost |
|---------|---------------|--------------|
| **ECS Fargate** | 2 vCPU, 4GB RAM, 5 tasks | ~$150 |
| **RDS PostgreSQL** | db.r6g.large (HA) | ~$200 |
| **Athena + S3** | 500GB storage, 100GB scanned/month | ~$20 |
| **SQS + Lambda** | 10M requests, 100K executions | ~$5 |
| **ALB** | Application Load Balancer | ~$20 |
| **ElastiCache Redis** | cache.t3.micro (optional) | ~$15 |
| **CloudWatch Logs** | 10GB/month | ~$5 |
| **Total (Production)** | | **~$415-500/month** |

---

## Next Steps

To implement AWS deployment:

1. ✅ Review this service mapping
2. ⬜ Create Terraform modules in `terraform/aws/`
3. ⬜ Adapt application code for AWS services (Boto3 for Athena, SQS, Secrets Manager)
4. ⬜ Create ECS task definitions
5. ⬜ Set up CI/CD pipeline (AWS CodePipeline or GitHub Actions)
6. ⬜ Test full deployment
7. ⬜ Expand this guide with actual deployment commands

---

## Resources

- **Main README**: [README.md](README.md) - Architecture overview
- **GCP Deployment**: [GCP-DEPLOYMENT.md](GCP-DEPLOYMENT.md) - Reference implementation
- **AWS ECS Docs**: https://docs.aws.amazon.com/ecs/
- **AWS Terraform Provider**: https://registry.terraform.io/providers/hashicorp/aws/

---

*This is a template guide. Contributions and improvements based on actual AWS deployments are welcome!*
