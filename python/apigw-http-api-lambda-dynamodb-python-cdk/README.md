
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
