#!/bin/bash
set -v
set -e
image="python39-matplotlib-lambda"
account=$(aws sts get-caller-identity --query Account --output text)
region="ap-southeast-1"
fullname="${account}.dkr.ecr.${region}.amazonaws.com/${image}:latest"

aws ecr describe-repositories --repository-names "${image}" --region ${region}  > /dev/null 2>&1

if [ $? -ne 0 ]
then
    aws ecr create-repository --repository-name "${image}"  --region ${region}  > /dev/null
fi

# Get the login command from ECR and execute it directly (for our own registry and for the base image registry)
aws ecr get-login-password --region ${region} | sudo docker login --username AWS --password-stdin ${account}.dkr.ecr.${region}.amazonaws.com

# Build the docker image locally and then push it to ECR with the full name.
cd container
echo "Building image with name ${image}"
sudo docker build -t ${image} .
sudo docker tag ${image} ${fullname}

echo "Pushing image to ECR ${fullname}"
sudo docker push ${fullname}

# Writing the image name to let the calling process extract it without manual intervention:
echo "${fullname}" > ecr_image_fullname.txt
