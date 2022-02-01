import  zstandard as zstd
 

with open("lngraph_2018_10_12__12_00.json.zst", 'rb') as fh:
    dctx = zstd.ZstdDecompressor()
    reader = dctx.stream_reader(fh)
    while True:
        chunk = reader.read(16384)
        if not chunk:
             break

	with open("new.json", 'a') as nf:
	     nf.write(chunk)
	nf.close()

fh.close()
