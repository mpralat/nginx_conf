Simple project for creating nginx configuration.
### How to run
#### Depenedencies
Python, pip, NGINX and Python packages
```
pip install -r requirements.txt
```

The user needs to provide a path to the HTML file.
You can use the example file to see how the project works
```
python main.py -f index.html
```

#### How it works
* The user has to provide the path to the HTML site they want to run.
* If the vHost name is not provided, the default "server" is used.
* Preparing the directory from which we'll be serving the static files user has provided at
var/www/virtualhosts and copying the provided files there.
* Updating the NGINX conf file - including our .conf file in the main settings.
* Restarting the NGINX service to make sure the changes are applied.
* Creating the config file - creating a new virtual Host.
* Pinging google.com to get our IP address and adding the IP - url address mapping to
/etc/hosts
* Restarting NGINX again
* The user can now access their site at an address displayed in the console.

#### Additional info
* Because of several changes made in the system files, we have to provide the permission before
the script starts working. 
* The user is prompted to type in the sudo password before the scripts starts.
* The directory structure is based on Arch Linux architecture and might not work on other Linux distributions.
