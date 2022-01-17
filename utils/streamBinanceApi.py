from binance import ThreadedWebsocketManager

symbol = 'BTCUSDT'

twm = ThreadedWebsocketManager()
# start is required to initialise its internal loop
twm.start()

def handle_socket_message(msg):
    print(f"message type: {msg['e']}")
    print(msg)

twm.start_kline_futures_socket(callback=handle_socket_message, symbol=symbol)
depth_stream_name = twm.start_futures_socket(callback=handle_socket_message)

# some time later

# twm.stop_socket(depth_stream_name)