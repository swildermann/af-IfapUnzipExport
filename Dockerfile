# To enable ssh & remote debugging on app service change the base image to the one below
# FROM mcr.microsoft.com/azure-functions/python:4-python3.9-appservice
FROM mcr.microsoft.com/azure-functions/python:4-python3.9

ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true

COPY requirements.txt /


RUN pip install -r /requirements.txt

RUN apt-get update && \
    apt-get install -y --no-install-recommends p7zip-full && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    7z -h

COPY . /home/site/wwwroot