import os
from shutil import copyfile
import socket

SITES_AVAILABLE_PATH = '/etc/nginx/sites-available/'
SITES_ENABLED_PATH = '/etc/nginx/sites-enabled/'
LOGS_PATH = '/var/www/logs'

verbose = True
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

        #TODO whole static dirs + template

    def create_dir(self, path):
        '''
        Basic funtion for creating the directories. 
        '''
        if not os.path.exists(path):
            if verbose:
                print("Creating the directory : " + path)
            os.system("sudo mkdir -p " + path)

    def prepare_content_directory(self):
        '''
        Creates a directory for the vhost where the static files should be stored.
        Changes the directory permission and adds the html file added by the user.
        '''
        if verbose:
            print("Preparing the content directory and copying the files.")
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
                if verbose:
                    print("Adding the include line to the config file!")
                basic_content = basic_content.rstrip()[:-1] + "\n" + include_string + "\n}"
        # try:
        #     fdesc = os.open(NGINX_CONF_FILE, self.flags, 0o777)
        # finally:
        #     os.umask(self.umask_original)
        # with os.fdopen(fdesc, 'w') as fout:
        #     fout.write(basic_content)
        self.write_to_file(NGINX_CONF_FILE,'w', basic_content)

    def restart_nginx(self):
        os.system('/usr/sbin/nginx -s reload')
        #TODO check if every system has this one


    def prepare_config_content(self):
        # Create the content of the config file
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
        config_path = INCLUDE_VHOSTS + self.server_name + ".com.conf"
        if os.path.exists(config_path):
            os.system('sudo rm ' + config_path)
        # try:
        #     fdesc = os.open(config_path, self.flags, 0o777)
        # finally:
        #     os.umask(self.umask_original)
        # with os.fdopen(fdesc, 'w') as fout:
        #     fout.write()
        self.write_to_file(config_path, 'w', self.prepare_config_content())


    def add_to_hosts_file(self):
        # pings google to get our ip
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
        expression = '\n' + str(ip_address) + " " + "www." + self.server_name + ".com" + " " + self.server_name + ".com"
        with open("/etc/hosts") as hosts_file:
            basic_content = hosts_file.read()
            if not expression in basic_content:
                self.write_to_file('/etc/hosts', 'a', expression)

    def write_to_file(self, file_path, type, content):
        try:
            fdesc = os.open(file_path, self.flags, 0o777)
        finally:
            os.umask(self.umask_original)
        with os.fdopen(fdesc, type) as fout:
            fout.write(content)


    # def create_config_file(self):
    #     self.create_dir(SITES_AVAILABLE_PATH)
    #     self.create_dir(SITES_ENABLED_PATH)
    #
    #     fname = SITES_AVAILABLE_PATH + self.server_name + ".com.conf"
    #     content = self.prepare_config_content()
    #     try:
    #         fdesc = os.open(fname, self.flags, 0o777)
    #     finally:
    #         os.umask(self.umask_original)
    #     with os.fdopen(fdesc, 'w') as fout:
    #         fout.write(content)
    #
    #     os.chmod(fname, 0o660)
    #
    #
    # def create_vhost(self):
    #     self.create_config_file()
    #     self.create_dir(LOGS_PATH)
    #     os.chmod(LOGS_PATH, 0o660)
    #     # Creating symbolic links to sites-enabled path
    #     self.create_dir(SITES_ENABLED_PATH)
    #     src = SITES_AVAILABLE_PATH + self.server_name + ".com.conf"
    #     dst = SITES_ENABLED_PATH + self.server_name + ".com.conf"
    #     os.symlink(src, dst)

