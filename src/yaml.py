import re as __re__

def __getcleanline__(stream: object) -> str:
	line: str = stream.readline()
	# matching lines that are not comments or unnecessary(empty) lines or partial lines that are not comments
	mat = __re__.match(r' *(?!#)[^ ].*?(?=$|\n| +#)', line)
	if mat:
		return mat.group(0)
	elif line:
		return __getcleanline__(stream)
	else:
		return None

def __converttype__(value: str, aliases: dict) -> tuple[object, str]:
	anchor: str = None
	output: object = None
	
	if len(value) > 1:
		if value[0] == '*':
			idx: int = value.find(' ')
			if idx == 1:
				raise Exception("Alias name cannot be empty")
			if idx <= -1:
				idx = None
			if value[1:idx] in aliases:
				output = aliases[value[1:idx]]
				value = value[idx:].strip()
				if idx == None:
					value = ''
				if not value == '':
					raise Exception("Cannot assign both value and alias at the same time")
				return output, anchor
			else:
				raise Exception("Cannot find alias for the given anchor")
		elif value[0] == '&':
			idx = value.find(' ')
			if idx == 1:
				raise Exception("Anchor name cannot be empty")
			if idx <= -1:
				anchor = value[1:]
				value = None
			else:
				anchor = value[1:idx]
				value = value[idx:].strip()
				if value[0] == '*':
					raise Exception("Incorrect combination of Anchors and Aliases")

	if len(value) <= 0 or value.lower() in ['null', '~']:
		output = None
	elif value[0] == value[-1] and value[0] in ['"', "'"]:
		output = value[1:-1]
	elif value.lower() in ["yes", "true", "on"]:
		output = True
	elif value.lower() in ["no", "false", "off"]:
		output = False
	elif __re__.fullmatch(r'[+-]?\d+', value):
		output = int(value)
	elif __re__.fullmatch(r'[+-]?\d+\.\d+?', value):
		output = float(value)
	else:
		output = value
	return output, anchor

def __parse__(stream: object, line: str = None, indent: str = '', aliases: dict = {}) -> tuple[list | dict, str, dict]:
	# if the next line is passed then take it else get the next line from the input stream
	if not line:
		line = __getcleanline__(stream)
	islist: bool = False
	keyname: str = None

	# determine if the returned object is a dictionary or a list
	if __re__.match(r' *\- ', line):
		islist = True
		obj: list = []
	else:
		obj: dict = {}
	
	while line:
		if not indent == '':
			if line.startswith(indent):
				line = line[len(indent):]
			else:
				return obj, line, aliases

		if line.startswith(' '):
			o, line, al = __parse__(stream, indent + line, indent + (' ' * (len(line) - len(line.lstrip()))), aliases)
			aliases = aliases | al
			if keyname:
				if anchor:
					aliases[anchor] = o
					anchor = None
				obj[keyname] = o
			elif islist:
				obj.append(o)
			else:
				raise Exception("Key-Value pair cannot be determined")
			
			if not line or not indent + line.lstrip() == line:
				return obj, line, aliases
			else:
				continue
		
		# list or list-item
		if line.startswith('- '):
			line = line[2:]

			# list item defined on the same level as that of the parent dictionary
			if not islist:
				if keyname:
					o, line, al = __parse__(stream, indent + '- ' + line, indent, aliases)
					aliases = aliases | al
					if anchor:
						aliases[anchor] = o
						anchor = None
					if obj[keyname] == None:
						obj[keyname] = o

					if not line or not indent + line.lstrip() == line:
						return obj, line, aliases
					else:
						continue
				else:
					raise Exception("Key-Value pair cannot be determined")
			# list within a list
			elif line.startswith('- '):
				o, line, al = __parse__(stream, '  ' + indent + line, indent + '  ', aliases)
				aliases = aliases | al
				obj.append(o)

				if not line or not indent + line.lstrip() == line:
					return obj, line, aliases
				else:
					continue
		elif islist:
			return obj, line, aliases

		# finding key-value separator `:`
		sep = __re__.search(r':(?= +.| *$)', line)

		# dictionary within a list
		if sep and islist:
			o, line, al = __parse__(stream, '  ' + indent + line, indent + (' ' * (len(line) - len(line.lstrip(' ')) + 2)), aliases)
			aliases = aliases | al
			obj.append(o)
			if not line or not indent + line.lstrip() == line:
				return obj, line, aliases
			else:
				continue

		# dictionary
		if sep:
			keyname = line[:sep.start(0)].strip()
			if keyname[0] == keyname[-1] and keyname[0] in ['"', "'"]:
				keyname = keyname[1:-1]
			value = line[sep.start(0) + 2:].strip()
			o, anchor = __converttype__(value, aliases)
			obj[keyname] = o
			if len(value) > 0 and not anchor:
				keyname = None
			if not anchor == None and len(o) > 0:
				aliases[anchor] = o
				anchor = None
		
		# list-item
		elif islist:
			o, anchor = __converttype__(line.strip(), aliases)
			if anchor:
				aliases[anchor] = o
				anchor = None
			obj.append(o)
		else:
			return obj, line, aliases
		
		line = __getcleanline__(stream)
	
	return obj, line, aliases


def parse(fs: object) -> list | dict:
	firstline: str = __getcleanline__(fs)
	if firstline.rstrip() == '---':
		firstline = None
	return __parse__(fs, firstline)[0]


import sys as __sys__
if __name__ == '__main__':
	filename: str = __sys__.argv[1].strip()
	fs: object = open(filename, 'r')
	print(parse(fs))