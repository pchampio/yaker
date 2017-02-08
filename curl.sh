# Token de drakirus
http GET localhost:8000/users/me/ 'Authorization:token 26325c8b4d0d94ab28a289a0fc7b20999aa6e62d'

# login
http GET localhost:8000/users/login/ -a drakirus:jkljkljkl

# Token de momo add
http POST localhost:8000/users/me/follower/add/ \
  follower=pierre \
  'Authorization:token 5be20c5fc5d62437e2811a9dce2b1123d8ba250c'

http POST localhost:8000/users/me/follower/add/ \
  follower=drakirus \
  'Authorization:token 5be20c5fc5d62437e2811a9dce2b1123d8ba250c'

# Token de drakirus add
http POST localhost:8000/users/me/follower/add/ follower=momo 'Authorization:token 26325c8b4d0d94ab28a289a0fc7b20999aa6e62d'

# Token de drakirus list
http GET localhost:8000/users/me/follower/ 'Authorization:token 26325c8b4d0d94ab28a289a0fc7b20999aa6e62d'

# Token de momo list
http GET localhost:8000/users/me/follower/ 'Authorization:token 5be20c5fc5d62437e2811a9dce2b1123d8ba250c'

# Token de momo delete
http post localhost:8000/users/me/follower/delete/ \
'authorization:token 5be20c5fc5d62437e2811a9dce2b1123d8ba250c' \
  follower=drakirus

http POST localhost:8000/users/register/ username=pierr2 email=pierr2@gmail.con password=jlkjkljkljkl


# Token de drakirus PlaySolo
http GET localhost:8000/game/playsolo/ 'Authorization:token 26325c8b4d0d94ab28a289a0fc7b20999aa6e62d'
