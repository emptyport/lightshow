import lightshow_utilities as lu

channels = []

with open('config.txt') as f:
	content = f.readlines()

content = [x.strip() for x in content]

for c in content:
	channels.append( (int(c.split('\t')[0]), (c.split('\t')[1])) )
	
n_channels = len(channels)
frequencies = lu.generate_frequencies(n_channels)

