# Token de drakirus
http GET localhost:8000/users/me/ 'Authorization:token 	00725f100a321d8df433f5dc1c3aa62be7bc59b6'

# del notif
http DELETE localhost:8000/users/me/notif/1/ 'Authorization:token 	cdd3de3c02f62d41f126274e8d6a8cbc3b721d96'

# login
http GET localhost:8000/users/login/ -a drakirus:jkljkljkl

# Token de momo add
http POST localhost:8000/users/me/follower/add/ \
  follower=pierre \
  'Authorization:token adba5bbf082fa05b54ea7a89f426527069cbf9c2'

http POST localhost:8000/users/me/follower/add/ \
  follower=drakirus \
  'Authorization:token adba5bbf082fa05b54ea7a89f426527069cbf9c2'

# Token de drakirus add
http POST localhost:8000/users/me/follower/ follower=Akumok 'Authorization:token cdd3de3c02f62d41f126274e8d6a8cbc3b721d96'

# Token de drakirus list
http GET localhost:8000/users/me/follower/ 'Authorization:token cdd3de3c02f62d41f126274e8d6a8cbc3b721d96'

# Token de momo list
http GET localhost:8000/users/me/follower/ 'Authorization:token adba5bbf082fa05b54ea7a89f426527069cbf9c2'

# Token de momo delete
http post localhost:8000/users/me/follower/delete/ \
'authorization:token adba5bbf082fa05b54ea7a89f426527069cbf9c2' \
  follower=drakirus

http POST localhost:8000/users/register/ username=Akumok \
  email=pierrsdddf@gmail.con password=jlkjkljkljkl

http GET localhost:8000/users/login/ -a test:jkljkljkl
