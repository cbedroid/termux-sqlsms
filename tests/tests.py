from random import randint
from time import sleep
from smstosql import SMS, Queued

results = []
sms = SMS().text_message()
print("SMS length", len(sms))


def maintest(one):
    # Test Queued time
    global results
    sleep(randint(1, 3))
    one.update(who=one.pop("sender", None))
    results.append(one)
    return one


# assert len(results) = len(sms)
