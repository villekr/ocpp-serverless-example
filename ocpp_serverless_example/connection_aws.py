class AWSLambdaConnection:
    def __init__(self, *, apigateway_client, connection_id: str):
        self.apigateway_client = apigateway_client
        self.connection_id: str = connection_id

    async def send(self, message: str):
        print("send")
        self.apigateway_client.post_to_connection(
            Data=message, ConnectionId=self.connection_id
        )

    async def recv(self) -> str:
        print("recv")
        # recv is not utilized in event based handling
        raise NotImplementedError
