import os
from shutil import copyfile
import socket

ROOT_DIRECTORY = '/var/www/virtualhosts/'
NGINX_CONF_FILE = '/etc/nginx/nginx.conf'
INCLUDE_VHOSTS = '/etc/nginx/conf.d/'


class VirtualHost:
    def __init__(self, server_name, html_file_path, port=None):
        print("Creating a new vhost...")
        if port is None:
            self.port = 80
        else:
            self.port = int(port)
        self.server_name = server_name
        self.html_dir_path = ROOT_DIRECTORY + self.server_name + ".com"
        self.html_file_path = html_file_path
        self.flags = os.O_WRONLY | os.O_CREAT
        self.umask_original = os.umask(0)

    def create_dir(self, path):
        '''
        Basic funtion for creating the directories. 
        '''
        if not os.path.exists(path):
            print("Creating the directory : " + path)
            os.system("sudo mkdir -p " + path)

    def prepare_content_directory(self):
        '''
        Creates a directory for the vhost where the static files should be stored.
        Changes the directory permission and adds the html file added by the user.
        '''
        print("Preparing the content directory and copying the static files.")
        self.create_dir(self.html_dir_path)
        os.chmod(self.html_dir_path, 0o755)
        copyfile(self.html_file_path, self.html_dir_path + "/index.html")

    def edit_nginx_conf_file(self):
        '''
        Makes sure that the nginx.conf file has the include for the newly created directory.
        '''
        include_string = 'include \"' + INCLUDE_VHOSTS + '*.conf\";'
        with open(NGINX_CONF_FILE) as nginx_conf:
            basic_content = nginx_conf.read()
            if not include_string in basic_content:
                print("Adding the include line to the main NGINX config file!")
                basic_content = basic_content.rstrip()[:-1] + "\n" + include_string + "\n}"
        self.write_to_file(NGINX_CONF_FILE, 'w', basic_content)

    def restart_nginx(self):
        os.system('/usr/sbin/nginx -s reload')

    def prepare_config_content(self):
        '''
        Prepares the content of the basic configuration file.
        '''
        conf = "server { \naccess_log off;\nerror_log logs/" + self.server_name + ".com_error_log crit;\n\n"
        conf += "listen " + str(self.port) + ";\n\n"
        conf += "server_name " + self.server_name + ".com www." + self.server_name + ".com;\n\n"
        conf += "\tlocation / {\n\t\troot " + ROOT_DIRECTORY + self.server_name + ".com;\n"
        conf += "\t\tindex index.html index.htm;\n}\n"
        conf += "\tlocation ~* .(gif|jpg|jpeg|png|ico|wmv|3gp|avi|mpg|mpeg|mp4|flv|mp3|mid|js|css|wml|swf)$ {\n"
        conf += "\troot " + ROOT_DIRECTORY + self.server_name + ".com;\n"
        conf += "\t\texpires max;\n\t\tadd_header Pragma public;\n\t\tadd_header Cache-control \"public, must-revalidate, proxy-revalidate\";\n\t}\n}"
        return conf

    def create_vhost_definitions(self):
        '''
        Creates a configuration file for the server in the main INCLUDE_VHOSTS directory. 
        '''
        print("Creating the conf file...")
        config_path = INCLUDE_VHOSTS + self.server_name + ".com.conf"
        if os.path.exists(config_path):
            os.system('sudo rm ' + config_path)
        self.write_to_file(config_path, 'w', self.prepare_config_content())

    def add_to_hosts_file(self):
        '''
        Adds the line to the /etc/hosts file. First, pings google.com to get our current IP address.
        '''
        # pings google to get our ip
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
        print("Adding the server name to the /etc/hosts...")
        expression = '\n' + str(ip_address) + " " + "www." + self.server_name + ".com" + " " + self.server_name + ".com"
        with open("/etc/hosts") as hosts_file:
            basic_content = hosts_file.read()
            if not expression in basic_content:
                self.write_to_file('/etc/hosts', 'a', expression)

        print("You can now access your site at: " + self.server_name + ".com")

    def write_to_file(self, file_path, type, content):
        '''
        Writes to a file with desired permission.
        '''
        try:
            fdesc = os.open(file_path, self.flags, 0o777)
        finally:
            os.umask(self.umask_original)
        with os.fdopen(fdesc, type) as fout:
            fout.write(content)
