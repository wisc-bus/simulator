#!/bin/bash
mkdir -p lambda_layers/python/lib/python3.8/site-packages
pip3 install -r requirements-layer.txt -t lambda_layers/python/lib/python3.8/site-packages/ 
cd lambda_layers
zip -r busSim-layer.zip .