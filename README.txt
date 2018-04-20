
Back end Requirements:
    - python3
    - tornado (for websockets)
    - sqlalchemy (for database)
    - flask (for rest api)

Front end Requirements:
    - Newest version Angular CLI version 5


Setup: Back end is in a virtual enviroment so it shouldn't need any setup, so just run npm install in the front end folder to install the node modules and everything should be ready to go.

To run backend: python3 /backend/app.py

To run frontend ng serve --open (seperate terminal window)


Because this isn't meant production yet (going to add trend analysis), the database is stored in memory and resets every time. To change that, declared a file name in the engine creation in /back-end/db_declerative.py. Also, the order book can be dynamically changed by changing the cryptocurrency pairs in pairs.py, but it's still buggy. Also GDAX sometimes has hiccups on their end when using websockets hosted on an http server, so you may need to refresh the page. 
