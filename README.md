# ocpp-serverless-example

Project to brainstorm how OCPP message handling could be done in event based and serverless faction using [mobilityhouse/ocpp](https://github.com/mobilityhouse/ocpp) library.

This example was tested with AWS API Gateway WebSocket API and AWS Lambda. It's worth noting the following:
- This repository doesn't contain full code&instructions how to deploy necessary AWS infrastructure
- AWS API Gateway doesn't support OCPP-J endpoint format at the moment