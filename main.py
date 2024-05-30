from client import BlumClient

client = BlumClient()

while True:
    client.update_balance()
    client.play_game()
    client.start_farming()
