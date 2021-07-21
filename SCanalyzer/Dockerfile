FROM public.ecr.aws/lambda/python:3.8

# RUN /var/lang/bin/python3.8 -m pip install --upgrade pip

RUN pip install SCanalyzer

COPY lambda.py .

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "lambda.handler" ]