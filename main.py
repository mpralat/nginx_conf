from create_vhost import VirtualHost
import os
import sys
import subprocess


def main():
    print("main")
    vhost = VirtualHost(server_name="mysite1", html_file_path='index.html')
    # creating dirs and files in var/www/virtualhosts
    vhost.prepare_content_directory()
    # add include to nginx.conf
    vhost.edit_nginx_conf_file()
    # restart
    vhost.restart_nginx()
    # create conf files
    vhost.create_vhost_definitions()
    # restart nginx
    vhost.restart_nginx()
    # add ip
    vhost.add_to_hosts_file()



def run_with_root():
    if os.geteuid() == 0:
        print("Program is running with needed privileges.")
    else:
        print("To use this program, you have to run it with root privileges.")
        subprocess.call(['sudo', 'python3', *sys.argv])
        exit(1)

if __name__ == "__main__":
    run_with_root()
    main()