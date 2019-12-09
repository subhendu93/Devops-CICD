import json
import requests

def gen_service_API():
    #Opening the Properties JSON file and loading on to a Python Dictionary
    with open('properties1.json') as f1:
      p_data = json.load(f1)
    #Open The Mashery_JSON File
    with open('Sample_Mashery_API_Calc.json') as f:
      data = json.load(f)
    if str(type(data)) == "<class 'list'>":
        data = data[0]

    with open('Static_np_MISDEV_Properties.json') as f:
        static_data = json.load(f)
    #API Name will end with TST, STG or PRD based on Organization
    data["name"] = p_data['Api_name']
    data["organization"]['id'] = static_data['env']['organization']['id']
    data["organization"]['name'] = static_data['env']['organization']['name']
    data["organization"]['parent'] = static_data['env']['organization']['parent']

    for i in range(len(data['endpoints'])):
        if len(p_data['endpoints']) == i:
            break
        if ('systemDomainAuthentication' in p_data['endpoints'][i]):
            if (p_data['endpoints'][i]['systemDomainAuthentication']['type'] == 'clientSslCert'):
                data['endpoints'][i]['systemDomainAuthentication']['username']=\
                    p_data['endpoints'][i]['name']['systemDomainAuthentication']['username']
                data['endpoints'][i]['systemDomainAuthentication']['certificate'] =\
                    p_data['endpoints'][i]['name']['systemDomainAuthentication']['certificate']
                data['endpoints'][i]['systemDomainAuthentication']['password'] =\
                    p_data['endpoints'][i]['name']['systemDomainAuthentication']['password']

            elif (p_data['endpoints'][i]['systemDomainAuthentication']['type'] == 'httpBasic'):
                data['endpoints'][i]['systemDomainAuthentication']['username'] = \
                    p_data['endpoints'][i]['name']['systemDomainAuthentication']['username']
                data['endpoints'][i]['systemDomainAuthentication']['password'] = \
                    p_data['endpoints'][i]['name']['systemDomainAuthentication']['password']

        data['endpoints'][i]['name'] = p_data['endpoints'][i]['name']
        if (data['endpoints'][i]['requestAuthenticationType']== "oauth"):
            data['endpoints'][i]["processor"]["preInputs"]["shared_token_spkey"]\
                = static_data['env']['oAuth']['shared_token_spkey']
        data['endpoints'][i]["trafficManagerDomain"] = p_data['env']['trafficManagerDomain']

        for j in range(len(data['endpoints'][i]["publicDomains"])):
            data['endpoints'][i]["publicDomains"][j]["address"] = \
                p_data['endpoints'][i]['publicDomains'][j]['address']

        # Change based on Organization
        for j in range(len(data['endpoints'][i]["systemDomains"])):
            data['endpoints'][i]["systemDomains"][j]["address"] = \
                p_data['endpoints'][i]['systemDomains'][j]['address']
    print("Json Data for services-API is prepared successfully")
    return json.dumps(data)

def create_API_service(data,headers):
    try :

        url = "https://dev1.api.biogen.com/serviceimp/np"
        res = requests.post(url, headers=headers, data=data)
        print(res.status_code)
        return res.json()

    except FileNotFoundError as e:
        print("The Required files are missing, please verify the file name and the PATH. {}".format(e))
    except ConnectionError:
        print("Please Check Your Connection")

def fetch_service_details(ser_d, headers):

    url = "https://dev1.api.biogen.com/serviceid/np"
    querystring = {"Api_ID": "{}".format(ser_d["id"])}
    ser_res = requests.get(url,headers=headers,params=querystring)
    print(ser_res)
    print(ser_res.json())
    return ser_res.json()

def gen_pkg_data(res):

    with open("Calc_Pkg_V1.json") as f:
        pkg_data = json.load(f)
    if str(type(pkg_data)) == "<class 'list'>":
        pkg_data = pkg_data[0]
    with open('properties1.json') as f1:
      prop_data = json.load(f1)
    with open('Static_np_MISDEV_Properties.json') as f:
        static_data = json.load(f)

    for d in range(len(pkg_data["plans"])):
        for t in range(len(pkg_data["plans"][d]["services"])):
            if (str(pkg_data["plans"][d]["services"][t]["name"]).startswith("API Oauth2")):
                pkg_data["plans"][d]["services"][t]["name"] = static_data['env']['oAuth']['name']
                pkg_data["plans"][d]["services"][t]["id"] = static_data['env']['oAuth']['id']
                pkg_data["plans"][d]["services"][t]["endpoints"] = [
                    {"name": "Client_Cred", "methods": [], "id": static_data['env']['oAuth']['Client_Cred']}]


            pkg_data["plans"][d]["services"][t]['name'] = res["name"]
            pkg_data["plans"][d]["services"][t]['id'] = res["id"]

            for i in range(len(pkg_data["plans"][d]["services"][t]["endpoints"])):
                pkg_data["plans"][d]["services"][t]["endpoints"][i]["name"]= res['endpoints'][i]["name"]
                pkg_data["plans"][d]["services"][t]["endpoints"][i]["id"]= res['endpoints'][i]["id"]

                for j in range(len(pkg_data["plans"][d]["services"][t]["endpoints"][i]["methods"])):
                    pkg_data["plans"][d]["services"][t]["endpoints"][i]["methods"][j]["id"] = res['endpoints'][i]["methods"][j]["id"]
                    pkg_data["plans"][d]["services"][t]["endpoints"][i]["methods"][j]["name"] = res['endpoints'][i]["methods"][j]["name"]
    print("Json Data for Package-API is prepared successfully")
    return json.dumps(pkg_data)

def post_pkg(pkg_data, headers):

    api_url_base = 'https://dev1.api.biogen.com/packageimp/np'
    pkg_res = requests.post(api_url_base, headers=headers, data=pkg_data)
    print("Package data posted and new API got created")
    print(pkg_res)
    return pkg_res.json()

def conditioning_API():
    file = "operation.json"
    with open(file) as f:
        check = json.load(f)
    headers = {
        'content-type': "application/json",
        'x-api-key': "*****************************"
    }
    if check['Operations']['Action'] == 'CREATE' and check['Operations']['Item'] == 'API_PACKAGE':
        service_data = gen_service_API()
        service_res = create_API_service(service_data, headers)
        res = fetch_service_details(service_res, headers)
        res = fetch_service_details(service_res, headers)
        pkg_data = gen_pkg_data(res)
        pkg_res=post_pkg(pkg_data,headers)
        print('Create API & Package Completed Successfully')
    # if check['Operations']['Action'] == 'CREATE' and check['Operations']['Item'] == 'ENDPOINT':
    #     print('Create new Endpoints for existing  API & Package is in progress...\n')
    #     res = get_token()
    #     create_endpoints(res)
    #
    # if check['Operations']['Action'] == 'CREATE' and check['Operations']['Item'] == 'METHOD':
    #     print('Create new Methods for existing  API & Package is in progress...')
    #     res = get_token()
    #     create_methods(res)
    # if check['Operations']['Action'] == 'MODIFY' and check['Operations']['Item'] == 'PLAN':
    #     print('Create Plan in progress...')
    #     res = get_token()
    #     create_plan(res)
    # if check['Operations']['Action'] == 'DELETE' and check['Operations']['Item'] == 'API':
    #     print('Create API & Package')
    #
    # if check['Operations']['Action'] == 'DELETE' and check['Operations']['Item'] == 'ENDPOINT':
    #     print('Create API & Package')
conditioning_API()
