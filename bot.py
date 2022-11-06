from lib2to3.pgen2 import token
from unicodedata import name
from urllib import response

import json

import discord

from dotenv import load_dotenv
import os

import requests

import sqlite3

from requests.structures import CaseInsensitiveDict
con = sqlite3.connect("database.db")
cur = con.cursor()

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    
    if message.content.startswith('!help'):
        await message.channel.send('''
            \n¿Cómo usar el bot del mundial?
            \n1. Registrarse usando el comando *!registro* y utilizar el siguiente formato: *!registro NOMBRE CORREO PASSWORD PASSWORD*
            \nLa contraseña debe ser de minimo 8 caracteres.
            \n2. Iniciar sesión con el comando *!iniciar* y utilizar el siguiente formato: *!iniciar CORREO PASSWORD*
            \n*Comandos*:
            \n*!equipo* sirve para obtener la información de un equipo en particular y se utiliza así: *!equipo PAIS*
            \n*!partidos* sirve para obtener la lista de partidos para equipos específicos y se utilíza así: *!partidos PAIS*
            \n*!grupo* sirve para saber que equipos conforman los grupos A,B,C,D,E,F,G,H y se utilíza así: *!grupo LETRA*
        ''')

    if message.content.startswith('!registro'):
        discord_id = message.author.id
        name = message.content.split(' ')[1]
        email = message.content.split(' ')[2]
        password = message.content.split(' ')[3]
        password_match = message.content.split(' ')[4]
        data_to_json = f'{{ "name": "{name}", "email": "{email}", "password": "{password}", "passwordConfirm": "{password_match}" }}'
        json_body = json.loads(data_to_json)
        response = requests.post('http://api.cup2022.ir/api/v1/user', json=json_body)
        data_response = response.json()
        if data_response['status'] == "success":
            cur.execute("""
            INSERT INTO users (discord_id, name, email, password) VALUES (?, ?, ?, ?)
            """, [discord_id, name, email, password])
            con.commit()
            await message.channel.send('Usuario creado')
        else:
            await message.channel.send('Ha habido un error:(')
        
    if message.content.startswith('!iniciar'):
        email = message.content.split(' ')[1]
        password = message.content.split(' ')[2]
        data_to_json = f'{{ "email": "{email}", "password": "{password}" }}'
        json_body = json.loads(data_to_json)
        response = requests.post('http://api.cup2022.ir/api/v1/user/login', json=json_body)
        data_response = response.json()
        token = data_response["data"]["token"]
        discord_id = message.author.id
        if data_response["status"] == "success":
            cur.execute(f"""
            UPDATE users
            SET token = ?
            WHERE discord_id = {discord_id}
            """, [token])
            con.commit()
            await message.channel.send('Iniciaste sesión')
            await message.channel.send('*Debe iniciar sesión nuevamente después de transcurridas 24 horas*')
        else:
            await message.channel.send('Ha habido un error:(')
    
    if message.content.startswith('!equipo'):
        token = cur.execute(f"""
            SELECT token FROM users
            WHERE discord_id = {message.author.id}
            """)
        con.commit()
        def convertTuple(tup):
            str = ''.join(tup)
            return str
        response_db = token.fetchone()
        tokenporfin = convertTuple(response_db)
        headers =  CaseInsensitiveDict()
        headers["Accept"] = "application/json"
        headers["Authorization"] = f"Bearer {tokenporfin}"
        response = requests.get('http://api.cup2022.ir/api/v1/team', headers=headers)
        data_response = response.json()
        # print(data_response)
        def getTeam(name):
            for team in data_response["data"]:
                if team["name_en"] == name:
                    return team

        name = message.content.split(' ')[1].capitalize()
        

        equipito = getTeam(f'{name}')
        # print(equipito)
        if equipito is None:
            await message.channel.send('Revise el pais')
        else:
            await message.channel.send(f'''
                \n{equipito['flag']}
                ''')
            await message.channel.send(f'''
                \nPaís: {equipito['name_en']}
                \nFIFA Code: {equipito['fifa_code']}
                \nGrupo: {equipito['groups']}
                ''')
    
    if message.content.startswith('!partidos'):
        name = message.content.split(' ')[1].capitalize()

        token = cur.execute(f"""
            SELECT token FROM users
            WHERE discord_id = {message.author.id}
            """)
        con.commit()
        def convertTuple(tup):
            str = ''.join(tup)
            return str
        response_db = token.fetchone()
        tokenporfin = convertTuple(response_db)
        headers =  CaseInsensitiveDict()
        headers["Accept"] = "application/json"
        headers["Authorization"] = f"Bearer {tokenporfin}"
        response = requests.get('http://api.cup2022.ir/api/v1/match/', headers=headers)
        data_response = response.json()
        
        def get_matchs(name):
            for team in data_response["data"]:
                arg = [team["home_team_en"] == name]
                for t in arg:
                    if t == True:
                        
                        return (team['home_team_en'])
            
            for team in data_response["data"]:
                arg = [team["away_team_en"] == name]
                for t in arg:
                    if t == True:
                        
                        return (team['away_team_en'])

                        
        if get_matchs(name) is None:
            await message.channel.send('Revíse el país')
        else:
            for team in data_response["data"]:
                arg = [team["home_team_en"] == name]
                for t in arg:
                    if t == True:
                        date = (team['local_date'])
                        home_team = (team['home_team_en'])
                        away_team = (team['away_team_en'])
                        flag1 = (team['home_flag'])
                        flag2 = (team['away_flag'])
                        await message.channel.send(f'''
                        --------
                        \n{date}
                        ''')
                        await message.channel.send(f'''
                        \n{home_team}
                        ''')
                        await message.channel.send(f'''
                        {flag1}
                        ''')
                        await message.channel.send('VS')
                        await message.channel.send(f'''
                        \n{away_team}
                        ''')
                        await message.channel.send(f'''
                        {flag2}
                        ''')

            for team in data_response["data"]:
                arg = [team["away_team_en"] == name]
                for t in arg:
                    if t == True:
                        date = (team['local_date'])
                        home_team = (team['home_team_en'])
                        away_team = (team['away_team_en'])
                        flag1 = (team['home_flag'])
                        flag2 = (team['away_flag'])
                        await message.channel.send(f'''
                        --------
                        \n{date}
                        ''')
                        await message.channel.send(f'''
                        \n{home_team}
                        ''')
                        await message.channel.send(f'''
                        {flag1}
                        ''')
                        await message.channel.send('VS')
                        await message.channel.send(f'''
                        \n{away_team}
                        ''')
                        await message.channel.send(f'''
                        {flag2}
                        ''')

    if message.content.startswith('!grupo'):
        token = cur.execute(f"""
            SELECT token FROM users
            WHERE discord_id = {message.author.id}
            """)
        con.commit()
        def convertTuple(tup):
            str = ''.join(tup)
            return str
        response_db = token.fetchone()
        tokenporfin = convertTuple(response_db)
        headers =  CaseInsensitiveDict()
        headers["Accept"] = "application/json"
        headers["Authorization"] = f"Bearer {tokenporfin}"
        response = requests.get('http://api.cup2022.ir/api/v1/team', headers=headers)
        data_response = response.json()
        # print(data_response)
        group = message.content.split(' ')[1].capitalize()

        for team in data_response["data"]:
            arg = [team["groups"] == group]
            for t in arg:
                if t == True:
                    teams = team['name_en']
                    await message.channel.send(f'''
                    \n{teams}
                    ''')

client.run(os.environ['TOKEN'])