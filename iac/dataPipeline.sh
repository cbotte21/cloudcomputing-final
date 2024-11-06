#!/bin/bash

aws lambda invoke --function-name dataPipeline --payload '{"n": 1}' --cli-binary-format raw-in-base64-out output.json

