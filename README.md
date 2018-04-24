# Bhavacopy
Fetches Bhavcopy from BSE site and updates to redis. Also has a cherrypy server to list first 10 stocks. Has a search feature which reads from redis.

# Deploy
To run this, `redis` needs to be up on port `6379`.
For running cherrypy server command is `python server.py`. 
CherryPy will run at `http://localhost:8080/`
