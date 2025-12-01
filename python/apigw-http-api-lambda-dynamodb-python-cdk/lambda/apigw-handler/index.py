# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

patch_all()

import boto3
import os
import json
import logging
import uuid
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb_client = boto3.client("dynamodb")


def log_security_event(event_type, details, context):
    """Log security events in structured JSON format"""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "request_id": context.request_id,
        "function_name": context.function_name,
        "details": details,
    }
    logger.info(json.dumps(log_entry))


def handler(event, context):
    # Log incoming request with security context
    log_security_event(
        "api_request",
        {
            "http_method": event.get("httpMethod"),
            "path": event.get("path"),
            "source_ip": event.get("requestContext", {}).get("identity", {}).get("sourceIp"),
            "user_agent": event.get("requestContext", {}).get("identity", {}).get("userAgent"),
        },
        context
    )
    
    table = os.environ.get("TABLE_NAME")
    logger.info(f"## Loaded table name from environemt variable DDB_TABLE: {table}")
    
    if event.get("body"):
        item = json.loads(event["body"])
        logger.info(f"## Received payload: {item}")
        year = str(item["year"])
        title = str(item["title"])
        id = str(item["id"])
        
        dynamodb_client.put_item(
            TableName=table,
            Item={"year": {"N": year}, "title": {"S": title}, "id": {"S": id}},
        )
        
        log_security_event(
            "dynamodb_write",
            {"table": table, "item_id": id, "operation": "put_item"},
            context
        )
        
        message = "Successfully inserted data!"
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": message}),
        }
    else:
        logger.info("## Received request without a payload")
        default_id = str(uuid.uuid4())
        
        dynamodb_client.put_item(
            TableName=table,
            Item={
                "year": {"N": "2012"},
                "title": {"S": "The Amazing Spider-Man 2"},
                "id": {"S": default_id},
            },
        )
        
        log_security_event(
            "dynamodb_write",
            {"table": table, "item_id": default_id, "operation": "put_item", "default_data": True},
            context
        )
        
        message = "Successfully inserted data!"
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": message}),
        }
