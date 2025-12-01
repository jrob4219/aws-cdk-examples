
# AWS API Gateway HTTP API to AWS Lambda in VPC to DynamoDB CDK Python Sample!


## Overview

Creates an [AWS Lambda](https://aws.amazon.com/lambda/) function writing to [Amazon DynamoDB](https://aws.amazon.com/dynamodb/) and invoked by [Amazon API Gateway](https://aws.amazon.com/api-gateway/) REST API. 

![architecture](docs/architecture.png)

## Security and Compliance Prerequisites

### CloudTrail Configuration
Ensure AWS CloudTrail is enabled in your account to capture API activity for security investigations and audit compliance per AWS Well-Architected Framework SEC04-BP01.

**Verify CloudTrail is configured:**
```bash
aws cloudtrail describe-trails
```

**If not configured, create a trail:**
```bash
aws cloudtrail create-trail --name my-trail --s3-bucket-name my-cloudtrail-bucket
aws cloudtrail start-logging --name my-trail
```

**Note:** This stack includes comprehensive logging:
- API Gateway access logs (CloudWatch Logs)
- VPC Flow Logs (CloudWatch Logs)
- Lambda function logs with structured JSON format (CloudWatch Logs)
- DynamoDB Point-in-Time Recovery enabled
- AWS X-Ray tracing for distributed request tracking

All logs are retained for one year by default.

## Throttling and Rate Limiting

This stack implements AWS Well-Architected Framework **REL05-BP02: Throttle requests** best practice to protect against unexpected traffic spikes and resource exhaustion.

### Configured Throttle Limits

**API Gateway Stage-Level Throttling:**
- **Rate Limit**: 100 requests per second
- **Burst Limit**: 200 requests

These limits protect the API from sudden traffic spikes, retry storms, and flooding attacks. When limits are exceeded, API Gateway returns `429 Too Many Requests` responses.

**AWS WAF Per-IP Rate Limiting:**
- **Rate Limit**: 2000 requests per 5 minutes per IP address
- **Action**: Block requests exceeding limit

AWS WAF provides an additional layer of protection by limiting requests from individual IP addresses, preventing a single malicious actor or misconfigured client from consuming all available capacity.

**Lambda Reserved Concurrency:**
- **Reserved Concurrent Executions**: 50

Reserved concurrency limits the maximum number of concurrent executions for this Lambda function, preventing it from consuming all available account-level concurrency and impacting other functions in the same account and region.

### Monitoring Throttled Requests

Monitor throttled requests in CloudWatch:
- Navigate to CloudWatch Metrics → API Gateway
- View `4XXError` metric for throttled request counts
- Navigate to CloudWatch Metrics → WAFV2
- View `BlockedRequests` metric for WAF-blocked requests
- Navigate to CloudWatch Metrics → Lambda
- View `ConcurrentExecutions` metric to monitor function concurrency
- CloudWatch Alarms trigger when thresholds are exceeded

**Important:** These throttle values should be validated through load testing before production use. Adjust limits based on your workload's tested capacity.

## Load Testing and Capacity Planning

### Load Testing Requirements

**IMPORTANT:** The throttle limits configured in this stack are baseline values and **must be validated through load testing** before production deployment. Load testing establishes the actual capacity of your workload and ensures throttle limits are set appropriately.

### Recommended Load Testing Approach

1. **Establish Baseline Metrics**
   - Deploy the stack to a non-production environment
   - Run initial tests with low traffic to establish baseline performance
   - Monitor CloudWatch metrics for Lambda duration, DynamoDB capacity, and API Gateway latency

2. **Conduct Load Tests**
   - Use tools like Apache JMeter, Locust, or AWS Distributed Load Testing
   - Gradually increase request rate to identify breaking points
   - Test sustained load at 80% of expected peak capacity
   - Test burst scenarios with sudden traffic spikes
   - Monitor all CloudWatch metrics and alarms during tests

3. **Key Metrics to Capture**
   - Maximum sustained requests per second
   - Maximum burst capacity
   - Lambda concurrent executions at peak load
   - Lambda function duration under load (average and P99)
   - DynamoDB consumed read/write capacity units
   - API Gateway response times (average and P99)
   - Error rates and throttled request counts

4. **Adjust Throttle Limits**
   - Set API Gateway throttle limits to 80% of tested maximum capacity
   - Configure Lambda reserved concurrency based on peak concurrent executions
   - Adjust WAF rate limits based on legitimate traffic patterns observed
   - Document all tested limits and the conditions under which they were established

### Load Testing Best Practices

- **Test Realistic Scenarios**: Use production-like data and request patterns
- **Test Maximum Request Size**: Validate throttle limits with largest expected payloads
- **Test Both Rate and Size Together**: Don't test maximum rate and maximum size separately
- **Provision Matching Resources**: Ensure test environment resources match production
- **Document Everything**: Record test methodology, results, and configurations
- **Retest After Changes**: Re-run load tests after infrastructure or code changes
- **Schedule Regular Testing**: Conduct load tests quarterly or after significant changes

### Updating Throttle Limits

**WARNING:** Do not increase throttle limits beyond tested capacity. When increasing limits:

1. Verify current infrastructure can handle the increased load
2. Conduct new load tests at the proposed higher limits
3. Ensure provisioned resources (Lambda memory, DynamoDB capacity) are adequate
4. Update limits incrementally and monitor production metrics
5. Document the new tested capacity and test conditions

### Example Load Test Command (using Apache Bench)

```bash
# Test sustained load - 50 requests/sec for 60 seconds
ab -n 3000 -c 50 -t 60 \
  -H "Content-Type: application/json" \
  -p payload.json \
  https://<API_ID>.execute-api.<REGION>.amazonaws.com/prod/

# Monitor CloudWatch metrics during test
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name ConcurrentExecutions \
  --dimensions Name=FunctionName,Value=apigw_handler \
  --start-time <START_TIME> \
  --end-time <END_TIME> \
  --period 60 \
  --statistics Maximum
```

## Setup

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## Deploy
At this point you can deploy the stack. 

Using the default profile

```
$ cdk deploy
```

With specific profile

```
$ cdk deploy --profile test
```

## After Deploy
Navigate to AWS API Gateway console and test the API with below sample data 
```json
{
    "year":"2023", 
    "title":"kkkg",
    "id":"12"
}
```

You should get below response 

```json
{"message": "Successfully inserted data!"}
```

## Monitoring and Observability

This stack includes comprehensive monitoring and logging:

### CloudWatch Logs
- **API Gateway Access Logs**: View in CloudWatch Logs console under `/aws/apigateway/access-logs`
- **Lambda Function Logs**: Structured JSON logs with security context in `/aws/lambda/apigw_handler`
- **VPC Flow Logs**: Network traffic logs for security analysis

### AWS X-Ray
- Navigate to AWS X-Ray console to view service maps and traces
- Analyze request latency and identify bottlenecks
- View detailed traces of API Gateway → Lambda → DynamoDB calls

### CloudWatch Alarms
- **Lambda Error Alarm**: Triggers when function errors occur
- **Lambda Duration Alarm**: Triggers when execution exceeds 10 seconds
- **API Throttle Alarm**: Triggers when API Gateway throttles requests
- **Lambda Concurrency Alarm**: Triggers when function approaches concurrency limit (90% of reserved)
- **WAF Blocked Requests Alarm**: Triggers when WAF blocks excessive requests

### AWS WAF
- Navigate to AWS WAF console to view blocked requests
- Review sampled requests to identify attack patterns
- Adjust rate limits based on legitimate traffic patterns

## Cleanup 
Run below script to delete AWS resources created by this sample stack.
```
cdk destroy
```

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
