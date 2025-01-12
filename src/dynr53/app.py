#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=W0102,E0712,C0103,R0903

"""Dynamic Route 53 Updater"""

__updated__ = "2025-01-12 23:39:05"


import boto3
import requests
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import socket
from config import Config

# ================================================================
#
# Step by step quide on AWS configuration
# ----------------------------------------
#
# AWS IAM Configuration:
# 1. Create an IAM user named "route53-updater".
# 2. Assign the following policy to the user:
# {
#     "Version": "2012-10-17",
#     "Statement": [
#         {
#             "Effect": "Allow",
#             "Action": "route53:ChangeResourceRecordSets",
#             "Resource": "arn:aws:route53:::hostedzone/*"
#         },
#         {
#             "Effect": "Allow",
#             "Action": "route53:GetChange",
#             "Resource": "*"
#         }
#     ]
# }
# 3. Store the access keys securely and use them to configure the script:
#    - Run `aws configure --profile route53-updater` on the machine where the
#      script will run.
#    - Enter the access key ID, secret access key, default region
#      (e.g., eu-south-2), and output format (e.g., json).
#    - The script will use this profile for AWS session management.
#
# ================================================================

# ================================================================
#
# Variables to configure per DNS entry 
# ------------------------------------
#
# Replace with your hosted zone ID
HOSTED_ZONE_ID = Config.HOSTED_ZONE_ID
#
# Replace with your domain name
RECORD_NAME = Config.RECORD_NAME
#
# Time to Live in seconds
TTL = Config.TTL
#
# ================================================================ 


##################################################################
#          DO NOT CONFIGURE ANYTHING BEYOND THIS POINT           #
##################################################################


# Function to fetch the current public IP
def get_public_ip():
    try:
        return requests.get("http://api.ipify.org").text.strip()  # noqa
    except requests.RequestException as e:
        print(f"Error fetching public IP: {e}")
        return None

# Function to resolve the current IP address assigned to the DNS entry
def resolve_dns_ip(record_name):
    try:
        return socket.gethostbyname(record_name)
    except socket.gaierror as e:
        print(f"Error resolving DNS for {record_name}: {e}")
        return None

# Function to fetch the current Route 53 record value
def get_route53_record_value(client, hosted_zone_id, record_name):
    try:
        response = client.list_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            StartRecordName=record_name,
            StartRecordType="A",
            MaxItems="1"
        )
        record_sets = response.get("ResourceRecordSets", [])
        if record_sets and record_sets[0]["Name"] == f"{record_name}.":
            return record_sets[0]["ResourceRecords"][0]["Value"]
        return None
    except client.exceptions.ClientError as e:
        print(f"AWS ClientError fetching Route 53 record: {e}")
        return None
    except Exception as e:
        print(f"Error fetching Route 53 record: {e}")
        return None

# Function to update the Route 53 DNS record
def update_route53_record(client, hosted_zone_id, record_name, ip, ttl):
    try:
        response = client.change_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            ChangeBatch={
                "Changes": [
                    {
                        "Action": "UPSERT",
                        "ResourceRecordSet": {
                            "Name": record_name,
                            "Type": "A",
                            "TTL": ttl,
                            "ResourceRecords": [{"Value": ip}],
                        },
                    }
                ]
            },
        )
        return response
    except client.exceptions.ClientError as e:
        print(f"AWS ClientError updating Route 53 record: {e}")
        return None
    except Exception as e:
        print(f"Error updating Route 53 record: {e}")
        return None

# Function to get AWS session
def get_aws_session():
    try:
        session = boto3.Session()
        sts = session.client("sts")
        sts.get_caller_identity()  # Validate credentials
        print("AWS session established successfully.")
        return session
    except NoCredentialsError:
        print("Error: No AWS credentials found. Ensure they are configured.")
        return None
    except PartialCredentialsError:
        print("Error: Incomplete AWS credentials found. Verify configuration.")
        return None
    except Exception as e:
        print(f"Error establishing AWS session: {e}")
        return None

# Main script logic
def main():
    try:

        # -- Resolve public IP address for DNS record to update
        dns_ip = resolve_dns_ip(RECORD_NAME)        
        if not dns_ip:
            print("Failed to resolve DNS IP. Continuing with the script.")
        else:
            print(f"Resolved DNS IP: {dns_ip}")

        # -- Get public IP address associated with Internet NIC
        current_ip = get_public_ip()
        if not current_ip:
            print("Failed to get current public ip address")
            return
        else:
            print(f"Current public IP: {current_ip}")

        # -- Evaluation of public IPs        
        if dns_ip and current_ip != dns_ip:
            pass
            print(f"Public IP ({current_ip}) different from DNS IP ({dns_ip}).")

            # -- Reached to this point IPs are different and we need to
            # -- reconfigure DNS for which we need to get a session on AWS
            aws_session = get_aws_session()
            if not aws_session:
                return

            # -- Spawn a Route53 client witn SoD & LP configuration applied.
            # -- For more details see top comment block
            route53_client = aws_session.client("route53")
            response = update_route53_record(route53_client, HOSTED_ZONE_ID,
                                             RECORD_NAME, current_ip, TTL)
            if response:
                print("Route 53 record updated successfully.")
            else:
                print("Failed to update Route 53 record.")

        else:
            print(f"No IP update needed.")
            return

    except Exception as e:
        print(f"Unexpected error in main execution: {e}")

if __name__ == "__main__":
    main()
