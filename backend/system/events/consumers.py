from . import pub_sub


@pub_sub.pattern_subscribe("players:*")
def test(data):
    print("running")
    print(data)
