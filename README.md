# fast-api-task
Two task done using fast api

Task 1

task1.py file contains code for api register and list.

task1 uses 2 databases mongodb and postgres sql

register api(Post request)
/register

parameters 
in body as formdata give values for 
first_name
email
password
phone
profile_picture

profile_picture should send as file in postman

list api(get request)

/users

it lists all the users registered

task2

task2.py file contains code for api register and list.

task2 uses postgres sql as databases  

register api(Post request)
/register

parameters 
in body as formdata give values for 
first_name
email
password
phone
profile_picture

profile_picture should send as file in postman

list api(get request)

/users

it lists all the users registered


list users according to id

/user/{user_id}


user id is integer number which is the id of the registered data



to run the server 
use

uvicorn <filename>:app --reload

eg: uvicorn test2:app --reload