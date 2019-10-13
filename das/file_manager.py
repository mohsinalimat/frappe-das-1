# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe
import os, base64, re
import hashlib
import mimetypes
from frappe.utils import get_hook_method, get_files_path, random_string, encode, cstr, call_hook_method, cint
from frappe import _
from frappe import conf
from copy import copy
from six.moves.urllib.parse import unquote
from six import text_type

class MaxFileSizeReachedError(frappe.ValidationError): pass

def get_file_url(file_data_name):
	data = frappe.db.get_value("File", file_data_name, ["file_name", "file_url"], as_dict=True)
	return data.file_url or data.file_name

def upload(doctype,docname,private):
	# get record details
	dt = doctype
	dn = docname
	folder = ""
	file_url = frappe.form_dict.file_url
	filename = frappe.form_dict.filename
	is_private = private

	if not filename and not file_url:
		frappe.msgprint(_("Please select a file or url"),
			raise_exception=True)

	# save
	if frappe.form_dict.filedata:
		filedata = save_uploaded(dt, dn, folder, is_private)
	elif file_url:
		filedata = save_url(file_url, filename, dt, dn, folder, is_private)

	comment = {}
	if dt and dn:
		comment = frappe.get_doc(dt, dn).add_comment("Attachment",
			_("added {0}").format("<a href='{file_url}' target='_blank'>{file_name}</a>{icon}".format(**{
				"icon": ' <i class="fa fa-lock text-warning"></i>' if filedata.is_private else "",
				"file_url": filedata.file_url.replace("#", "%23") if filedata.file_name else filedata.file_url,
				"file_name": filedata.file_name or filedata.file_url
			})))

	return {
		"name": filedata.name,
		"file_name": filedata.file_name,
		"file_url": filedata.file_url,
		"is_private": filedata.is_private,
		"comment": comment.as_dict() if comment else {}
	}

def save_uploaded(dt, dn, folder, is_private):
	fname, content = get_uploaded_content()
	if content:
		return save_file(fname, content, dt, dn, folder, is_private=is_private);
	else:
		raise Exception

def save_url(file_url, filename, dt, dn, folder, is_private):
	# if not (file_url.startswith("http://") or file_url.startswith("https://")):
	# 	frappe.msgprint("URL must start with 'http://' or 'https://'")
	# 	return None, None

	file_url = unquote(file_url)

	f = frappe.get_doc({
		"doctype": "File",
		"file_url": file_url,
		"file_name": filename,
		"attached_to_doctype": dt,
		"attached_to_name": dn,
		"folder": folder,
		"is_private": is_private
	})
	f.flags.ignore_permissions = True
	try:
		f.insert();
	except frappe.DuplicateEntryError:
		return frappe.get_doc("File", f.duplicate_entry)
	return f

def get_uploaded_content():
	# should not be unicode when reading a file, hence using frappe.form
	if 'filedata' in frappe.form_dict:
		if "," in frappe.form_dict.filedata:
			frappe.form_dict.filedata = frappe.form_dict.filedata.rsplit(",", 1)[1]
		frappe.uploaded_content = base64.b64decode(frappe.form_dict.filedata)
		frappe.uploaded_filename = frappe.form_dict.filename
		return frappe.uploaded_filename, frappe.uploaded_content
	else:
		frappe.msgprint(_('No file attached'))
		return None, None

def extract_images_from_doc(doc, fieldname):
	content = doc.get(fieldname)
	content = extract_images_from_html(doc, content)
	if frappe.flags.has_dataurl:
		doc.set(fieldname, content)

def extract_images_from_html(doc, content):
	frappe.flags.has_dataurl = False

	def _save_file(match):
		data = match.group(1)
		data = data.split("data:")[1]
		headers, content = data.split(",")

		if "filename=" in headers:
			filename = headers.split("filename=")[-1]

			# decode filename
			if not isinstance(filename, text_type):
				filename = text_type(filename, 'utf-8')
		else:
			mtype = headers.split(";")[0]
			filename = get_random_filename(content_type=mtype)

		doctype = doc.parenttype if doc.parent else doc.doctype
		name = doc.parent or doc.name

		# TODO fix this
		file_url = save_file(filename, content, doctype, name, decode=True).get("file_url")
		if not frappe.flags.has_dataurl:
			frappe.flags.has_dataurl = True

		return '<img src="{file_url}"'.format(file_url=file_url)

	if content:
		content = re.sub('<img[^>]*src\s*=\s*["\'](?=data:)(.*?)["\']', _save_file, content)

	return content

def get_random_filename(extn=None, content_type=None):
	if extn:
		if not extn.startswith("."):
			extn = "." + extn

	elif content_type:
		extn = mimetypes.guess_extension(content_type)

	return random_string(7) + (extn or "")

def save_file(fname, content, dt, dn, folder=None, decode=False, is_private=0):
	if decode:
		if isinstance(content, text_type):
			content = content.encode("utf-8")

		if "," in content:
			content = content.split(",")[1]
		content = base64.b64decode(content)

	file_size = check_max_file_size(content)
	content_hash = get_content_hash(content)
	content_type = mimetypes.guess_type(fname)[0]
	fname = get_file_name(fname, content_hash[-6:])
	file_data = get_file_data_from_hash(content_hash, is_private=is_private)
	if not file_data:
		call_hook_method("before_write_file", file_size=file_size)

		write_file_method = get_hook_method('write_file', fallback=save_file_on_filesystem)
		file_data = write_file_method(fname, content, content_type=content_type, is_private=is_private)
		file_data = copy(file_data)

	file_data.update({
		"doctype": "File",
		"attached_to_doctype": dt,
		"attached_to_name": dn,
		"folder": folder,
		"file_size": file_size,
		"content_hash": content_hash,
		"is_private": is_private
	})

	f = frappe.get_doc(file_data)
	f.flags.ignore_permissions = True
	try:
		f.insert()
	except frappe.DuplicateEntryError:
		return frappe.get_doc("File", f.duplicate_entry)

	return f

def get_file_data_from_hash(content_hash, is_private=0):
	for name in frappe.db.sql_list("select name from `tabFile` where content_hash=%s and is_private=%s", (content_hash, is_private)):
		b = frappe.get_doc('File', name)
		return {k:b.get(k) for k in frappe.get_hooks()['write_file_keys']}
	return False

def save_file_on_filesystem(fname, content, content_type=None, is_private=0):
	fpath = write_file(content, fname, is_private)

	if is_private:
		file_url = "/private/files/{0}".format(fname)
	else:
		file_url = "/files/{0}".format(fname)

	return {
		'file_name': os.path.basename(fpath),
		'file_url': file_url
	}

def get_max_file_size():
	return conf.get('max_file_size') or 10485760

def check_max_file_size(content):
	max_file_size = get_max_file_size()
	file_size = len(content)

	if file_size > max_file_size:
		frappe.msgprint(_("File size exceeded the maximum allowed size of {0} MB").format(
			max_file_size / 1048576),
			raise_exception=MaxFileSizeReachedError)

	return file_size

def write_file(content, fname, is_private=0):
	"""write file to disk with a random name (to compare)"""
	file_path = get_files_path(is_private=is_private)

	# create directory (if not exists)
	frappe.create_folder(file_path)
	# write the file
	with open(os.path.join(file_path.encode('utf-8'), fname.encode('utf-8')), 'w+') as f:
		f.write(content)

	return get_files_path(fname, is_private=is_private)

def remove_all(dt, dn, from_delete=False):
	"""remove all files in a transaction"""
	try:
		for fid in frappe.db.sql_list("""select name from `tabFile` where
			attached_to_doctype=%s and attached_to_name=%s""", (dt, dn)):
			remove_file(fid, dt, dn, from_delete)
	except Exception as e:
		if e.args[0]!=1054: raise # (temp till for patched)

def remove_file_by_url(file_url, doctype=None, name=None):
	if doctype and name:
		fid = frappe.db.get_value("File", {"file_url": file_url,
			"attached_to_doctype": doctype, "attached_to_name": name})
	else:
		fid = frappe.db.get_value("File", {"file_url": file_url})

	if fid:
		return remove_file(fid)

def remove_file(fid, attached_to_doctype=None, attached_to_name=None, from_delete=False):
	"""Remove file and File entry"""
	file_name = None
	if not (attached_to_doctype and attached_to_name):
		attached = frappe.db.get_value("File", fid,
			["attached_to_doctype", "attached_to_name", "file_name"])
		if attached:
			attached_to_doctype, attached_to_name, file_name = attached

	ignore_permissions, comment = False, None
	if attached_to_doctype and attached_to_name and not from_delete:
		doc = frappe.get_doc(attached_to_doctype, attached_to_name)
		ignore_permissions = doc.has_permission("write") or False
		if frappe.flags.in_web_form:
			ignore_permissions = True
		if not file_name:
			file_name = frappe.db.get_value("File", fid, "file_name")
		comment = doc.add_comment("Attachment Removed", _("Removed {0}").format(file_name))

	frappe.delete_doc("File", fid, ignore_permissions=ignore_permissions)

	return comment

def delete_file_data_content(doc, only_thumbnail=False):
	method = get_hook_method('delete_file_data_content', fallback=delete_file_from_filesystem)
	method(doc, only_thumbnail=only_thumbnail)

def delete_file_from_filesystem(doc, only_thumbnail=False):
	"""Delete file, thumbnail from File document"""
	if only_thumbnail:
		delete_file(doc.thumbnail_url)
	else:
		delete_file(doc.file_url)
		delete_file(doc.thumbnail_url)

def delete_file(path):
	"""Delete file from `public folder`"""
	if path:
		if ".." in path.split("/"):
			frappe.msgprint(_("It is risky to delete this file: {0}. Please contact your System Manager.").format(path))

		parts = os.path.split(path.strip("/"))
		if parts[0]=="files":
			path = frappe.utils.get_site_path("public", "files", parts[-1])

		else:
			path = frappe.utils.get_site_path("private", "files", parts[-1])

		path = encode(path)
		if os.path.exists(path):
			os.remove(path)

def get_file(fname):
	"""Returns [`file_name`, `content`] for given file name `fname`"""
	file_path = get_file_path(fname)

	# read the file
	with open(encode(file_path), 'r') as f:
		content = f.read()

	return [file_path.rsplit("/", 1)[-1], content]

def get_file_path(file_name):
	"""Returns file path from given file name"""
	f = frappe.db.sql("""select file_url from `tabFile`
		where name=%s or file_name=%s""", (file_name, file_name))
	if f:
		file_name = f[0][0]

	file_path = file_name

	if "/" not in file_path:
		file_path = "/files/" + file_path

	if file_path.startswith("/private/files/"):
		file_path = get_files_path(*file_path.split("/private/files/", 1)[1].split("/"), is_private=1)

	elif file_path.startswith("/files/"):
		file_path = get_files_path(*file_path.split("/files/", 1)[1].split("/"))

	else:
		frappe.throw(_("There is some problem with the file url: {0}").format(file_path))

	return file_path

def get_content_hash(content):
	return hashlib.md5(content).hexdigest()

def get_file_name(fname, optional_suffix):
	# convert to unicode
	fname = cstr(fname)

	n_records = frappe.db.sql("select name from `tabFile` where file_name=%s", fname)
	if len(n_records) > 0 or os.path.exists(encode(get_files_path(fname))):
		f = fname.rsplit('.', 1)
		if len(f) == 1:
			partial, extn = f[0], ""
		else:
			partial, extn = f[0], "." + f[1]
		return '{partial}{suffix}{extn}'.format(partial=partial, extn=extn, suffix=optional_suffix)
	return fname

@frappe.whitelist()
def download_file(file_url):
	"""
	Download file using token and REST API. Valid session or
	token is required to download private files.

	Method : GET
	Endpoint : frappe.utils.file_manager.download_file
	URL Params : file_name = /path/to/file relative to site path
	"""
	file_doc = frappe.get_doc("File", {"file_url":file_url})
	file_doc.check_permission("read")

	with open(getattr(frappe.local, "site_path", None) + file_url, "rb") as fileobj:
		filedata = fileobj.read()
	frappe.local.response.filename = file_url[file_url.rfind("/")+1:]
	frappe.local.response.filecontent = filedata
	frappe.local.response.type = "download"