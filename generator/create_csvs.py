"""Generate CSVs of random data for Warbler.

Students won't need to run this for the exercise; they will just use the CSV
files that this generates. You should only need to run this if you wanted to
tweak the CSV formats or generate fewer/more rows.
"""

import csv
from random import choice, randint, sample
from itertools import permutations
import requests
from faker import Faker


USERS_CSV_HEADERS = ['email', 'username', 'password', 'first_name', 'last_name', 'image_url', 'interests', 'hobbies', 'zip_code', 'coordinates', 'friend_radius_miles']
LIKES_CSV_HEADERS = ['liker_user_id', 'liked_user_id']
DISLIKES_CSV_HEADERS = ['disliker_user_id', 'disliked_user_id']

NUM_USERS = 20
NUM_LIKES = 10
NUM_DISLIKES = 10

fake = Faker()

# Generate random profile image URLs to use for users

image_urls = [
    f"https://randomuser.me/api/portraits/{kind}/{i}.jpg"
    for kind, count in [("lego", 10), ("men", 100), ("women", 100)]
    for i in range(count)
]

radius_choices = [15, 30, 5, 100]
zip_code_choices = ["95125", "95129", "95051", "95050", "94110", "94612"]
coordinates_choices = ["-121.9,37.32", "-121.98,37.305", "-121.98,37.35", "-121.96,37.35", "-122.42,37.76", "-122.27,37.81"]


with open('users.csv', 'w') as users_csv:
    users_writer = csv.DictWriter(users_csv, fieldnames=USERS_CSV_HEADERS)
    users_writer.writeheader()

    for i in range(NUM_USERS):
        users_writer.writerow(dict(
            email=fake.email(),
            username=fake.user_name(),
            image_url=choice(image_urls),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            password='$2b$12$Q1PUFjhN/AWRQ21LbGYvjeLpZZB6lfZ1BPwifHALGO6oIbyC3CmJe',
            hobbies=fake.sentence(),
            interests=fake.sentence(),
            zip_code=choice(zip_code_choices),
            coordinates=choice(coordinates_choices),
            friend_radius_miles=choice(radius_choices)
        ))


# Generate follows.csv from random pairings of users

with open('likes.csv', 'w') as likes_csv:
    all_pairs = list(permutations(range(1, NUM_USERS + 1), 2))

    users_writer = csv.DictWriter(likes_csv, fieldnames=LIKES_CSV_HEADERS)
    users_writer.writeheader()

    for liker_user_id, liked_user_id in sample(all_pairs, NUM_LIKES):
        users_writer.writerow(dict(liker_user_id=liker_user_id, liked_user_id=liked_user_id))

# Generate follows.csv from random pairings of users

with open('dislikes.csv', 'w') as dislikes_csv:
    all_pairs = list(permutations(range(1, NUM_USERS + 1), 2))

    users_writer = csv.DictWriter(dislikes_csv, fieldnames=DISLIKES_CSV_HEADERS)
    users_writer.writeheader()

    for disliker_user_id, disliked_user_id in sample(all_pairs, NUM_LIKES):
        users_writer.writerow(dict(disliker_user_id=disliker_user_id, disliked_user_id=disliked_user_id))