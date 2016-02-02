<h3 align="center">
HexTile Concepts</h3>
<p>
  <i>
Tuesday February/02/2016 12:04:00 PM  </i>
</p>
<p>
  <i>
20160202120400381133  </i>
</p>
<h3>
test_000</h3>
<p>&nbsp;&nbsp;&nbsp;&nbsp;
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
<h3>
test_001</h3>
&nbsp;&nbsp;&nbsp;&nbsp;
This test illustrates the production of a single hexagon with labels.
<ul>
<li>The 'T' label is the tile number;
<li>The 'S' label is the tubulin strand number;
<li>The 'R' label is the ring number.
</ul>
<h5>
Figure 1</h5>
<pre>
 _________________ 
|      _____      |
|     /T1   \     |
|    / S1    \    |
|    \ R0    /    |
|     \_____/     |
|_________________|
</pre>
<h3>
test_002</h3>
&nbsp;&nbsp;&nbsp;&nbsp;
            <h5>
Figure 2</h5>
<pre>
 ______________________________ 
|            _____             |
|           /     \            |
|     _____/       \_____      |
|    /     \       /     \     |
|   /       \_____/ A1    \    |
|   \       /     \       /    |
|    \_____/ A3    \_____/     |
|    /     \       /     \     |
|   /       \_____/ A2    \    |
|   \       /     \       /    |
|    \_____/       \_____/     |
|          \       /           |
|           \_____/            |
|______________________________|
</pre>
<h3>
test_003</h3>
&nbsp;&nbsp;&nbsp;&nbsp;
The default execution of HexTile produces 5 rings around center.
It also shows no labels and no modifications.
<h5>
Figure 3</h5>
<pre>
 ____________________________________________________________________________________ 
|                                       _____                                        |
|                                      /     \                                       |
|                                _____/       \_____                                 |
|                               /     \       /     \                                |
|                         _____/       \_____/       \_____                          |
|                        /     \       /     \       /     \                         |
|                  _____/       \_____/       \_____/       \_____                   |
|                 /     \       /     \       /     \       /     \                  |
|           _____/       \_____/       \_____/       \_____/       \_____            |
|          /     \       /     \       /     \       /     \       /     \           |
|    _____/       \_____/       \_____/ C17   \_____/       \_____/       \_____     |
|   /     \       /     \       /     \       /     \       /     \       /     \    |
|  /       \_____/       \_____/ C16   \_____/ C18   \_____/       \_____/       \   |
|  \       /     \       /     \       /     \       /     \       /     \       /   |
|   \_____/       \_____/ C15   \_____/       \_____/ C1    \_____/       \_____/    |
|   /     \       /     \       /     \       /     \       /     \       /     \    |
|  /       \_____/ C14   \_____/ A2    \_____/       \_____/ C2    \_____/       \   |
|  \       /     \       /     \       /     \       /     \       /     \       /   |
|   \_____/       \_____/ A3    \_____/ A1    \_____/       \_____/       \_____/    |
|   /     \       /     \       /     \       /     \       /     \       /     \    |
|  /       \_____/ C13   \_____/ A5    \_____/ B1    \_____/ C3    \_____/       \   |
|  \       /     \       /     \       /     \       /     \       /     \       /   |
|   \_____/       \_____/ A4    \_____/ B3    \_____/       \_____/       \_____/    |
|   /     \       /     \       /     \       /     \       /     \       /     \    |
|  /       \_____/ C12   \_____/ D1    \_____/ B2    \_____/ C4    \_____/       \   |
|  \       /     \       /     \       /     \       /     \       /     \       /   |
|   \_____/       \_____/       \_____/ D3    \_____/       \_____/       \_____/    |
|   /     \       /     \       /     \       /     \       /     \       /     \    |
|  /       \_____/ C11   \_____/ D2    \_____/       \_____/ C5    \_____/       \   |
|  \       /     \       /     \       /     \       /     \       /     \       /   |
|   \_____/       \_____/ C10   \_____/       \_____/ C6    \_____/       \_____/    |
|   /     \       /     \       /     \       /     \       /     \       /     \    |
|  /       \_____/       \_____/ C9    \_____/ C7    \_____/       \_____/       \   |
|  \       /     \       /     \       /     \       /     \       /     \       /   |
|   \_____/       \_____/       \_____/ C8    \_____/       \_____/       \_____/    |
|         \       /     \       /     \       /     \       /     \       /          |
|          \_____/       \_____/       \_____/       \_____/       \_____/           |
|                \       /     \       /     \       /     \       /                 |
|                 \_____/       \_____/       \_____/       \_____/                  |
|                       \       /     \       /     \       /                        |
|                        \_____/       \_____/       \_____/                         |
|                              \       /     \       /                               |
|                               \_____/       \_____/                                |
|                                     \       /                                      |
|                                      \_____/                                       |
|____________________________________________________________________________________|
</pre>
<h3>
test_004</h3>
&nbsp;&nbsp;&nbsp;&nbsp;
Here a one ring set is shown after one tubulin group has been rotated.
A1, A2, and A3 refer to a group labeled 'A' where
Strands 1, 2, and 3 have been rotated clockwise.
See Figure 0 to see the original locations of these strands.
            <h5>
Figure 4</h5>
<pre>
 ______________________________ 
|            _____             |
|           /     \            |
|     _____/       \_____      |
|    /     \       /     \     |
|   /       \_____/ A1    \    |
|   \       /     \       /    |
|    \_____/ A3    \_____/     |
|    /     \       /     \     |
|   /       \_____/ A2    \    |
|   \       /     \       /    |
|    \_____/       \_____/     |
|          \       /           |
|           \_____/            |
|______________________________|
</pre>
<h3>
test_005</h3>
&nbsp;&nbsp;&nbsp;&nbsp;
Here a three ring set is shown after three tubulin groups have been rotated.
Note that group C is a set of all strands in the outer ring rotated clockwise.
            <h5>
Figure 5</h5>
<pre>
 _________________________________________________________ 
|                          _____                          |
|                         /T37  \                         |
|                   _____/ S36   \_____                   |
|                  /T36  \ R3    /T20  \                  |
|            _____/ S35   \_____/ S37   \_____            |
|           /T35  \ R3    /T19  \ R3    /T21  \           |
|     _____/ S34   \_____/ S19   \_____/ S20   \_____     |
|    /T34  \ R3    /T18  \ R2    /T8   \ R3    /T22  \    |
|   / S33   \_____/ S7    \_____/ S8    \_____/ S21   \   |
|   \ R3    /T17  \ R2    /T7   \ R2    /T9   \ R3    /   |
|    \_____/ S18   \_____/ S6    \_____/ S9    \_____/    |
|    /T33  \ R2    /T6   \ R1    /T2   \ R2    /T23  \    |
|   / S32   \_____/ S16   \_____/ S1    \_____/ S22   \   |
|   \ R3    /T16  \ R1    /T1   \ R1    /T10  \ R3    /   |
|    \_____/ S17   \_____/ S3    \_____/ S10   \_____/    |
|    /T32  \ R2    /T5   \ R0    /T3   \ R2    /T24  \    |
|   / S31   \_____/ S4    \_____/ S2    \_____/ S23   \   |
|   \ R3    /T15  \ R1    /T4   \ R1    /T11  \ R3    /   |
|    \_____/ S15   \_____/ S14   \_____/ S11   \_____/    |
|    /T31  \ R2    /T14  \ R1    /T12  \ R2    /T25  \    |
|   / S30   \_____/ S5    \_____/ S12   \_____/ S24   \   |
|   \ R3    /T30  \ R2    /T13  \ R2    /T26  \ R3    /   |
|    \_____/ S29   \_____/ S13   \_____/ S25   \_____/    |
|          \ R3    /T29  \ R2    /T27  \ R3    /          |
|           \_____/ S28   \_____/ S26   \_____/           |
|                 \ R3    /T28  \ R3    /                 |
|                  \_____/ S27   \_____/                  |
|                        \ R3    /                        |
|                         \_____/                         |
|_________________________________________________________|
</pre>
<h3>
test_006</h3>
&nbsp;&nbsp;&nbsp;&nbsp;
Here a six ring set is shown after three tubulin groups have been rotated.
Note that group C is a set of all strands in
the 2nd to outer ring rotated clockwise.
Note that group E is a set of all strands in
the next inner ring rotated clockwise.
Each group of strands may be rotated separately in either direction.
            <h5>
Figure 6</h5>
<pre>
 ____________________________________________________________________________________ 
|                                       _____                                        |
|                                      /     \                                       |
|                                _____/       \_____                                 |
|                               /     \       /     \                                |
|                         _____/       \_____/       \_____                          |
|                        /     \       /     \       /     \                         |
|                  _____/       \_____/ C23   \_____/       \_____                   |
|                 /     \       /     \       /     \       /     \                  |
|           _____/       \_____/ C22   \_____/ C24   \_____/       \_____            |
|          /     \       /     \       /     \       /     \       /     \           |
|    _____/       \_____/ C21   \_____/ E17   \_____/ C1    \_____/       \_____     |
|   /     \       /     \       /     \       /     \       /     \       /     \    |
|  /       \_____/ C20   \_____/ E16   \_____/ E18   \_____/ C2    \_____/       \   |
|  \       /     \       /     \       /     \       /     \       /     \       /   |
|   \_____/ C19   \_____/ E15   \_____/       \_____/ E1    \_____/ C3    \_____/    |
|   /     \       /     \       /     \       /     \       /     \       /     \    |
|  /       \_____/ E14   \_____/ A2    \_____/       \_____/ E2    \_____/       \   |
|  \       /     \       /     \       /     \       /     \       /     \       /   |
|   \_____/ C18   \_____/ A3    \_____/ A1    \_____/       \_____/ C4    \_____/    |
|   /     \       /     \       /     \       /     \       /     \       /     \    |
|  /       \_____/ E13   \_____/ A5    \_____/ B1    \_____/ E3    \_____/       \   |
|  \       /     \       /     \       /     \       /     \       /     \       /   |
|   \_____/ C17   \_____/ A4    \_____/ B3    \_____/       \_____/ C5    \_____/    |
|   /     \       /     \       /     \       /     \       /     \       /     \    |
|  /       \_____/ E12   \_____/ D1    \_____/ B2    \_____/ E4    \_____/       \   |
|  \       /     \       /     \       /     \       /     \       /     \       /   |
|   \_____/ C16   \_____/       \_____/ D3    \_____/       \_____/ C6    \_____/    |
|   /     \       /     \       /     \       /     \       /     \       /     \    |
|  /       \_____/ E11   \_____/ D2    \_____/       \_____/ E5    \_____/       \   |
|  \       /     \       /     \       /     \       /     \       /     \       /   |
|   \_____/ C15   \_____/ E10   \_____/       \_____/ E6    \_____/ C7    \_____/    |
|   /     \       /     \       /     \       /     \       /     \       /     \    |
|  /       \_____/ C14   \_____/ E9    \_____/ E7    \_____/ C8    \_____/       \   |
|  \       /     \       /     \       /     \       /     \       /     \       /   |
|   \_____/       \_____/ C13   \_____/ E8    \_____/ C9    \_____/       \_____/    |
|         \       /     \       /     \       /     \       /     \       /          |
|          \_____/       \_____/ C12   \_____/ C10   \_____/       \_____/           |
|                \       /     \       /     \       /     \       /                 |
|                 \_____/       \_____/ C11   \_____/       \_____/                  |
|                       \       /     \       /     \       /                        |
|                        \_____/       \_____/       \_____/                         |
|                              \       /     \       /                               |
|                               \_____/       \_____/                                |
|                                     \       /                                      |
|                                      \_____/                                       |
|____________________________________________________________________________________|
</pre>

