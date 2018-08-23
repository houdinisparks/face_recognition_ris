
## Overview 
This is an early api prototype made for an automated visitor/employee registration system using facial
recognition which I had in mind. This api is built on top of Microsoft Face Api. It only requires a single api call for the following
- registering users
- identifying users
- deleting users

and also has the following additional features
- ensure user is only registered once in its own group (meaning Face Api only keeps a single person id
for the user)
- detect if the person in the image has registered in a certain person group is specified. if person group is not
specified, then it will check person against all person groups.

## Use Cases  
This api can be implemented over the various use cases: 
- Registering people and authenticating them using their faces

## How to deploy the api
**Prerequisites:**
- Microsoft Face Api Key
- Microsoft Azure Table Storage Key

### 1) Create an external environment config file
Create a file config.ini and save it to folder regident/config/config.ini.
Fill it with the contents below.
```
[DEFAULT]
FACEAPI_KEY = 
FACEAPI_BASEURL = https://<region>.api.cognitive.microsoft.com/face/v1.0
FACEAPI_REGION = 
AZURESTORAGE_KEY = 
AZURESTORAGE_CONNECTIONSTRING = 
AZURESTORAGE_ACCTNAME = 
AZURESTORAGE_TABLENAME = 
```

*still in development...*

## How to use the api
<still in dev>

## Future Implementations:
- Save faces to azure blob storage
- Have more friendly http error codes. Now is just using the Azure http error codes.

 