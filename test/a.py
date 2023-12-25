import os
import urllib.request

# print(os.path.abspath(__file__).(os.path.abspath(__file__),))
# print(os.path.dirname(__file__))

a = urllib.request.urlopen("https://h59q2.no-mad-world.club/link/5MoYFiqBWSryHGpE?clash=3&extend=1")
# print(a.read())
urllib.request.urlretrieve("https://h59q2no-mad-world.club/link/5MoYFiqBWSryHGpE?clash=3&extend=1", "a.yaml")