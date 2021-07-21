FROM public.ecr.aws/lambda/python:3.8

# RUN /var/lang/bin/python3.8 -m pip install --upgrade pip

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY SCanalyzer/ ./SCanalyzer
COPY handlers/lambda.py .


# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "lambda.handler" ]