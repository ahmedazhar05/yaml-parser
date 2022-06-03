import re

def getcleanline(stream):
	line = stream.readline()
	# matching lines that are not comments or unnecessary(empty) lines or partial lines that are not comments
	mat = re.match(r' *(?!#)[^ ].*?(?=$|\n| +#)', line)
	if mat:
		return mat.group(0)
	elif line:
		return getcleanline(stream)
	else:
		return None

def converttype(value):
	if len(value) <= 0 or value.lower() in ['null', '~']:
		return None
	elif value[0] == value[-1] and value[0] in ['"', "'"]:
		return value[1:-1]
	elif value.lower() in ["yes", "true", "on"]:
		return True
	elif value.lower() in ["no", "false", "off"]:
		return False
	elif re.fullmatch(r'[+-]?\d+', value):
		return int(value)
	elif re.fullmatch(r'[+-]?\d+\.\d+?', value):
		return float(value)
	else:
		return value

def parse(stream, line = None, indent = ''):
	if not line:
		line = getcleanline(stream)
	islist = False
	keyname = None
	if re.match(r' *\- ', line):
		islist = True
		obj = []
	else:
		obj = {}
	
	while line:
		if not indent == '':
			if line.startswith(indent):
				line = line[len(indent):]
			else:
				return obj, line

		if line.startswith(' '):
			o, line = parse(stream, indent + line, indent + (' ' * (len(line) - len(line.lstrip()))))
			if keyname:
				obj[keyname] = o
			elif islist:
				obj.append(o)
			else:
				raise Exception("Key-Value pair cannot be determined")
			
			if not line or not indent + line.lstrip() == line:
				return obj, line
			else:
				continue
		
		if line.startswith('- '):
			line = line[2:]
			if not islist:
				if keyname:
					if obj[keyname] == None:
						o, line = parse(stream, '- ' + line, indent)
						obj[keyname] = o

					if not line or not indent + line.lstrip() == line:
						return obj, line
					else:
						continue
				else:
					raise Exception("Key-Value pair cannot be determined")
		elif islist:
			return obj, line

		# finding key-value separator `:`
		sep = re.search(r':(?= +.| *$)', line)

		if sep and islist:
			o, line = parse(stream, '  ' + indent + line, indent + (' ' * (len(line) - len(line.lstrip(' ')) + 2)))
			obj.append(o)
			if not line or not indent + line.lstrip() == line:
				return obj, line
			else:
				continue

		if sep:
			keyname = line[:sep.start(0)].strip()
			if keyname[0] == keyname[-1] and keyname[0] in ['"', "'"]:
				keyname = keyname[1:-1]
			value = line[sep.start(0) + 2:].strip()
			obj[keyname] = converttype(value)
			if len(value) > 0:
				keyname = None
		elif islist:
			obj.append(converttype(line.strip()))
		else:
			return obj, line
		
		line = getcleanline(stream)
	
	return obj, line


import sys
if __name__ == '__main__':
	f = open(sys.argv[1].strip(), 'r')

	firstline = getcleanline(f)
	if firstline.strip() == '---':
		print(parse(f)[0])
	else:
		print(parse(f, firstline)[0])