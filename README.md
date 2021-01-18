# ocpp-serverless-example

Project to brainstorm how OCPP message handling could be done in event based and serverless faction using [mobilityhouse/ocpp](https://github.com/mobilityhouse/ocpp) library.

This repository contains two folders/packages: ocpp_serverless_example and ocpp_router_example.

## ocpp_serverless_example

PoC on how current ChargePoint functionality should be modified in order to run ocpp message handling in AWS serverless environment

This example was tested with AWS API Gateway WebSocket API and AWS Lambda. It's worth noting the following:
- This repository doesn't contain full code&instructions how to deploy necessary AWS infrastructure
- AWS API Gateway doesn't support OCPP-J endpoint format at the moment

## ocpp_router_example

Drafting ideas on how ocpp library interface should be designed to allow event based message handling.
