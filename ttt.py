async def main():
    print("listening to new pools....")
    async for websocket in connect(WSS):
        try:
            subscription_id = await subscribe_to_logs(
                websocket,
                RpcTransactionLogsFilterMentions(RaydiumLPV4),
                Finalized
            )
            async for i, signature in enumerate(process_messages(websocket, log_instruction)):  # type: ignore
                try:
                    tx_queue.append([signature, RaydiumLPV4])
                except SolanaRpcException as err:
                    print(err)
                    continue
        except (ProtocolError, ConnectionClosedError) as err:
            print(f"error:", err)
            continue
        except KeyboardInterrupt:
            if websocket:
                await websocket.logs_unsubscribe(subscription_id)