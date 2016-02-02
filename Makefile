all:	HexTile.html

HexTile.html:	HexTile.py Makefile
	./HexTile.py -r
