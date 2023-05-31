import profile
from ssl import SSLSyscallError
from traceback import print_exc
from tracemalloc import start
import requests
import json
from collections import defaultdict
from datetime import *
import re

with open('credentials.txt', "r") as f:
    content = f.readlines()
    SECRET_API = content[0].replace("\n",'')
    DATABASE_ID = content[1].replace("\n",'')
    USER = content[3].replace("\n",'')
    PASSWORD = content[4].replace("\n",'')
    day = content[2].replace("\n",'')


def get_schedule(date,identifiant, mdp):
    global Data
   
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
    }

    data = {
    'data': '{"identifiant": '+'"'+identifiant+'"'+',"motdepasse": '+'"'+mdp+'"'+'}'
    }

    response = requests.post('https://api.ecoledirecte.com/v3/login.awp', headers=headers,data=data)

    json_object = json.loads(response.text)

    token = json_object["token"]
    ###########################################
    data = json_object['data']
    accounts=data["accounts"]
    accounts = accounts[0]
    Id = accounts["id"]



    ####################################

    headers = {
        'x-token': token,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
        "dateDebut": "2022-02-28",
        "dateFin": "2022-03-06",
        
    }
    params = (
        ('verbe', 'get'),
        ('v', '4.2.3'),
    )
    data = {
    'data': '{\n    "dateDebut": "'+date+'",\n    "dateFin": "'+date+'",\n    "avecTrous": true\n}'
    
    }


   
    response = requests.post('https://api.ecoledirecte.com/v3/E/'+str(Id)+'/emploidutemps.awp?verbe=get&v=4.5.1', headers=headers, data=data,params=params)
    json_data = json.loads(response.content)
    json_data= json_data["data"]
    



    Data = defaultdict(list)

    for x in range(len(json_data)):
        fetch_sched = json_data[x]

        start_date = fetch_sched["start_date"].split(" ")
        start_date=start_date[1]

        end_date = fetch_sched["end_date"].split(" ")
        end_date=end_date[1]
        if fetch_sched["matiere"] == ' ':
            #\u200
            Data[start_date].append("\n")
            Data[start_date].append("")
            Data[start_date].append(start_date)
            Data[start_date].append(end_date)
            Data[start_date].append(fetch_sched["isAnnule"])
            Data[start_date].append("")

        else:
            Data[start_date].append(fetch_sched["matiere"])
            Data[start_date].append(fetch_sched["prof"])
            Data[start_date].append(start_date)
            Data[start_date].append(end_date)
            Data[start_date].append(fetch_sched["isAnnule"])
            Data[start_date].append(fetch_sched["salle"])

    Data = sorted(Data.items())    

    


##############################################################


get_schedule(day,USER,PASSWORD)

cours = {}
for elem in Data:
    if elem[1][0] != "\n":
        cours[elem[1][0]] = elem[1][1], elem[1][2], elem[1][3], elem[1][5], elem[1][4]

classes = list(cours.keys())


headers = {
    'Authorization': f'Bearer {SECRET_API}',
    'Content-Type': 'application/json',
    'Notion-Version': '2022-06-28',
}


for i in range(len(classes)):

    prof = cours.get(classes[i])[0]
    start = cours.get(classes[i])[1]
    end = cours.get(classes[i])[2]
    salle = cours.get(classes[i])[3]
    isAnnule = cours.get(classes[i])[4]

    if salle == "":
        resalle = 0
    else:
        resalle = int(re.findall(r'\d+', salle)[0])
    
    if resalle != 0:
        date_start = str(day)+"T"+str(start)
        date_end = str(day)+"T"+str(end)

        json_data = {
            'parent': {
                'type': 'database_id',
                'database_id': f'{DATABASE_ID}',
            },
            'properties': {
                'Name': {
                    'type': 'title',
                    'title': [
                        {
                            'type': 'text',
                            'text': {
                                'content': f'{classes[i]}',
                            },
                        },
                    ],
                },
                'Salle': {
                    'type': 'number',
                    'number': resalle,
                },
                'Prof': {
                    "type": "rich_text",
                    "rich_text": [
                            {
                            "type": "text",
                            "text": {
                                "content": f"{prof}",
                                "link": None
                            },
                            "annotations": {
                                "bold": False
                            }
                        }
                    ]
                },
                'Date': {
                    'type': 'date',
                    'date': {
                        'start': f"{date_start}",
                        'end': f'{date_end}'
                        #'time_zone': "Europe/Paris"
                    },
                },
            },
        }



        response = requests.post('https://api.notion.com/v1/pages', headers=headers, json=json_data)
print("done")
    
