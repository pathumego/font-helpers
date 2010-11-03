#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  Copyright (C) 2010 Andrey V. Panov
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see "http://www.gnu.org/licenses/".
#
#   This fontforge script removes empty (i.e. zero) kerning pairs from font

import fontforge
import sys, getopt

def usage():
  print " -i file, --input=file     	input font file"
  print " -o file, --output=file    	output font file"
  print " -s, --subtable=\"string\"	kerning subtable"
  print " -t, --threshold=int      	remove kern |offsets| <= threshold (default 0)"

try:
  opts, args = getopt.getopt(sys.argv[1:], "hi:s:o:t:", ["help", "input=", "subtable=", "output=", "threshold="])
except getopt.GetoptError, err:
  print "unrecognized option"
  usage()
  sys.exit(2)
outfile = None
font_name = None
kern_table = "LGC kerning subtable"
kern_look = "LGC kerning"
threshold = 0
for (o, a) in opts:
  if o in ("-i", "--input"):
    font_name = a
  elif o in ("-h", "--help"):
    usage()
    sys.exit()
  elif o in ("-o", "--output"):
    outfile = a
  elif o in ("-s", "--subtable"):
    kern_table = a
  elif o in ("-t", "--threshold"):
    threshold = int(a)

if not outfile:
  outfile = font_name
#font_name = sys.argv[1]
font = fontforge.open(font_name)
font = fontforge.activeFont()
font.selection.all()
selection = font.selection.byGlyphs
for glyf in selection:
  if glyf.isWorthOutputting:
    oldtable = glyf.getPosSub(kern_table)
    if len(oldtable):
      #print oldtable
      newtable = ()
      changekern = 0
      for subtable in oldtable:
        if subtable[1] == 'Pair':
          temp = abs(subtable[5])
          if temp > threshold:
	    newtable += subtable,
	  elif temp <= threshold:
	    changekern = 1
      if changekern:
        glyf.removePosSub(kern_table)
        for subtable in newtable:
          #print subtable
          glyf.addPosSub(subtable[0],subtable[2],subtable[3],\
          subtable[4],subtable[5],subtable[6],subtable[7],\
          subtable[8],subtable[9],subtable[10])

font.save(outfile)
