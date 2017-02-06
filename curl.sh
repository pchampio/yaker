# Token de drakirus
curl --silent localhost:8000/users/me/  -H 'Authorization: Token 26325c8b4d0d94ab28a289a0fc7b20999aa6e62d'

curl --silent localhost:8000/users/login/  -u drakirus:jkljkljkl

# Token de momo add
curl --silent -X POST localhost:8000/users/me/follower/add/  -H 'Authorization: Token 5be20c5fc5d62437e2811a9dce2b1123d8ba250c' \
-H "Content-Type: application/json" -d '{"follower": "drakirus"}'

curl --silent -X POST localhost:8000/users/me/follower/add/  -H 'Authorization: Token 5be20c5fc5d62437e2811a9dce2b1123d8ba250c' \
-H "Content-Type: application/json" -d '{"follower": "pierre"}'

# Token de drakirus add
curl --silent -X POST localhost:8000/users/me/follower/add/  -H 'Authorization: Token 26325c8b4d0d94ab28a289a0fc7b20999aa6e62d' \
-H "Content-Type: application/json" -d '{"follower": "momo"}'

# Token de drakirus list
curl --silent -X GET localhost:8000/users/me/follower/ -H 'Authorization: Token 26325c8b4d0d94ab28a289a0fc7b20999aa6e62d'

# Token de momo list
curl --silent -X GET localhost:8000/users/me/follower/ -H 'Authorization: Token 5be20c5fc5d62437e2811a9dce2b1123d8ba250c'

# Token de momo delete
curl --silent -X POST localhost:8000/users/me/follower/delete/  -H 'Authorization: Token 5be20c5fc5d62437e2811a9dce2b1123d8ba250c' \
-H "Content-Type: application/json" -d '{"follower": "drakirus"}'

curl --silent -X POST -F "username=pierr2" -F "email=piere2@gmail.con" -F "password=sdffffffffffffcfsdf" \
  "http://127.0.0.1:8000/users/register/"




# Token de drakirus PlaySolo
curl --silent -X GET localhost:8000/game/playsolo/ -H 'Authorization: Token 26325c8b4d0d94ab28a289a0fc7b20999aa6e62d'
