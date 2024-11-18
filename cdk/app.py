#!/usr/bin/env python3
import os
import aws_cdk as cdk
from aws_cdk import (
    aws_s3 as s3,
    aws_ec2 as ec2,
    aws_lambda as _lambda,
    aws_rds as rds,
    aws_elasticache as elasticache,
)
from constructs import Construct

class MyStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a VPC
        vpc = ec2.Vpc(self, "searchengine-vpc", max_azs=2)

        # Create an S3 bucket
        bucket = s3.Bucket(self, "searchengine-data", versioned=True)

        # Create an RDS database
        db_instance = rds.DatabaseInstance(self, "searchengine-rds",
            engine=rds.DatabaseInstanceEngine.postgres(version=rds.PostgresEngineVersion.VER_12_3),
            instance_type=ec2.InstanceType("t2.micro"),
            vpc=vpc,
            multi_az=False,
            allocated_storage=20,
            max_allocated_storage=100,
            publicly_accessible=False,
            vpc_subnets={
                "subnet_type": ec2.SubnetType.PRIVATE_WITH_NAT
            },
            database_name="searchengine_database",
            credentials=rds.Credentials.from_generated_secret("postgres"),
        )

        # Security Group for ElastiCache
        redis_sg = ec2.SecurityGroup(
            self,
            "RedisSG",
            vpc=vpc,
            description="Allow Redis access",
            allow_all_outbound=True,
        )
        # Allow inbound traffic on the Redis port (6379)
        redis_sg.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(6379),
            "Allow Redis traffic"
        )
        # Subnet group for Redis
        redis_subnet_group = elasticache.CfnSubnetGroup(
            self,
            "RedisSubnetGroup",
            description="Subnet group for Redis",
            subnet_ids=[subnet.subnet_id for subnet in vpc.private_subnets]
        )

        # ElastiCache Redis Cluster
        redis_cluster = elasticache.CfnCacheCluster(
            self,
            "searchengine-redis",
            engine="redis",
            cache_node_type="cache.t3.micro",  # Instance type
            num_cache_nodes=1,  # Number of nodes
            cache_subnet_group_name=redis_subnet_group.ref,  # Reference subnet group
            vpc_security_group_ids=[redis_sg.security_group_id],  # Attach security group
        )

        # Create an EC2 instance
        webServerInstance = ec2.Instance(self, "webServer",
            instance_type=ec2.InstanceType("t2.micro"),
            machine_image=ec2.AmazonLinuxImage(),
            vpc=vpc,
        )

         # Create an EC2 instance
        crawlerInstance = ec2.Instance(self, "crawler",
            instance_type=ec2.InstanceType("t2.micro"),
            machine_image=ec2.AmazonLinuxImage(),
            vpc=vpc,
        )

        # Create a Lambda function
        lambda_function = _lambda.Function(self, "file_parser",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="index.handler",
            code=_lambda.Code.from_asset("lambda"),
            vpc=vpc,
        )



app = cdk.App()
MyStack(app, "SearchEngineStack",
    env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
)
app.synth()