# INSTALL 
## Docker
Run `docker run --publish 8095:5000 --detach --name component-use-plug synbiohub/plugin-visual-component-use` Check it is up using localhost:8095/sankey/status

## Python
Using python run `pip install -r requirements.txt` to install the requirements. 
Then run `FLASK_APP=app python -m flask run`. 
A flask module will run at localhost:5000/sankey/.
