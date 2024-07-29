# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: tools.proto
# Protobuf Python Version: 5.26.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0btools.proto\"<\n\x07\x43ontent\x12#\n\tmime_type\x18\x01 \x01(\x0e\x32\x10.ContentMimeType\x12\x0c\n\x04\x64\x61ta\x18\x02 \x01(\x0c\"8\n\x17WebBrowserCommandOutput\x12\r\n\x05index\x18\x01 \x01(\x05\x12\x0e\n\x06output\x18\x02 \x01(\t\"6\n\x16WebBrowserCommandError\x12\r\n\x05index\x18\x01 \x01(\x05\x12\r\n\x05\x65rror\x18\x02 \x01(\t\"W\n\x0fWebBrowserInput\x12$\n\x04type\x18\x01 \x01(\x0e\x32\x16.WebBrowserCommandType\x12\x10\n\x08selector\x18\x02 \x01(\t\x12\x0c\n\x04\x64\x61ta\x18\x03 \x01(\t\"2\n\x10WebBrowserButton\x12\x10\n\x08selector\x18\x01 \x01(\t\x12\x0c\n\x04text\x18\x02 \x01(\t\"6\n\x14WebBrowserInputField\x12\x10\n\x08selector\x18\x01 \x01(\t\x12\x0c\n\x04text\x18\x02 \x01(\t\"7\n\x15WebBrowserSelectField\x12\x10\n\x08selector\x18\x01 \x01(\t\x12\x0c\n\x04text\x18\x02 \x01(\t\"9\n\x17WebBrowserTextAreaField\x12\x10\n\x08selector\x18\x01 \x01(\t\x12\x0c\n\x04text\x18\x02 \x01(\t\"=\n\x0eWebBrowserLink\x12\x10\n\x08selector\x18\x01 \x01(\t\x12\x0c\n\x04text\x18\x02 \x01(\t\x12\x0b\n\x03url\x18\x03 \x01(\t\"\xf3\x02\n\x10WebBrowserOutput\x12\x0b\n\x03url\x18\x01 \x01(\t\x12\r\n\x05title\x18\x02 \x01(\t\x12\x0c\n\x04html\x18\x03 \x01(\t\x12\x0c\n\x04text\x18\x04 \x01(\t\x12\x12\n\nscreenshot\x18\x05 \x01(\x0c\x12\"\n\x07\x62uttons\x18\x06 \x03(\x0b\x32\x11.WebBrowserButton\x12%\n\x06inputs\x18\x07 \x03(\x0b\x32\x15.WebBrowserInputField\x12\'\n\x07selects\x18\x08 \x03(\x0b\x32\x16.WebBrowserSelectField\x12+\n\ttextareas\x18\t \x03(\x0b\x32\x18.WebBrowserTextAreaField\x12\x1e\n\x05links\x18\n \x03(\x0b\x32\x0f.WebBrowserLink\x12)\n\x07outputs\x18\x0b \x03(\x0b\x32\x18.WebBrowserCommandOutput\x12\'\n\x06\x65rrors\x18\x0c \x03(\x0b\x32\x17.WebBrowserCommandError\"\x99\x02\n\x17WebBrowserSessionConfig\x12\x10\n\x08init_url\x18\x01 \x01(\t\x12\x1d\n\x15terminate_url_pattern\x18\x02 \x01(\t\x12\x14\n\x0csession_data\x18\x03 \x01(\t\x12\x0f\n\x07timeout\x18\x04 \x01(\x05\x12\x11\n\ttext_only\x18\x05 \x01(\x08\x12\x11\n\thtml_only\x18\x06 \x01(\x08\x12\r\n\x05\x62rief\x18\x07 \x01(\x08\x12\x17\n\x0fpersist_session\x18\x08 \x01(\x08\x12\x1a\n\x12\x63\x61pture_screenshot\x18\t \x01(\x08\x12\x13\n\x0binteractive\x18\n \x01(\x08\x12\x14\n\x0crecord_video\x18\x0b \x01(\x08\x12\x11\n\tskip_tags\x18\x0c \x01(\x08\"H\n\x11WebBrowserSession\x12\x0e\n\x06ws_url\x18\x01 \x01(\t\x12\x14\n\x0csession_data\x18\x02 \x01(\t\x12\r\n\x05video\x18\x03 \x01(\x0c\"g\n\x11WebBrowserRequest\x12\x30\n\x0esession_config\x18\x01 \x01(\x0b\x32\x18.WebBrowserSessionConfig\x12 \n\x06inputs\x18\x02 \x03(\x0b\x32\x10.WebBrowserInput\"}\n\x12WebBrowserResponse\x12#\n\x07session\x18\x01 \x01(\x0b\x32\x12.WebBrowserSession\x12\x1f\n\x05state\x18\x02 \x01(\x0e\x32\x10.WebBrowserState\x12!\n\x06output\x18\x03 \x01(\x0b\x32\x11.WebBrowserOutput*\xce\x02\n\x0f\x43ontentMimeType\x12\x08\n\x04TEXT\x10\x00\x12\x08\n\x04JSON\x10\x01\x12\x08\n\x04HTML\x10\x02\x12\x07\n\x03PNG\x10\x03\x12\x08\n\x04JPEG\x10\x04\x12\x07\n\x03SVG\x10\x05\x12\x07\n\x03PDF\x10\x06\x12\t\n\x05LATEX\x10\x07\x12\x0c\n\x08MARKDOWN\x10\x08\x12\x07\n\x03\x43SV\x10\t\x12\x07\n\x03ZIP\x10\n\x12\x07\n\x03TAR\x10\x0b\x12\x08\n\x04GZIP\x10\x0c\x12\t\n\x05\x42ZIP2\x10\r\x12\x06\n\x02XZ\x10\x0e\x12\x08\n\x04\x44OCX\x10\x0f\x12\x08\n\x04PPTX\x10\x10\x12\x08\n\x04XLSX\x10\x11\x12\x07\n\x03\x44OC\x10\x12\x12\x07\n\x03PPT\x10\x13\x12\x07\n\x03XLS\x10\x14\x12\x05\n\x01\x43\x10\x15\x12\x07\n\x03\x43PP\x10\x16\x12\x08\n\x04JAVA\x10\x17\x12\n\n\x06\x43SHARP\x10\x18\x12\n\n\x06PYTHON\x10\x19\x12\x08\n\x04RUBY\x10\x1a\x12\x07\n\x03PHP\x10\x1b\x12\x0e\n\nJAVASCRIPT\x10\x1c\x12\x07\n\x03XML\x10\x1d\x12\x07\n\x03\x43SS\x10\x1e\x12\x07\n\x03GIF\x10\x1f*\x80\x01\n\x15WebBrowserCommandType\x12\x08\n\x04GOTO\x10\x00\x12\r\n\tTERMINATE\x10\x01\x12\x08\n\x04WAIT\x10\x02\x12\t\n\x05\x43LICK\x10\x03\x12\x08\n\x04\x43OPY\x10\x04\x12\x08\n\x04TYPE\x10\x05\x12\x0c\n\x08SCROLL_X\x10\x06\x12\x0c\n\x08SCROLL_Y\x10\x07\x12\t\n\x05\x45NTER\x10\x08*;\n\x0fWebBrowserState\x12\x0b\n\x07RUNNING\x10\x00\x12\x0e\n\nTERMINATED\x10\x01\x12\x0b\n\x07TIMEOUT\x10\x02\x32G\n\x05Tools\x12>\n\rGetWebBrowser\x12\x12.WebBrowserRequest\x1a\x13.WebBrowserResponse\"\x00(\x01\x30\x01\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'tools_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_CONTENTMIMETYPE']._serialized_start=1532
  _globals['_CONTENTMIMETYPE']._serialized_end=1866
  _globals['_WEBBROWSERCOMMANDTYPE']._serialized_start=1869
  _globals['_WEBBROWSERCOMMANDTYPE']._serialized_end=1997
  _globals['_WEBBROWSERSTATE']._serialized_start=1999
  _globals['_WEBBROWSERSTATE']._serialized_end=2058
  _globals['_CONTENT']._serialized_start=15
  _globals['_CONTENT']._serialized_end=75
  _globals['_WEBBROWSERCOMMANDOUTPUT']._serialized_start=77
  _globals['_WEBBROWSERCOMMANDOUTPUT']._serialized_end=133
  _globals['_WEBBROWSERCOMMANDERROR']._serialized_start=135
  _globals['_WEBBROWSERCOMMANDERROR']._serialized_end=189
  _globals['_WEBBROWSERINPUT']._serialized_start=191
  _globals['_WEBBROWSERINPUT']._serialized_end=278
  _globals['_WEBBROWSERBUTTON']._serialized_start=280
  _globals['_WEBBROWSERBUTTON']._serialized_end=330
  _globals['_WEBBROWSERINPUTFIELD']._serialized_start=332
  _globals['_WEBBROWSERINPUTFIELD']._serialized_end=386
  _globals['_WEBBROWSERSELECTFIELD']._serialized_start=388
  _globals['_WEBBROWSERSELECTFIELD']._serialized_end=443
  _globals['_WEBBROWSERTEXTAREAFIELD']._serialized_start=445
  _globals['_WEBBROWSERTEXTAREAFIELD']._serialized_end=502
  _globals['_WEBBROWSERLINK']._serialized_start=504
  _globals['_WEBBROWSERLINK']._serialized_end=565
  _globals['_WEBBROWSEROUTPUT']._serialized_start=568
  _globals['_WEBBROWSEROUTPUT']._serialized_end=939
  _globals['_WEBBROWSERSESSIONCONFIG']._serialized_start=942
  _globals['_WEBBROWSERSESSIONCONFIG']._serialized_end=1223
  _globals['_WEBBROWSERSESSION']._serialized_start=1225
  _globals['_WEBBROWSERSESSION']._serialized_end=1297
  _globals['_WEBBROWSERREQUEST']._serialized_start=1299
  _globals['_WEBBROWSERREQUEST']._serialized_end=1402
  _globals['_WEBBROWSERRESPONSE']._serialized_start=1404
  _globals['_WEBBROWSERRESPONSE']._serialized_end=1529
  _globals['_TOOLS']._serialized_start=2060
  _globals['_TOOLS']._serialized_end=2131
# @@protoc_insertion_point(module_scope)
