all:	HexTile.html

README.md HexTile.html:	HexTile.py Makefile
	./HexTile.py -r
	./HexTile.py -r -g
