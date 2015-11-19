import sublime, sublime_plugin

class ShootCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		self.view.insert(edit, 0, "Hello, World!")

import sys
import os
import sublime
import sublime_plugin
import logging
import threading
import string
import random
import re
import json
sys.path.append(os.path.join(os.path.dirname(__file__), "socketIO"))
from socketIO_client import SocketIO, BaseNamespace

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class BaseCommand(sublime_plugin.TextCommand):

    def alertUser(msg):
        sublime.message_dialog(msg)


class LogwebCommand(BaseCommand):

    def run(self, edit):
        print("Running LogwebCommand")
        server = SocketServerThread()
        server.start()

class GetWordsCommand(BaseCommand):
	def run(self, edit):
		view = self.view
		r = sublime.Region(0, view.size())
		text = view.substr(r)
		words = text.split()
		print(words)
		view.run_command('find_logs', r)


class FindLogs(BaseCommand):
	def run(self, edit):
		view = self.view
		pattern = r'(util\.logweb\((.*)\);)'
		# These regions must be reversed so offsets dont get distorted.
		for region in reversed(list(view.find_all(pattern))):
			regString = view.substr(region)
			if "uuid" not in regString:
				matchString =  re.sub(pattern, r'util.logweb(\g<2>, {uuid:"' + id_generator() +'"});', regString)
				print("MATCH STRING: ", matchString)
				if matchString != regString:
					view.replace(edit,region,matchString)

class AnnotateLog(BaseCommand):
	def run(self, edit, **args):
		view = self.view
		logVal = args["value"]
		logId = args["uuid"]
		pattern = r'(util\.logweb\((.*)\);)'
		logRegions = view.find_all(pattern)
		for region in reversed(list(view.find_all(pattern))):
			regString = view.substr(region)
			if logId in regString:
				print("Found ID to annotate: ", regString)
				stringWithAnnotation = regString + " /* Annotated value: " + str(logVal) + " */"
				print("Replacing with: " + stringWithAnnotation)
				view.replace(edit,region, stringWithAnnotation)


class registerRegions(sublime_plugin.EventListener):
    # This method is called every time a file is saved (not only the first
    # time is saved)

    def on_pre_save(self, view):
        print('Searching for logs in file: ' + view.file_name())
        if view.window().extract_variables()['file_extension'] in ['html','pub', 'dict']:
	        view.run_command('find_logs')
        	pass
        else:
        	view.erase_regions('logRegions')
        # self.io.emit('message', "Received from client: ")



class SocketServerThread(threading.Thread):
    """A socket server to hold the connection."""

    def __init__(self):
        super(SocketServerThread, self).__init__()
        threading.Thread.__init__(self)

    def run(self):
        try:
            print("threading has begun")
            self.io = SocketIO('http://10.224.59.158', 3000, verify=False)
            print("Created new SocketServer")
            self.io.on('connected', self.handleClientMessage)
            self.io.on('reply', self.on_server_response)
            self.io.wait()
            return
        except (e):
            print("There was an error in the server thread.")
        print("threading has completed")
        # self.io.wait(seconds=10)

    def on_connect(self):
        print('[Connected]')

    def on_server_response(self, responseObj):
        print('Server response received', type(responseObj))
        # responseDict = json.loads(responseObj)
        sublime.active_window().active_view().run_command("annotate_log", responseObj)
        

    def handleServerMessage(self, *args):
        print("Server Message", args)

    def handleClientMessage(self, *args):
        print("Client Message", args)
