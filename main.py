from client import BlumClient, sleep

client = BlumClient()

while True:
    client.update_balance()
    client.play_game()
    client.start_farming()
