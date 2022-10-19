import os
import click

from Node.Node import Node


if __name__ == '__main__':
    click.clear()

    ip_to_synch = '192.168.175.128'

    server = Node()
    server.start_node(ip_to_synch)
