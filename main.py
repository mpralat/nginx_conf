from create_vhost import VirtualHost
import os
import sys
import subprocess
import argparse


def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-s',
        '--server_name',
        default='server'
    )
    parser.add_argument(
        '-f',
        '--html_file',
        required=True
    )

    return parser.parse_args()


def run_with_root():
    if os.geteuid() == 0:
        print("Program is running with needed privileges.")
    else:
        print("To use this program, you have to run it with root privileges.")
        subprocess.call(['sudo', 'python3', *sys.argv])
        exit(1)


def main():
    args = parse()
    vhost = VirtualHost(server_name=args.server_name, html_file_path=args.html_file)
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


if __name__ == "__main__":
    run_with_root()
    main()
