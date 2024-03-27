# Use the AWS ECR Python image as the base image
FROM public.ecr.aws/lambda/python:3.11

# Copy requirements.txt
COPY requirements.txt ${LAMBDA_TASK_ROOT}

#install packages
RUN pip install -r requirements.txt

#Copy src files
COPY src/* ${LAMBDA_TASK_ROOT}

# add custom /tmp to lambda /tmp
#ADD src/tmp ${LAMBDA_TASK_ROOT}/tmp

# Set CMD to handler
CMD ["main.handler"]

