try:
    import requests
    import json

    api_url_base = 'https://api.mashery.com/v3/token'
    headers = {
        'cache-control': "no-cache",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {'client_id' : '8znbk4ecpvab46zczfjhqtvy',
            'client_secret' : 'h8Gb5Tes5B',
            'grant_type':'password',
            'username' : 'svc-apiDevops',
            'password'  :  '$vcDe^0p$',
            'scope': '14bc374a-d7dc-423f-95d7-94150a18d99a'}
    res = requests.post(api_url_base,headers=headers,data=payload)
    print(res)
    res = res.json()
    print(res["access_token"])

    api_url_base = "https://api.mashery.com/v3/rest/services"
    payload = {"fields": "name,id,plans.name,plans.id,plans.services.name,plans.services.id,plans.services.endpoints.id,plans.services.endpoints.name,plans.services.endpoints.methods.name,plans.services.endpoints.methods.id",
               "filter" : "name:Dummy_Calc_Pkg"}
    headers = {
        'authorization': "Bearer {}".format(res["access_token"]),
        'cache-control': "no-cache"
    }
    ser_res = requests.get(api_url_base, headers=headers, params=payload)
    pkg_data=ser_res.json()

    with open("operation.json") as f:
        oper_data = json.load(f)
    desired_data=[]

    for i in range(len(pkg_data)):

        for j in range(len(pkg_data[i]['plans'])):
            if pkg_data[i]['plans'][j]['name'] == oper_data['Operations']['AdditionalPLANName']:
                #if the Environment is not DEV .... Check....
                pkg_data[i]['plans'][j]["selfServiceKeyProvisioningEnabled"] = False
                desired_data.append(pkg_data[i]['plans'])





    api_url_base = "https://api.mashery.com/v3/rest/packages"
    payload = {"fields": "name,id,plans.name,plans.id,plans.services.name,plans.services.id,plans.services.endpoints.id,plans.services.endpoints.name,plans.services.endpoints.methods.name,plans.services.endpoints.methods.id",
               "filter" : "name:Dummy_Calc_Pkg"}
    headers = {
        'authorization': "Bearer {}".format(res["access_token"]),
        'cache-control': "no-cache"
    }
    res2 = requests.get(api_url_base, headers=headers, params=payload)
    res2 = res2.json()

    #here have to fetch the Target Package ID
    #print(res2)
    #print(res2["id"])
    api_url_base = "https://api.mashery.com/v3/rest/services/Target_API_Name"
    payload = {"fields": "endpoints.name,endpoints.id,endpoints.methods.id,endpoints.methods.name,name,id"}
    headers = {
        'authorization': "Bearer {}".format(res["access_token"]),
        'cache-control': "no-cache"
    }
    details = requests.get(api_url_base, headers=headers, params=payload)
    details = details.json()


    for d in range(len(desired_data)):
        for t in range(len(desired_data[d]["services"])):
            desired_data[d]["services"][t]['name'] = details["name"]
            desired_data[d]["services"][t]['id'] = details["id"]

            for i in range(len(desired_data[d]["services"][t]["endpoints"])):
                desired_data[d]["services"][t]["endpoints"][i]["name"] = details['endpoints'][i]["name"]
                desired_data[d]["services"][t]["endpoints"][i]["id"] = details['endpoints'][i]["id"]

                for j in range(len(desired_data[d]["services"][t]["endpoints"][i]["methods"])):
                    desired_data[d]["services"][t]["endpoints"][i]["methods"][j]["id"] = \
                        details['endpoints'][i]["methods"][j]["id"]
                    desired_data[d]["services"][t]["endpoints"][i]["methods"][j]["name"] = \
                        details['endpoints'][i]["methods"][j]["name"]
    print("Json Data for Package-Plan-API is prepared successfully")

    print(desired_data)

    # endpointPost = requests.post(api_url_base+"/{}/endpoints".format(resp[0]['id']),headers,data = json.dumps(desired_data))
    # print(endpointPost)

except ConnectionError as e:
    print("Please check your connection...")
    print("Error Details : {}".format(e))
