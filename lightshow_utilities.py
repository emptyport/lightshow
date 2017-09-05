def generate_frequencies(n_channels, min_freq=20, max_freq=20000):
	interval_spacing = (max_freq - min_freq) / n_channels
	frequencies = []
	for i in range(min_freq, max_freq+1, interval_spacing):
		frequencies.append(i)
	return frequencies
