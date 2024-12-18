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
    aws_sns as s3_notifications,
    SecretValue,
    Duration
)
from aws_cdk.aws_s3_notifications import LambdaDestination
from constructs import Construct

class MyStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        key_pair = ec2.KeyPair.from_key_pair_name(self, 'KeyPair', 'Cody')

        vpc = ec2.Vpc(self, "searchengine-vpc", 
            max_azs=2,  # Number of Availability Zones to use
            enable_dns_support=True,
            enable_dns_hostnames=True,
            nat_gateways=1,  # No NAT Gateway (since we're using public subnets)
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="public-subnet",
                    subnet_type=ec2.SubnetType.PUBLIC,  # Public subnet
                    cidr_mask=24,
                ),
                # Optionally, you can add private subnets if needed
                ec2.SubnetConfiguration(
                    name="private-subnet",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,  # Private subnet with NAT gateway (if you need one)
                    cidr_mask=24,
                ),
            ]
        )

        # Create an S3 bucket
        bucket = s3.Bucket(self, "searchengine-data", versioned=True)

        # Create an RDS database
        db_user = "searchengineuser"
        db_password = "Superpassword123"
        db_name = "searchengine_database"
        parameter_group = rds.ParameterGroup(self, "RDSParameterGroup",
            engine=rds.DatabaseInstanceEngine.postgres(version=rds.PostgresEngineVersion.VER_16_3),
            parameters={
                "rds.force_ssl": "0"  # Disable SSL enforcement
            }
        )
        db_instance = rds.DatabaseInstance(self, db_name,
            engine=rds.DatabaseInstanceEngine.postgres(version=rds.PostgresEngineVersion.VER_16_3),
            instance_type=ec2.InstanceType("t3.micro"),
            vpc=vpc,
            parameter_group=parameter_group,
            multi_az=False,
            allocated_storage=20,
            max_allocated_storage=100,
            publicly_accessible=False,
            database_name=db_name,
            credentials = rds.Credentials.from_password(db_user, SecretValue.unsafe_plain_text(db_password)),
        )
        db_endpoint = db_instance.instance_endpoint.socket_address.split(":")[0]
        db_port = str(db_instance.db_instance_endpoint_port)


        # Security Group for ElastiCache
        redis_sg = ec2.SecurityGroup(
            self,
            "RedisSG",
            vpc=vpc,
            description="Allow Redis access from within the VPC",
            allow_all_outbound=True,
        )

        # Allow inbound traffic on the Redis port (6379) from resources in the same VPC
        redis_sg.add_ingress_rule(
            ec2.Peer.ipv4(vpc.vpc_cidr_block),  # Restrict to the VPC CIDR block
            ec2.Port.tcp(6379),
            "Allow Redis traffic from VPC"
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
            machine_image=ec2.AmazonLinuxImage(
                generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2023  
            ),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),  # Use public subnet
            associate_public_ip_address=True,
            key_pair=key_pair,
        )
        webServerInstance.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3ReadOnlyAccess")
        )
        webServerInstance.add_user_data(
            "sudo yum install -y gcc-c++ make",
            "curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -", 
            "sudo yum install nodejs -y",
            "sudo yum install -y nodejs@latest", 
            "sudo npm install -g npm@latest",  
            "sudo yum install git -y",
            "git clone https://github.com/cbotte21/cloudcomputing-final app",
            "cd app/remixjs",
            "npm install",
            "npm run build > /var/log/remixjs_build_output.log 2>&1",
            f"export PG_HOST={db_endpoint}",
            f"export PG_PORT={db_port}",
            f"export PG_DATABASE={db_name}",
            f"export PG_USER={db_user}",
            f"export PG_PASSWORD={db_password}",
            "npm run start > /var/log/remixjs_output.log 2>&1"
        )
        webServerInstance.role.add_to_policy(
            iam.PolicyStatement(
                actions=["rds:Connect", "elasticache:Connect"],
                resources=["*"]  # Replace with resource ARNs for more secure access
            )
        )
        # Open SSH port (22) in security group to allow inbound SSH connections
        webServerInstance.connections.allow_from_any_ipv4(
            ec2.Port.tcp(22),  # Allow SSH access
            "Allow SSH access from anywhere"
        )

        # Open HTTP port (80) for web traffic
        webServerInstance.connections.allow_from_any_ipv4(
            ec2.Port.tcp(80),  # Allow HTTP traffic
            "Allow HTTP access from anywhere"
        )

         # Create an EC2 instance
        crawlerInstance = ec2.Instance(self, "Crawler",
            instance_type=ec2.InstanceType("t2.micro"),
            machine_image=ec2.AmazonLinuxImage(),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),  # Use public subnet
            associate_public_ip_address=True,
            key_pair=key_pair,
        )
        crawlerInstance.add_user_data(
            f"echo 'REDIS_HOST={redis_cluster.attr_redis_endpoint_address}' >> /etc/environment",
            f"echo 'REDIS_PORT=6379' >> /etc/environment", 
            f"echo 'S3_BUCKET_NAME={bucket.bucket_name}' >> /etc/environment",
            "source /etc/environment",
            "sudo yum install -y python38",
            "sudo python3 -m pip install --upgrade pip",
            "sudo yum install git -y",
            "git clone https://github.com/cbotte21/cloudcomputing-final app",
            "cd app/crawler",
            "python3 -m pip install -r requirements.txt",
            "cd src",
            "env REDIS_HOST=${REDIS_HOST} REDIS_PORT=${REDIS_PORT} S3_BUCKET_NAME=${S3_BUCKET_NAME} /usr/local/bin/scrapy crawl crawl > /var/log/scrapy_output.log 2>&1"
        )
        crawlerInstance.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess")
        )
        crawlerInstance.role.add_to_policy(
            iam.PolicyStatement(
                actions=["elasticache:Connect"],
                resources=["*"]
            )
        )
        # Open SSH port (22) in security group to allow inbound SSH connections
        crawlerInstance.connections.allow_from_any_ipv4(
            ec2.Port.tcp(22),  # Allow SSH access
            "Allow SSH access from anywhere"
        )

        lambda_function = _lambda.Function(self, "FileParser",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="index.handler",
            code=_lambda.Code.from_asset("lambda/lambda.zip"),
            vpc=vpc,
            environment={
                "PG_HOST": db_endpoint,
                "PG_PORT": db_port,
                "PG_DATABASE": db_name,
                "PG_USER": db_user,
                "PG_PASSWORD": db_password,
                "S3_BUCKET_NAME": bucket.bucket_name
            },
            timeout= Duration.seconds(5),
            memory_size=256
        )
        lambda_function.add_to_role_policy(
            iam.PolicyStatement(
                actions=["s3:GetObject", "s3:PutObject"],
                resources=[f"{bucket.bucket_arn}/*"]
            )
        )

        # Add security group rule for EC2 to access RDS
        db_instance.connections.allow_default_port_from(webServerInstance, "Allow EC2 to connect to RDS")

        # Add security group rule for Lambda to access RDS
        db_instance.connections.allow_default_port_from(lambda_function, "Allow Lambda to connect to RDS")

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