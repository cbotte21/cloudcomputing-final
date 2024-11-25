#!/usr/bin/env python3
import os
import aws_cdk as cdk
from aws_cdk import (
    aws_s3 as s3,
    aws_ec2 as ec2,
    aws_lambda as _lambda,
    aws_rds as rds,
    aws_elasticache as elasticache,
    aws_iam as iam,
    aws_sns as s3_notifications
)
from aws_cdk.aws_s3_notifications import LambdaDestination
from constructs import Construct

class MyStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a VPC
        vpc = ec2.Vpc(self, "searchengine-vpc", max_azs=2)

        # Create an S3 bucket
        bucket = s3.Bucket(self, "searchengine-data", versioned=True)

        # Create an RDS database
        db_name = "searchengine_database"
        db_instance = rds.DatabaseInstance(self, db_name,
            engine=rds.DatabaseInstanceEngine.postgres(version=rds.PostgresEngineVersion.VER_16_3),
            instance_type=ec2.InstanceType("db.t3.micro"),
            vpc=vpc,
            multi_az=False,
            allocated_storage=20,
            max_allocated_storage=100,
            publicly_accessible=False,
            vpc_subnets={
                "subnet_type": ec2.SubnetType.PRIVATE_WITH_NAT
            },
            database_name=db_name,
            credentials=rds.Credentials.from_generated_secret("postgres"),
        )
        db_endpoint = db_instance.db_instance_endpoint_address
        db_port = db_instance.db_instance_endpoint_port

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
        webServerInstance.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3ReadOnlyAccess")
        )
        webServerInstance.add_user_data(
            f"echo 'DB_HOST={db_endpoint}' >> /etc/environment",
            f"echo 'DB_PORT={db_port}' >> /etc/environment",
            f"echo 'DB_NAME={db_name}' >> /etc/environment",
            "sudo yum install -y gcc-c++ make",
            "curl -sL https://rpm.nodesource.com/setup_16.x | sudo -E bash -",
            "sudo yum install -y nodejs",
            "sudo yum install git -y",
            "git clone https://github.com/cbotte21/cloudcomputing-final app",
            "cd app/remixjs",
            "npm build",
            "npm start"
        )
        webServerInstance.role.add_to_policy(
            iam.PolicyStatement(
                actions=["rds:Connect", "elasticache:Connect"],
                resources=["*"]  # Replace with resource ARNs for more secure access
            )
        )

         # Create an EC2 instance
        crawlerInstance = ec2.Instance(self, "crawler",
            instance_type=ec2.InstanceType("t2.micro"),
            machine_image=ec2.AmazonLinuxImage(),
            vpc=vpc,
        )
        crawlerInstance.add_user_data(
            f"echo 'REDIS_HOST={redis_cluster.attr_redis_endpoint_address}' >> /etc/environment",
            f"echo 'REDIS_PORT=6379' >> /etc/environment", 
            f"echo 'S3_BUCKET_NAME={bucket.bucket_name}' >> /etc/environment",
            "sudo amazon-linux-extras install python3",
            "sudo yum install git -y",
            "git clone https://github.com/cbotte21/cloudcomputing-final app",
            "cd app/crawler",
            "pip install -r requirements.txt",
            # Run application
        )
        crawlerInstance.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess")
        )
        crawlerInstance.role.add_to_policy(
            iam.PolicyStatement(
                actions=["rds:Connect", "elasticache:Connect"],
                resources=["*"]
            )
        )

        lambda_function = _lambda.Function(self, "file_parser",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="index.handler",
            code=_lambda.Code.from_asset("lambda"),
            vpc=vpc,
            environment={
                "DB_HOST": db_instance.db_instance_endpoint_address,
                "DB_PORT": db_instance.db_instance_endpoint_port,
                "DB_NAME": db_name,
            },
        )
        lambda_function.add_to_role_policy(
            iam.PolicyStatement(
                actions=["s3:GetObject", "s3:PutObject"],
                resources=[f"{bucket.bucket_arn}/*"]
            )
        )
        lambda_function.add_to_role_policy(
            iam.PolicyStatement(
                actions=["rds:Connect"],
                resources=["*"]  # Replace with RDS resource ARN for more secure access
            )
        )

        # Lambda s3 trigger
        bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            LambdaDestination(lambda_function)
        )



app = cdk.App()
MyStack(app, "SearchEngineStack",
    env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
)
app.synth()