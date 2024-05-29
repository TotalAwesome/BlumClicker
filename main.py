from client import BlumClient, sleep

client = BlumClient()

while True:
    client.update_balance()
    client.play_game()
    sleep_time = client.start_farming()
    sleep(sleep_time)