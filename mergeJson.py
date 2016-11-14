#!/usr/bin/python

import json
import sys

if __name__ == '__main__':
	if len(sys.argv)<3:
		print 'Please, provide two arguments'
		sys.exit(-1)
	fname1 = sys.argv[1]
	fname2 = sys.argv[2]
	fnameBck = fname1+'.bck'
	
	with open(fname1) as f:
		data1 = json.load(f)
	with open(fname2) as f:
		dala2 = json.load(f)
	
	aux = data1.copy()
	aux.update(data1)
	# Backup orig data	
	with open(fnameBck, 'w') as f:
		json.dump(data1, f)
	# Overwrite by merged data
	with open(fname1, 'w') as f:
		json.dump(aux, f)
	


