import pygtk
pygtk.require('2.0')
import gtk
import os.path
from xml.parsers import expat

class ConfigModel():
	
	def __init__(self, filepath):
		# init default values
		self.scope = "global"
		
		self.filepath = filepath
		self.sv = ConfigService(self, filepath)
		
	def load(self):
		self.sv.load()
		
	def save(self):
		self.sv.save()
		
	def set_scope(self,value):
		self.scope = value
		
	def get_scope(self):
		return self.scope

class ConfigService():
	def __init__(self, config, filepath):
		self.file = os.path.expanduser(str(filepath))
		self.config = config
		self.current_tag = None
	
	def load(self):
		
		dirname = os.path.dirname(self.file)
		if not os.path.isdir(dirname):
			os.makedirs(dirname)
		if not os.path.isfile(self.file):
			self.save(config,filepath)
		
		self.current_tag = None
		
		parser = expat.ParserCreate('UTF-8')
		parser.buffer_text = True
		parser.StartElementHandler = self.__start_element
		parser.EndElementHandler = self.__end_element
		parser.CharacterDataHandler = self.__character_data

		parser.ParseFile(open(self.file, 'rb'))
		
	def save(self):
		fp = file(self.file, "wb")
		fp.write('<?xml version="1.0" encoding="UTF-8"?>\n')
		scope_dump = '    <scope>%s</scope>\n' % self._escape(self.config.get_scope())
		settings = '<autocomplete>\n%s</autocomplete>\n' % scope_dump;
		fp.write(settings)
		fp.close()
		
	def _escape(self, xml):
		return xml.replace('&', '&amp;') \
					 .replace('<', '&lt;')  \
					 .replace('>', '&gt;')  \
					 .replace('"', '&quot;')
	
	def __start_element(self, tag, attrs):
		if tag == 'scope':
			self.current_tag = 'scope'
	def __end_element(self, tag):
		self.current_tag = None
	def __character_data(self, data):
		if self.current_tag == 'scope':
			self.config.set_scope(data)
	
class ConfigurationDialog(gtk.Dialog):
	def __init__(self,config,callback):
		gtk.Dialog.__init__(self,"Autocomplete settings",None,gtk.DIALOG_DESTROY_WITH_PARENT)
		self.set_resizable(False)
		self.config = config
		self.callback = callback
		
		close_button = self.add_button(gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE)
		close_button.grab_default()
		help_button = self.add_button(gtk.STOCK_HELP, gtk.RESPONSE_HELP)
		
		help_button.connect_object("clicked", self.show_help_dialog,None)
		close_button.connect_object("clicked", gtk.Widget.destroy,self)
		
		scope_box = gtk.HBox(False, 0)
		scope_box.set_border_width(25)
		
		scope_label = gtk.Label("Scope : ")
		global_scope_button = gtk.RadioButton(None, "global")
		local_scope_button = gtk.RadioButton(global_scope_button, "local for each window")
		
		if self.config.get_scope() == "global":
			global_scope_button.set_active(True)
		else:
			local_scope_button.set_active(True)
		
		# NOTE : if connecting to local_scope_button too, even with clicked, 
		# 		 the callback function is called twice.
		#		 So we just connect that button
		global_scope_button.connect_object("toggled", self.configuration_change,None)
		
		self.global_scope_button = global_scope_button;
		self.local_scope_button = local_scope_button;
		
		scope_box.pack_start(scope_label, True, True, 0)
		scope_box.add(global_scope_button)
		scope_box.add(local_scope_button)
		
		self.vbox.pack_start(scope_box, True, True, 0)
		scope_box.show_all()
	
	def get_config(self):
		return self.config
	
	def configuration_change(self,widget,data=None):
		if self.global_scope_button.get_active():
			self.config.set_scope("global")
		else:
			self.config.set_scope("local")
		
		self.config.save()
		self.callback()
	
	def show_help_dialog(self,widget,data=None):
		help_dialog = gtk.Dialog("Autocomplete plugin help")
		close_button = help_dialog.add_button(gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE)
		close_button.grab_default()
		close_button.connect_object("clicked", gtk.Widget.destroy, help_dialog)
		
		inner_box = gtk.HBox(False, 0)
		inner_box.set_border_width(40)
		help_label = gtk.Label("Help is coming soon...")
		
		inner_box.pack_start(help_label, True, True, 0)
		help_dialog.vbox.pack_start(inner_box, True, True, 0)
		help_dialog.show_all()