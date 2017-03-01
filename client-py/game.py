#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests, getpass, json, pprint
import asyncio
import websockets

async def hello():
    async with websockets.connect('ws://localhost:8000/playsolo/?token='+token) as websocket:

        await websocket.send('{"test":1}')

            #  i = input("i :")
        for i in range(5):
            for j in range(5):

                t = input("play :")
                msg = '{"i":'+str(i)+',"j":'+str(j)+'}'
                await websocket.send(msg)

                print("\n")
                greeting = await websocket.recv()
                greeting = jsonDec.decode(greeting)
                pprint.pprint((greeting))
                print("\n")
                greeting.clear()

        print("\n")
        greeting = await websocket.recv()
        greeting = jsonDec.decode(greeting)
        pprint.pprint((greeting))
        print("\n")
        greeting.clear()


async def lobby():
    async with websockets.connect('ws://localhost:8000/playmulti/lobby/?token='+token+"&room=test") as websocket:

        #  await websocket.send('{"test":1}')

        greeting = await websocket.recv()
        greeting = jsonDec.decode(greeting)
        pprint.pprint((greeting))
# start

jsonDec = json.decoder.JSONDecoder()

menu = input('Menu :\n 1- login\n 2- register\n == ')
if menu != '1' and menu != '2':
    exit(1)

#  user = input('user : ')
#  pswd = getpass.getpass('Password:')

user = "drakirus"
pswd = "jkljkljkl"
if menu == '1':
    r = requests.get('http://localhost:8000/users/login/', auth=(user, pswd))
    print ("status : " + str(r.status_code))
    print ("reponse : " + str(r.text))
    if r.status_code != 200:
        exit(1)
    token = jsonDec.decode(r.text)['token']
elif menu == '2':
    email = input('email : ')
    r = requests.post('http://localhost:8000/users/register/', {"username":user, "email":email, "password":pswd})
    print ("status : " + str(r.status_code))
    print ("reponse : " + str(r.text))
    if r.status_code != 201:
        exit(1)
    token = jsonDec.decode(r.text)['token']


print ("\n")
print ("User session :")
r = requests.get('http://localhost:8000/users/me/', headers={"Authorization": "token " + token})
print ("status : " + str(r.status_code))
print ("reponse : " + str(r.text))
if r.status_code != 200:
    exit(1)

###############


while 1:
    print ("\n")
    menu = input('Coucou :\n 1- Add-follower\n 2- List-follower\n 3- Delete-follower\n 4- PlaySolo\n 5- CreateLobby\n == ')
    menu = int(menu)

    if menu == 1:
        user = input('user ? : ')
        r = requests.post('http://localhost:8000/users/me/follower/add/',
                          headers={"Authorization": "token " + token},data={"follower": user})
        print ("status : " + str(r.status_code))
        print ("reponse : " + str(r.text))

    if menu == 2:
        r = requests.get('http://localhost:8000/users/me/follower/',
                          headers={"Authorization": "token " + token})
        print ("status : " + str(r.status_code))
        print ("reponse : " + str(r.text))


    if menu == 3:
        user = input('user ? : ')
        r = requests.post('http://localhost:8000/users/me/follower/delete/',
                          headers={"Authorization": "token " + token},data={"follower": user})
        print ("status : " + str(r.status_code))
        print ("reponse : " + str(r.text))

    if menu == 4:
        asyncio.get_event_loop().run_until_complete(hello())

    if menu == 5:
        asyncio.get_event_loop().run_until_complete(lobby())
