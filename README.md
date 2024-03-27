# aws-wafr-automation-suite
A suite of services designed to enhance the AWS WAFR outputs

This is not for sale...yet

Authenticate Docker with ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 720050647263.dkr.ecr.us-east-1.amazonaws.com

Tag docker image
docker tag wafr-image:test 720050647263.dkr.ecr.us-east-1.amazonaws.com/wafr-bot-images:latest

docker push to ecr
docker push 720050647263.dkr.ecr.us-east-1.amazonaws.com/wafr-bot-images:latest

Test API Params
getWafrReport?workload_id=bcc6bf1d68218b99986acca5ffb711f7&milestone_number=1&customer=Test