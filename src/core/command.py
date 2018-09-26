from abc import ABC, abstractmethod

from helpers.cmd import register_command

def command(cmd):
    register_command(cmd)
    # print(cmd.name) # TODO remove
    # command_list.append(cmd)
    # command_names.append(cmd.name.lower())
    return cmd

# Abstract parent class for all commands
class Command(ABC):
    def __init__(self, client):
        self.client = client

    @property
    @abstractmethod
    def name(self):
        pass

    @property
    @abstractmethod
    def description(self):
        pass

    # Returns True if user has the privileges for this command, False if not
    # Must be specifically implemented for command classes that have privilege requirements
    def check_privs(self, discord_user):
        return True

    @abstractmethod
    async def execute(self, msg, args):
        pass