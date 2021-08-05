# AWS Authentication

Throughout this guide, [aws-vault](https://github.com/99designs/aws-vault) is used in order to assume the correct role for accessing our AWS environment. It is recommended to set something like this up, but you can get by with manual authentication or other tooling. Just ensure that the various AWS env vars are setup such that you can use the aws cli as the `developer` role. You can check this with the following command:

```bash
aws sts get-caller-identity
```

If everything is configured correctly this should return the details of the `developer` role (account `955696714113` at time of writing)

```json
{
    "UserId": <REDACTED>,
    "Account": "955696714113",
    "Arn": "arn:aws:sts::955696714113:assumed-role/developer/<REDACTED>"
}
```

# Running locally

You can run the server locally, however you will still need to be [authenticated with AWS](#aws-authentication). By default the app will go to s3 to fetch all of the collection logs on startup (stored in `var/cache`). For development you probably don't want to do that every time; this behaviour can be switched off by setting the environment variable `FETCH=False`.

```bash
aws-vault exec dl-dev -- make server
```

```bash
FETCH=False aws-vault exec dl-dev -- make server
```

# Building the infrastructure

Infrastructure is managed using [terraform](https://www.terraform.io/). It is split into two different "configurations" (`tf/base` and `tf/app`), so that core things such as the VPC, security groups, and load balancer endpoint are not put at risk when deploying new versions of the application. In future this core infrastructure could be separated further into it's own git repository.

Terraform's state is stored in s3, with locking provided by DynamoDB. This ensures that two people cannot apply terraform changes at the same time.

## Base infrastructure

The base terraform configuration includes:
 - VPC
 - SSL Certificate
 - Internet Gateway
 - Route Table + Associations
 - Security Groups
 - Subnets
 - Load Balancer

Due to a limitation of terraform, when deploying from scratch (i.e. there's not even a VPC), we need to create the vpc before the subnets can be built. We do this by using `-target=aws_vpc.dl_web_vpc` when creating the terraform plan:

```bash
cd tf/base
aws-vault exec dl-dev -- terraform plan -out=tfplan -target=aws_vpc.dl_web_vpc
```

Inspect the plan to make sure it's doing what you expect, then apply it with;

```bash
aws-vault exec dl-dev -- terraform apply tfplan
```

Complete the base deployment by running once again, without the `-target`:

```bash
aws-vault exec dl-dev -- terraform plan -out=tfplan
```

Again check the plan before going ahead with the apply:

```bash
aws-vault exec dl-dev -- terraform apply tfplan
```


## Application infrastructure

The app infrastructure includes:
 - ECS cluster, service & task
 - IAM roles & policies
 - Load Balancer listeners and target groups
 - Cloudwatch log group
 - Autoscaling group & associated launch configuration

The [base infrastructure](#base-infrastructure) must be fully built before you can deploy the application layer. The application layer terraform reads the remote state of the base configuration from s3, and uses it's outputs.

The application layer can be built in a single pass:

```bash
aws-vault exec dl-dev -- make plan
```

As before, check the output of the plan is as expected, then:

```bash
aws-vault exec dl-dev -- make apply
```


# Building the application container

The docker container can be built with the following command (NB this tag can be anything):

```bash
docker build -t dl_web_container .
```

**OPTIONAL**: You can test the newly built container locally. Note that we must explicitly tell docker to take the various AWS variables from our environment (set by aws-vault) and provide them to the container at runtime:

```bash
aws-vault exec dl-dev -- docker run -it -e AWS_REGION -e AWS_ACCESS_KEY_ID -e AWS_SESSION_TOKEN -e AWS_SECRET_ACCESS_KEY -p80:80 dl_web_container
```

Tag the image with the AWS ECR tag. This can be taken from the terraform output, like so:

```bash
aws-vault exec dl-dev -- terraform -chdir=tf/app output -json | jq --raw-output '.ecr_repository.value'
```

Which will return the ECR repository URL (same as the tag)

```
955696714113.dkr.ecr.eu-west-2.amazonaws.com/dl-web
```

Tag our build:

```bash
docker tag dl_web_container:latest 955696714113.dkr.ecr.eu-west-2.amazonaws.com/dl-web:latest
```

Authenticate with AWS in order for docker push to work:

```bash
aws-vault exec dl-dev -- aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin 955696714113.dkr.ecr.eu-west-2.amazonaws.com
```

Then we're finally ready to push the image:

```bash
docker push 955696714113.dkr.ecr.eu-west-2.amazonaws.com/dl-web
```

# Force redeployment

If you have pushed a new container, and want to force a redeployment of the ECS service in order to start using it, you can do so directly with aws and do not need to use terraform. The command is:

```bash
aws-vault exec dl-dev -- aws ecs update-service --force-new-deployment --service dl-web-service --cluster dl-web-cluster
```

# Logging

The containers are configured to send their logs to AWS Cloudwatch. The log group is called `/ecs/dl-web`.

Logging configuration can be found in `log_config.yml`. Here you can change log level of each of the loggers independently, change the log format, or redirect specific/all logs to file.
