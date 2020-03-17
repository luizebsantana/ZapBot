import sys

def parse_input():
	kargs = {}
	kargs['args'] = []
	i = 0
	while i < len(sys.argv):
		if '-' in sys.argv[i] or '--' in sys.argv[i]:
			if '=' in sys.argv[i] and sys.argv[i][-1] != '=':
				key, arg = sys.argv[i].split('=')[:2]
				kargs[key] = arg
			elif i < len(sys.argv)-1 and not ('-' in sys.argv[i+1] or '--' in sys.argv[i+1]):
				kargs[sys.argv[i].replace('=','')] = sys.argv[i+1].replace('=','')
				i+=1
			else:
				kargs[sys.argv[i]] = True
		else:
			kargs['args'].append(sys.argv[i])
		i+=1
	return kargs

def get_input(key, k=None, default=0, type=str):
	kargs = parse_input()
	if key in kargs:
		return type(kargs[key])
	elif k in kargs:
		return type(kargs[k])
	return type(default)
