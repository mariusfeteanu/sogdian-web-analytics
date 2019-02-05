## Prerequisites

You need to set the following env variables for the commands below to work. If using docker for development, you need to set them before you start the container.

```bash
export AWS_PROFILE=admin-dev
export AWS_DEFAULT_REGION=eu-west-1
export STACK_PREFIX=sogdian-dev
```

or, for Windows Powershell:

```bash
$env:AWS_PROFILE="admin-dev"
$env:AWS_DEFAULT_REGION="eu-west-1"
$env:STACK_PREFIX="sogdian-dev"
```

The variables above are specific to your deployment.


All these commands below are tested on Linux. If you have another OS, you can try to make that work yourself or you can use the docker dev environment included with the project.
  - `docker-compose build`
  - `docker-compose.exe run devenv`


The rest of this doc assumes that you have your base infra setup as detailed in it's own repo. It also assumes you have access to AWS and an IAM user with access to code commit.

## Deployment

If the pre-requisites are met, you can just push the code and the pipeline you setup earlier should take care of the deployment.

```bash
# Remove current mappings (e.g. github)
git remote rm origin
# Add new origin
git remote add origin https://git-codecommit.$AWS_DEFAULT_REGION.amazonaws.com/v1/repos/$STACK_PREFIX-web-analytics
git remote -v
# Push to your own codecommit repo. Insert here password from step 1.
git push --set-upstream origin master
```

You can now wait for code pipeline to deploy:
```bash
sleep 30  # wait 30 secs to give the pipeline time to react to the build
aws cloudformation wait stack-create-complete --stack-name web-analytics
```

And then retrieve the api key you can use to post:
```bash
aws apigateway get-api-keys --include-value | jq '.items[] | select(.name=="dev_collect_web_events") | .value' -r
```

And the url to post to:
```bash
aws apigateway get-rest-apis | jq '.items[] | select(.name=="api-collect-web-events") | .id' -r | xargs -L1 -I{} echo "https://{}.execute-api.eu-west-1.amazonaws.com/dev/log"
```

You can then use [Postman](https://www.getpostman.com/) to post a json event to that url, setting the api key from before in the `x-api-key` header.
