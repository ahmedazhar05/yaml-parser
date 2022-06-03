import re

def getcleanline(stream):
	line = stream.readline()
	# matching lines that are not comments or unnecessary(empty) lines or partial lines that are not comments
	mat = re.match(r'[^\s#].+?(?=\n|\s+#)', line)
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

def parse(stream, line = None, level = 0, tab = None):
	if not line:
		line = getcleanline(stream)
	islistitem = False
	keyname = None
	l = []
	d = {}
	nestlen = 0
	
	sp_count = len(line) - len(line.lstrip(' '))
	
	# determining spaces-count of a single level indentation
	if not tab and line.startswith(' '):
		tab = ( ' ' * sp_count )
	
	# determining number of indents for the first line which should also be applied to the rest of the lines of the same indentation level
	if line.startswith(' '):
		lvl = sp_count // len(tab)
		if not (lvl == level and sp_count == len(tab * lvl)):
			raise Exception("Irregular indentation")
		else:
			nestlen = len(tab * lvl)
	
	
	while line:
		if line.startswith(' '):
			if keyname:
				d[keyname] = parse(stream, line, level + 1, tab)
			elif islistitem:
				l.append(d | parse(stream, line, level + 1, tab))
				d = {}
			elif tab and nestlen >= len(tab):
				if len(line) - len(line.lstrip(' ')) < nestlen:
					raise Exception("Mapping values can't be determined")
				else:
					line = line[nestlen:]
			else:
				raise Exception("Mapping values can't be determined")
	
		if line.startswith('- '):
			line = line[2:]
			islistitem = True
		
		sep = re.search(r':(?= +[^\n]| *\n)', line)
		if sep:
			keyname = line[:sep.start(0)].strip()
			if keyname[0] == keyname[-1] and keyname[0] in ['"', "'"]:
				keyname = keyname[1:-1]
			value = converttype(line[sep.start(0) + 2:])
			d[keyname] = value
			if not value == None:
				keyname = None
		elif islistitem:
			l.append(converttype(line))
		
		line = getcleanline(stream)
	
	# if islistitem:
	# 	return l
	# 	return [d]
	return d


import sys
if __name__ == '__main__':
	f = open(sys.argv[1].strip(), 'r')
	
	firstline = f.readline()
	if firstline.strip() == '---':
		print(parse(f))
	else:
		print(parse(f, firstline))