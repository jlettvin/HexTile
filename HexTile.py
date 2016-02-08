#!/usr/bin/env python

"""HexTile.py

Usage:
    HexTile.py \
[(-v | --verbose)] \
[(-T Tiles| --Tiles=Tiles)] \
[(-t tubulin| --tubulin=tubulin)] \
[(-r | --rotate)] \
[(-g | --github)] \
[(-R Rings| --Rings=Rings)] \
[(-l | --label)]
    HexTile.py (-h | --help)
    HexTile.py (--version)

Options:
    -l --label                     Label the tiles [default: False]
    -r --rotate                    Rotate some strands [default: False]
    -g --github                    Output in github Readme.md format
    -R Rings --Rings=Rings         Count of rings [default: 0]
    -t TUBULIN --tubulin=TUBULIN   Strand count [default: 91]
    -T TILES --Tiles=TILES         Tile count [default: 91]
    -v --verbose                   Show details about execution
    -h --help                      Show this screen
    --version                      Show version

Tubulin polymers distinctively course through the neurons of vertebrates.
They form long unbroken unbranching chains from dendritic receptor
down the dendrite, through the soma (sometimes), and to the axon terminal.
These polymers intertwine but never touch.
Modeling them poses a challenge which we approach as an exercise in
forming ropes without individual strands intersecting.
The method used is displacing strands around loops of adjacent hexagonal tiles.
This guarantees no intersection as long as the tiles in a loop are
more than three, the tiles form complete loops, and intersect no other loops.

HexTile.py generates a field of hexagonal tiles
which may host an individual abstract tubulin strand.
Closed continuous non-intersecting loops of tubulin strands
may be rotated to adjacent tiles.
This emulates the character of tubulin pathways in axons.
"""

from docopt import (docopt)
from sys import (exit, argv)
from cPickle import (load, dump)
from random import (seed, randint, random)
from math import (sqrt, ceil)
from itertools import (product)
from pprint import (pprint)
from scipy import (arange)
from operator import (add)
from inspect import (getdoc, getmembers, getframeinfo, currentframe, isclass)
from inspect import (isfunction, ismethod, stack)
from datetime import (datetime)

from Tag import (TAG)
from SelfDoc import (classSelfDoc)

class Dictionary(dict):
    '''
    The goal of this class is to simplify updating of dictionaries.
    The implementation was going to expose keys as class members
    but it was not necessary at this time, so this class is
    VESTIGIAL.
    '''
    def __init__(self, **kw):
        self.update(kw)

    def __call__(self, keys=[], **kw):
        """
        Functor:
        updates values for kw key/value pairs
        returns values for keys
        """
        self.update(kw)
        return [self[key] for key in keys]

class HexTile(dict):
    """
    The goal of this class is to emulate the pathways of tubulin strands
    as they course through a neuron extension on their way to terminals.
    Tubulin strands weave considerably on their course along any featureless
    length of extension between bifurcations and/or terminals.
    A sequence of only a few Hex instances generally suffices.

    See Test.test_000() for more detail.
    """

    neighbor = [[1,0,-1],[0,1,-1],[-1,1,0],[-1,0,1],[0,-1,1],[1,-1,0]]
    s3o2 = sqrt(3.0)/2.0
    edge = 1.0 # unit scale for hexagon edge
    fullRings = {N: 1+6*sum(range(N+1)) for N in range(30)} # >30 permitted

    def __init__(self, sibling=None, **kw):
        """
        Initialization includes inheriting a sibling's dictionary if exists
        otherwise instance uses the specified values from the arg dictionary.
        """
        if sibling:
            # inherit the sibling dictionary to continue its tubulin strands.
            self.kw = sibling.kw
        else:
            # otherwise start a new dictionary with specified values
            self.kw = kw
        rings = int(kw['--Rings'])
        # If rings are specified, tiles map to the calculated number for rings.
        if rings and HexTile.fullRings.has_key(rings):
            Tiles = HexTile.fullRings[rings]
        else:
            Tiles = int(kw['--Tiles'])
        # tubulins must map to one per tile or less
        tubulins = int(kw['--tubulin'])
        if tubulins > Tiles:
            kw['--tubulin'] = str(Tiles)

        self.verbose = kw.get('--verbose', False)
        self.tubes = Tiles
        self.ring = {}
        self.needed(Tiles)
        self.generateRings()
        if self.kw['--rotate']:
            self.rotate(self.kw['rotates'])

    def needed(self, area):
        """
        Ensure that everything fits, and calculate the radius.
        """
        assert type(area) == type(1)
        assert 0 < area <= HexTile.fullRings.values()
        ring, N, self.radius = 6, 1, 0
        A = area - 1            # account for the center tile
        while A > 0:
            N += ring           # unused count
            A -= ring           # remove tile count appropriate for ring
            ring += 6           # each ring adds 6 more tiles
            self.radius += 1    # count how many tiles from center
        if self.verbose:
            print 'area', area, 'needs radius', self.radius

    def xy(self, elements, txy=[0.0, 0.0]):
        """
        Calculate the planar coordinates for the RGB positional specifier
        scaled as specified.
        The RGB specifier is non-orthogonal,
        identifying a tile by its displacement along three vectors
        where the vectors are 120 degrees apart.
        TODO This should be updated for txy=[1.0, 1.0].
        """
        R, G, B = elements(['R','G','B'])
        S = HexTile.edge
        return (S * R * txy[0], S * (B - G) * HexTile.s3o2 * txy[1])

    def adjacent(self, t1, t2):
        """
        Tile adjacency requires that displacement along an RGB vector
        have values 0, +1, and -1.
        UPDATED.
        """
        tile1, tile2 = self[t1], self[t2]
        dR = tile2['R'] - tile1['R']; adR = abs(dR)
        dG = tile2['G'] - tile1['G']; adG = abs(dG)
        dB = tile2['B'] - tile1['B']; adB = abs(dB)
        return (dR+dG+dB) == 0 and adR <= 1 and adG <= 1 and adB <= 1

    def adjacents(self, tiles):
        """
        Review a sequence of tiles for adjacency.
        """
        shifted = tiles[1:] + tiles[:1]
        for t1,t2 in zip(tiles, shifted):
            if not self.adjacent(t1, t2):
                if self.verbose:
                    print 'NOT ADJACENT!', t1, t2
                return False
        if self.verbose:
            print 'YES ADJACENT!', tiles
        return True

    def rotate(self, groups):
        """
        Displace a sequence of tubulins to neighbors fulfilling adjacency.

        groups is a list of sublists.
        Each sublist is a sequence of Tile numbers.
        Each sequence is to be rotated or translated as a group.
        Tile numbers are expected to be unique over all sublists.
        Adjacent Tile numbers are expected to be neighbors.

        Make sure there are no shared tiles
        """
        if self.kw['--rotate']:
            if groups:
                A = sorted(reduce(add, groups))
                B = sorted(list(set(A)))
                assert A==B, str(A)+' != '+str(B)

            for group, tiles in enumerate(groups):
                self.adjacents(tiles)
                indices = [self[-tile] for tile in tiles]
                if self.verbose:
                    print 'tiles', tiles
                    print 'indices', indices
                for moved, (tile, index) in enumerate(
                        zip(tiles, indices[1:] + indices[0:1])):
                    if self.verbose:
                        print tile, index
                    self[index]['strand'] = -tile
                    self[index]['group'] = group
                    self[index]['moved'] = moved
                    self[-tile] = index
        return self

    def generateRings(self):
        """
        generateRings makes the initial concentric rings of tiles.
        Initialization specifies how many rings are to be formed.
        This method performs the calculations necessary to
        actually create and label those things.
        """
        rgb = [0,0,0]
        tile = 1
        ring = 0
        elements = Dictionary(
                R=0,G=0,B=0,ring=ring,strand=-tile,group=0,moved=0)
        self.ring = {ring:[elements,]}
        tubulins = int(self.kw['--tubulin'])
        if self.verbose:
            print 'generating:', tubulins
        self[tile] = self.ring[0][-1]
        self[-tile] = tile
        if self.kw.get('autonumber', False):
            self[-tile] = tile  # tubulin assigned to tile of same number
        delta = HexTile.neighbor

        for ring in range(1,self.radius+1):
            # Subtle algorithm.  Be cautious in modifying.
            self.ring[ring] = []
            r,g,b = rgb[0], rgb[1]-ring, rgb[2]+ring
            for j in range(len(delta)):
                for k in range(ring):
                    tile += 1
                    p = -(tile if tile <= tubulins else 0)
                    if self.verbose:
                        print tile, tubulins, p
                    t = (r,g,b) = [
                            u+delta[j][v]
                            for u,v in
                            zip([r,g,b], range(3))]
                    elements = Dictionary(
                            R=r,G=g,B=b,ring=ring,strand=p,group=0,moved=0)
                    self.ring[ring] += [elements,]
                    self[tile] = self.ring[ring][-1]
                    self[-tile] = tile
                    # Positive numbers are cardinal tile numbers
                    # Negative numbers are tubulin fiber numbers
                    # Initially, tubulins are in same-numbered tiles
                    # Rotations move tubulins to different numbered tiles

    def __str__(self):
        """
        This is very poorly implemented, but works for at least 800 tubulins!
        """
        rings = len(self.ring.keys())
        diameter = 1 + 2 * rings
        S, V, U, BS, FS = ' ', '|', '_', '\\', '/'

        # Create tile for insertion (note the "horns" atop the hexagon.
        template = [list(line) for line in [
                ' \_____/ ',
                ' /     \\ ',
                '/       \\',
                '\       /',
                ' \_____/ ',
                ]]
        # Calculate its dimensions
        txy = [len(template[0]) ,len(template)]
        txy0 = [txy[0]/2, txy[1]/2]

        # Create printable field of sufficient size, and get its center
        W = (txy[0] * diameter)
        H = (txy[1] * diameter)

        # Create a template scan line
        # TODO get rid of need for bias
        bias = [0.75, 0.867]
        self.rendered = S * int(bias[0]*W)
        self.rendered = [list(self.rendered) for _ in range(int(bias[1]*H))]
        self.xy0 = [ len(self.rendered[0])/2, len(self.rendered)/2 ]

        # (x0,y0) is the center of the fully rendered image
        x0, y0 = self.xy0

        # Render the hexagons for the tubulin strands
        for number in range(1, self.tubes+1):
            # RGB is the 3-axis planar coordinates for a tile
            elements = self[number]
            group, moved, ring, strand = elements(
                    ['group', 'moved', 'ring', 'strand'])

            # (x1,y1) offsets tile coordinates to center the tile
            x1, y1 = (-d for d in txy0)

            # (xc,yc) is the cartesian coordinates for a given tile
            xc, yc = self.xy(elements, txy)

            # TODO Fix this truly gross way of adjusting offsets
            xc *= [0.775, 0.78][xc>0]
            yc *= [0.465, 0.46][yc>0]

            # (xs, ys) is the upper left corner of the numbered tile
            xs, ys = xc+x1, -(yc+y1)

            # Render hexagonal tiles into scan lines
            for y2 in range(txy[1]):
                # y char subst coordinate is center + upper left + scanline
                y = int(y0+ys+y2)
                for x2 in range(txy[0]):
                    # x char subst coordinate is center + upper left + scanline
                    x = int(x0+xs+x2)
                    self.rendered[y][x] = template[y2][x2]

            # Insert tile numbers in the scan-line rendered hexagons
            def putNumber(k, n, buf, x, y):
                s = '%s%d' % (k, int(n)) if k or n else ''
                for i, c in enumerate(list(s)):
                    self.rendered[int(y)][int(x+i)] = c

            # Label this tile
            if self.kw['--label']:
                if strand:
                    zipped = zip(['T','S','R'], [number, -strand, ring], [1,2,3])
                else:
                    zipped = zip(['T', '' ,'R'], [number, 0, ring], [1,2,3])
                for key, value, offset in zipped:
                    putNumber(key, value, self.rendered, x0+xs+2, y0+ys+offset)
            elif strand and number != -strand:
                # group, moved are the identifiers within the group
                for key, value, offset in zip(
                        [chr(ord('A')+group),],
                        [moved+1,],
                        [2,],
                        ):
                    putNumber(key, value, self.rendered, x0+xs+2, y0+ys+offset)

        # Get rid of "horns" atop the hexagons
        for y in range(1, len(self.rendered)):
            for x in range(1, len(self.rendered[0])-2):
                c = self.rendered[y][x]
                cul = self.rendered[y-1][x-1]
                cup = self.rendered[y-1][x]
                cur = self.rendered[y-1][x+1]
                if c == BS and cul == S and cup != FS:
                    self.rendered[y][x] = S
                if c == FS and cur == S and cup != BS:
                    self.rendered[y][x] = S

        self.field = ''

        # Display the hexagons
        Vrule = V+U*(len(self.rendered[0])-3)+V
        Srule = S+U*(len(self.rendered[0])-3)+S
        self.field += '%s\n' % Srule

        for line in self.rendered:
            rendered = ''.join(line[2:-1])
            if not rendered.strip():
                continue
            self.field += V + rendered + V + '\n'
        self.field += '%s\n' % Vrule

        # Announce how many tubulin fibers there are in how many rings
        if self.verbose:
            if self.kw['--rotate']:
                self.field += 'Letters/Numbers are rotation groups/elements\n'
            else:
                self.field += 'T(tile#), strand(protein#), H(ring#)\n'
                self.field += 'tubulin(%d), rings(%d)\n' % (self.tubes, rings)

        return self.field

if __name__ == "__main__":

    def tag(text, *args):
        if not args:
            TAG.add(text)
        else:
            name = args[0]
            more = tuple(args[1:])
            if isinstance(name, list):
                name = name[0]
                more = tuple(args[0][1:])
            with TAG(name):
                tag(text, *more)

    def validate():
        kw = docopt(__doc__, version="0.0.1")
        verbose = kw['--verbose']
        Tiles = int(kw.get('--Tiles', 0))
        tubes = int(kw.get('--tubulin', 0))
        rotates = []
        assert \
                Tiles in HexTile.fullRings.values(), \
                'Choose: '+str(HexTile.fullRings)
        if Tiles or tubes:
            if Tiles and not tubes:
                tubes = Tiles
            elif tubes and not Tiles:
                Tiles = tubes
            if tubes > Tiles:
                tubes = Tiles
            kw['--tubulin'] = str(tubes)
            kw['--Tiles'] = str(Tiles)
            if verbose:
                print 'kw', kw

        groups = {
                61:range(38,62),
                37:range(20,38),
                18:[6,7,18,17,16],
                14:[4,5,14],
                3:[1,2,3],
                }
        for key, val in groups.iteritems():
            if tubes >= key:
                rotates += [val,]
        kw['rotates'] = rotates
        if verbose:
            print 'rotates', rotates
        return kw

    class Test(dict, classSelfDoc):

        def _common(self, name, doc, **kw):
            groups = {}
            tubes = kw.get('--tubulin', kw.get('--Tiles', 37))
            kw['--tubulin'] = tubes

            # These are hand-generated loops of hexagons suitable for testing.
            if tubes >= 61:
                groups[61] = range(38,62)
            if tubes >= 37:
                groups[37] = range(20,38)
            if tubes >= 18:
                groups[18] = [6,7,18,17,16]
            if tubes >= 14:
                groups[14] = [4,5,14]
            if tubes >= 3:
                groups[3] = [1,2,3]

            rotates = []
            for key, val in groups.iteritems():
                if tubes >= key:
                    rotates += [val,]
            kw['rotates'] = rotates
            tag(name, 'h3')
            tag(doc)
            if not kw.get('ignore', False):
                params = {}
                params.update(self)
                params.update(kw)
                #tag(str(params))
                h = HexTile(**params)
                tag('Figure %s' % (name[5:].strip('0')), 'h5')
                tag(str(h), 'pre')

        def test_000(self):
            r"""<p>&nbsp;&nbsp;&nbsp;&nbsp;
The goal of this document is to emulate the pathways of tubulin strands
as they course through a neuron extension on their way to terminals.
Tubulin strands weave considerably on their course along any featureless
length of extension between bifurcations and/or terminals.
A sequence of only a few Hex instances generally suffices.

</p><p>&nbsp;&nbsp;&nbsp;&nbsp;
This emulation uses hexagonal tiles to enable a line to meander through
a sequence of instances from one end to the other
without intersecting another line.
A line is thought as traversing the center point of its containing
hexagonal tile on its way to the next layer hexagonal tile.
Avoiding intersection is achieved by allowing cycles of single lines to
rotate one step, where the number of tiles in the cycle is variable and
the cycle is simple (no figure 8s) and
multiple cycles in the same hex instance have no tiles in common.
Minimum cycle size is 3 tiles.
Rotations may be clockwise or anticlockwise.
</p><p>&nbsp;&nbsp;&nbsp;&nbsp;

In this module, there should be at least two Hex instances for each end of
a line segment extending from one point to another in the paraboloid mesh.
Preferably there should be three or more to cause a significant weaving of
tubulins along that segment consistent with the histological evidence from
Cajal's drawings and direct imaging evidence in literature since 2000.
However, the principal goal is to cause at least some weaving of tubulin.
This weaving eventually enables aggregation of signal from common rings
of fixed paraboloid radius (height) into tight groups at the base bundle.
This aggregation is what enables coincidence to be detected by sharing
activity energy for detections at a common Airy disk radius.
</p><p>&nbsp;&nbsp;&nbsp;&nbsp;

A Hex object generates and serves coordinates of hexagonal tile positions
around a central tile position.  The coordinates are given in two forms.
Standard (x,y) coordinates are useful for projection in OpenGL.
RGB coordinates are more natural and elegant for internal use.

Ideas for this implementation were taken from:
    <ul>
    <li><a href="http://stackoverflow.com/questions/2459402/\
hexagonal-grid-coordinates-to-pixel-coordinates">
hexagonal-grid-coordinates-to-pixel-coordinates
    </a>

    <li><a href="http://www.codeproject.com/Articles/14948/\
Hexagonal-grid-for-games-and-other-projects-Part">
Hexagonal-grid-for-games-and-other-projects-Part
    </a>
    </ul>

</p><p>&nbsp;&nbsp;&nbsp;&nbsp;
For any given tile, there are six neighbors.

</p><p>&nbsp;&nbsp;&nbsp;&nbsp;
RGB axes refer to three non-orthogonal axes each of which is orthogonal
to sequences of hexagons touching along full edges (not just points).
See the image HexRGB.gif in this directory.
Tile positions are numbered along a stepped spiral
from the center starting from the upper right of vertical going
all the way around to vertical, then stepping out to the next upper right
of vertical.  Confirm by observation.
The tile labels shown have the tile number at the top and then the
offsets along the R, G, B axes.
For instance, starting from the R axis label, the layers of hexagons
are labeled -2, -1, 0, 1, 2.  Confirm by observing the leftmost RGBN label.
Tile numbers begin with 1, not 0 for convenience.
Tubulin numbers are negative numbers
and both tile and tubulin numbers are used
to fetch tile information from a common dictionary.
</p>

<pre>
                                        G
                                       /
                        _____         /
                       / 19  \
                 _____/       \_____
                / 18  \ 0,-2,2/  8  \
   S /    _____/       \_____/       \_____    \ S
    /    / 17  \-1,-1,2/  7  \ 1,-2,1/  9  \    \
        /       \_____/       \_____/       \
        \ -2,0,2/  6  \ 0,-1,1/  2  \ 2,-2,0/
         \_____/       \_____/       \_____/
         / 16  \ -1,0,1/  1  \ 1,-1,0/ 10  \
  _____ /       \_____/       \_____/       \
R       \ -2,1,1/  5  \ 0,0,0 /  3  \2,-1,-1/
         \_____/       \_____/       \_____/
         / 15  \ -1,1,0/  4  \ 1,0,-1/ 11  \
        /       \_____/       \_____/       \
        \ -2,2,0/ 14  \ 0,1,-1/ 12  \ 2,0,-2/
         \_____/       \_____/       \_____/
               \-1,2,-1/ 13  \ 1,1,-2/
                \_____/       \_____/
                      \ 0,2,-2/
                       \_____/        \
                                       \
                        _____           B
                          S

___________________________________________________________________________

                       |--s-|
                        _____     ___ ___
                       /     \     r   |
                      /       \   ___  a
                      \       /        |
                       \_____/        _|_

                             |h|
                     |----b----|

                     h = s * sin(30)
                     r = s * cos(30)
                     b = s + 2*h
                     a = r * 2
___________________________________________________________________________
</pre>

<p>
I have been working on a new sub-topic of neural processing for some time now.
In the past I drew tiny tubes from here to there,
attempting but failing to avoid intersections.
But I decided to try to model these tubes mathematically.
</p><p>
The easiest analogy is to think of a rope.
A rope is made of smaller ropes twisted together.
The smaller ropes is made of strings twisted together.
Strings are threads twisted together.
Threads are individual fibers twisted together.
None of them, at any level, intersect.
</p><p>
What I have done, in my modeling software,
is to generate a hexagonal mesh points up/down, flat left/right.
The images below are screen shots of models generated by the software.
</p><p>
Each cell in the mesh has a central (x,y) coordinate.
Each cell is a unit edge hexagon (scalable).
Each cell is numbered in a stepped spiral.
Spiral steps occur at the first positive position off the x==0 y axis.
The central cell is numbered 1, not 0 (T1 means Tile 1).
As cell numbers increase, steps are required to start new rings.
The central tile is in ring 0 (R0 means ring 0).
It is surrounded by ring 1.  Ring 1 is surrounded by ring 2, and so on.
Tubulin strands initially are numbered identically to tiles they occupy.
In the first image below, note that tubulin 1 is Tile 1 in Ring 0 (T1/S1/R0).
</p><p>
Axons (and other neuron interior spaces) have bundles of tubulin like ropes.
Fiber intersection is forbidden.
The tightest packing of tubulin is into a fully occupied hexagonal mesh.
An axon may be considered to be a sequence of hexagonal mesh cross-sections.
Tubulins weave as they advance along the axon.
There must be rules for the weaving that prevent intersection.
I will now explain those rules.
</p><p>
The location of two adjacent tubulin strands can't be exchanged (intersection).
A sequence of occupied tiles ending with an unoccupied tile
may be translated towards that tile.
Occupants of tiles forming a cycle of edge-adjacent tiles
may be rotated one step.
If occupants are missing,
the translation or rotation may still take place (displacement).
Multiple translations and rotations are expected between two adjacent meshes.
Single-step translations and rotations are the only operations permitted.
Sharing tiles amongst operational groups is forbidden.
</p><p>
This second image illustrates a single rotation of tubulins 1, 2, and 3.
Tile 1 now has tubulin 3, Tile 2 tubulin 1, and Tile 3 tubulin 2.
</p><p>
A tubulin rope constructed by rotations of a fully packed hex mesh
along a regularly spaced sequence of meshes will have
no intersections and will obey the rules required of the tubulin tree.
</p><p>
Tubulins become neighbors at the base of the tubulin tree,
then weave along sequences of hex meshes until they approach
the location of a tubulin termination where it must propagate
to the outer surface of the mesh in the direction necessary
to enable the tubulin to service the dendritic spine which acts as
a transient gradient sampler of local neurotransmitter.
</p><p>
This is a faithful representation of minimum conditions for a tubulin tree.
There are important additions to be made such as
using a sparsely occupied larger hexagonal mesh to enable tubulins
to rapidly cross a large volume such as in a cell body.
</p><p>
More on this later.
My current hoped-for result is to produce such a tree on a 3D printer
where each tubulin is colored differently.
</p><p>
This software could probably be used for constructing models of rope.
</p>
"""
            name, doc = self.frameName, self.frameDoc
            self._common(name, doc, ignore=True)

        def test_001(self):
            r"""&nbsp;&nbsp;&nbsp;&nbsp;
This test illustrates the production of a single hexagon with labels.
<ul>
<li>The 'T' label is the tile number;
<li>The 'S' label is the tubulin strand number;
<li>The 'R' label is the ring number.
</ul>
"""
            name, doc = self.frameName, self.frameDoc
            kw = {'--tubulin': 1, '--Tiles': 1, '--label': True}
            self._common(name, doc, **kw)

        def test_002(self):
            r"""&nbsp;&nbsp;&nbsp;&nbsp;
            A first ring is tiled with labels that begin with
            the first tile after 12 noon in the Figure.
            """
            name, doc = self.frameName, self.frameDoc
            kw = {'--tubulin': 7, '--Tiles': 7, '--label': True}
            self._common(name, doc, **kw)

        def test_003(self):
            r"""&nbsp;&nbsp;&nbsp;&nbsp;
The default execution of HexTile produces 5 rings around center.
It also shows no labels and no modifications.
"""
            name, doc = self.frameName, self.frameDoc
            self._common(name, doc)

        def test_004(self):
            r"""&nbsp;&nbsp;&nbsp;&nbsp;
Here a one ring set is shown after one tubulin group has been rotated.
A1, A2, and A3 refer to a group labeled 'A' where
Strands 1, 2, and 3 have been rotated clockwise.
See Figure 0 to see the original locations of these strands.
            """
            name, doc = self.frameName, self.frameDoc
            kw = {'--tubulin': 7, '--Tiles': 7, '--rotate': True}
            self._common(name, doc, **kw)

        def test_005(self):
            r"""&nbsp;&nbsp;&nbsp;&nbsp;
Here a three ring set is shown after three tubulin groups have been rotated.
Note that group C is a set of all strands in the outer ring rotated clockwise.
            """
            name, doc = self.frameName, self.frameDoc
            kw = {'--tubulin': 37, '--Tiles': 37, '--rotate': True, '--label': True}
            self._common(name, doc, **kw)

        def test_006(self):
            r"""&nbsp;&nbsp;&nbsp;&nbsp;
Here a six ring set is shown after three tubulin groups have been rotated.
Note that group C is a set of all strands in
the 2nd to outer ring rotated clockwise.
Note that group E is a set of all strands in
the next inner ring rotated clockwise.
Each group of strands may be rotated separately in either direction.
            """
            name, doc = self.frameName, self.frameDoc
            kw = {'ignore': True}
            kw = {'--tubulin': 61, '--Tiles': 91, '--rotate': True}
            self._common(name, doc, **kw)

        '''
        def test_007(self):
            r"""&nbsp;&nbsp;&nbsp;&nbsp;
            """
            name, doc = self.frameName, self.frameDoc
            kw = {'ignore': True}
            self._common(name, doc, **kw)

        def test_008(self):
            r"""&nbsp;&nbsp;&nbsp;&nbsp;
            """
            name, doc = self.frameName, self.frameDoc
            kw = {'ignore': True}
            self._common(name, doc, **kw)

        def test_009(self):
            r"""&nbsp;&nbsp;&nbsp;&nbsp;
            """
            name, doc = self.frameName, self.frameDoc
            kw = {'ignore': True}
            self._common(name, doc, **kw)

        def test_010(self):
            r"""&nbsp;&nbsp;&nbsp;&nbsp;
            """
            name, doc = self.frameName, self.frameDoc
            kw = {'ignore': True}
            self._common(name, doc, **kw)

        def test_011(self):
            r"""&nbsp;&nbsp;&nbsp;&nbsp;
            """
            name, doc = self.frameName, self.frameDoc
            kw = {'ignore': True}
            self._common(name, doc, **kw)
        '''

        def __init__(self, **kw):
            self.update(kw)
            self.github_format = self.get('--github', None)


        def __call__(self):
            tests = [n for n, m in getmembers(self) if n.startswith('test_')]
            if (self.github_format):
                self.github(tests)

                with open('README.md', 'w') as html:
                    print>>html, TAG.final()
            else:
                with TAG('html'):
                    tag('HexTile Concepts', ['head', 'title'])
                    with TAG('body'):
                        self.github(tests)

                with open('HexTile.html', 'w') as html:
                    print>>html, TAG.final()
            return self

        def github(self, tests):
            timestamp = datetime.now()
            human = '%A %B/%d/%Y %I:%M:%S %p'
            place = '%Y%m%d%H%M%S%f'

            with TAG('h3', align='center'):
                tag('HexTile Concepts')
            tag(timestamp.strftime(human), ['p', 'i'])
            tag(timestamp.strftime(place), ['p', 'i'])
            for test in tests:
                exec('self.%s()' % test)
            return self

    def main():
        """This is the principal starting point of this script."""
        kw = validate()

        tests = Test(**kw)()

    main()
