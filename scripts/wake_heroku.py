import requests

url="https://btc-inform.herokuapp.com/callback"


def notify():
  r = requests.get(url)
  print(r)