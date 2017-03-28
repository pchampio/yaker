# Yaker
> Pierre Champion

L3 SPI Réalisation d'une application web a l'aide du Framework [Django](https://www.djangoproject.com/)

## Installation  

### Font-end  
les fichier dans [client-js](./client-js) doivent êtres asservi par un serveur
web  
j'utilise en développement `python3 -m http.server 8080` dans le repertoire
`client-js`

#### développement  
Les src import de l'[index.html](/client-js/index.html#L36) sont à modifier.  
Les variables `backend` dans [app.js](client-js/app.js#L55) sont à adapter.  


### Back-end  

le Back-end est situer dans [server](./server).  
le serveur Back-end est accessible sur le port `8080`  

#### développement  
Une base de données [Redis](https://redis.io/download) est nécessaire.
```
pip install -r requirements.txt
./manage.py makemigrations
./manage.py migrate
# start redis daemon
./manage.py runserver
```

#### Docker  
Juste `docker-compose up`


### Tests unitaire

L'application `users` dans Django est testé [test.py](/server/users/tests.py).  

```
Name                               Stmts   Miss  Cover
------------------------------------------------------
users.py                               0      0   100%
users/admin.py                        40     40     0%
users/cache_wrapper.py                26      6    77%
users/migrations/0001_initial.py       8      0   100%
users/migrations.py                    0      0   100%
users/models.py                       20     14    30%
users/serializers.py                  59      8    86%
users/urls.py                          3      0   100%
users/users_games_stats.py            25     18    28%
users/views.py                        84      3    96%
------------------------------------------------------
TOTAL                                265     89    66%
------------------------------------------------------
Ran 16 tests in 0.853s

OK
```
