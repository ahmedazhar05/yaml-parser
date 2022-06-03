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

# determining the level/depth of the line and returning stripped line
def relevel(line, tabs = '  '):
	tab_count = len(tabs)
	spaces_count = len(line) - len(line.lstrip(' '))
	level = spaces_count // tab_count
	line = line[level * tab_count:]
	return level, line

def parse(stream, next = None, level = 0, tab = None):
	if not line:
		line = getcleanline(stream)
	keyname = None
	obj = None

	while line:
		lvl, line = relevel(line, tab)
		if lvl == level - 1:
			return obj, line
		
		if line.startswith('- '):
			line = line[2:]
			islistitem = True

		sep = re.search(r':(?= +[^\n]| *\n)', line)
		if sep and obj == None:
			obj = {}
		if sep and type(obj) == dict:
			keyname = line[:sep.start(0)].strip()
			if keyname[0] == keyname[-1] and keyname[0] in ['"', "'"]:
				keyname = keyname[1:-1]
			value = line[sep.start(0) + 2:].strip()
			obj[keyname] = converttype(value)
			if len(value) > 0:
				keyname = None
		elif islistitem:
			l.append(converttype(line))
		else:
			raise Exception('Uneven spaces')
		
		line = getcleanline(stream)


import sys
if __name__ == '__main__':
	f = open(sys.argv[1].strip(), 'r')
	
	firstline = f.readline()
	if firstline.strip() == '---':
		print(parse(f)[0])
	else:
		print(parse(f, firstline)[0])