# rxr_webapp
web app built using dash that is built into a docker image for deployment to AWS

## Creating Docker Image
We create the docker image using the Dockerfile with the command below, note it must be run from the directory containing the Dockerfile as that is what the final . is referring to.

`docker build -t conorwaldron512/rxr_webapp:1.0 .`

## Running the Docker Image Locally
You can run the docker image locally (if you have Docker installed and you have created or pulled the image) with the command below
Note that we pick a random port (8888) on the host side but we must use the port 5000 on the container side as that was specified in app.py

`docker run -d -p 8888:5000 conorwaldron512/rxr_webapp:1.0`

If you then go to localhost:8888 you can see the web app working locally, the same as if you ran app.py from pycharm on your local machine

## Pushing the Image to a Public Repository
You can publish your image to a public docker image repository such as DockerHub with the commands below

`docker login`

`docker push conorwaldron512/rxr_webapp:1.0`

Now others can pull and run this image themselves with the single command

`docker run -d -p 8888:5000 conorwaldron512/rxr_webapp:1.0`

## Host on AWS ElasticBeanStalk
We can host this container (instance of the image) on AWS ElasticBeanStalk so others can access our website.
We use the Dockerrun.aws.json file to tell AWS where the image is and what ports we want.

* Go to AWS Elastic Bean Stalk
* pick create web app
* choose docker as the platform
* select 'upload your code' and select local file and upload your aws.json file.

When its running you will be given a url such as http://rxrwebapp-env.eba-irezwkxb.us-east-1.elasticbeanstalk.com/
