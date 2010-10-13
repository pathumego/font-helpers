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
#   This fontforge script creates truetype instructions for accented glyphs,
#   mostly Latin or Cyrillic ones. The produced file must be compiled with
#   xgridfit.
#
import fontforge
import sys, re, getopt
import unicodedata

strip_suff = re.compile("\..*$", re.I)

# Symmetric accents which should be centered
sym_accents = ("cyrbreve", "cyrBreve", "dotaccent", "macron", "circumflex", \
"caron", "breve", "dieresis", "dotbelowcomb", "tidle", "ring", "uni0302", \
"uni0304", "uni0306", "uni0307", "uni0308", "uni030A", "uni030C", "uni0311")
macfun="call-macro"

sym_bases = (u'A', u'H', u'I', u'M', u'N', u'O', u'T', u'U', u'V', u'W', u'X', u'Y', u'ı', u'l', u'm', u'n', u'o', u'v', u'w', u'x', u'y', u'А', u'Ж', u'И', u'М', u'Н', u'О', u'П', u'У', u'Х', u'Ч', u'Ы', u'ж', u'и', u'н', u'о', u'п', u'у', u'х', u'ч', u'ы')

up_anc_bases = (u'C', u'G', u'Q', u'S', u'a', u'c', u'e', u'f', u's', u'ſ', u'З', u'О', u'С', u'Э', u'а', u'е', u'з', u'о', u'с', u'э', u'Ә', u'ә')

tm = (1.0, 0.0, 0.0, 1.0)

def mat_mult(m1,m2):
  return (m1[0]*m2[0] + m1[2]*m2[1], m1[1]*m2[0] + m1[3]*m2[1], \
  m1[0]*m2[2] + m1[2]*m2[3], m1[1]*m2[2] + m1[3]*m2[3])

def extrema_points(glyf):
  global font, subref, point_bot, point_left, point_top, point_right, point_num, point_bot2, point_top2, tm
  if  not(subref):
    point_bot = (0.0, 32768.0, 0)
    point_top = (0.0, -32768.0, 0)
    point_left = (32768.0, 0.0, 0)
    point_right = (-32768.0, 0.0, 0)
    point_bot2 = (0.0, 32768.0, 0)
    point_top2 = (0.0, -32768.0, 0)
  for contour in font[glyf].foreground:
    for point in contour:
      point_x = point.x*tm[0]+point.y*tm[2]+shift_x
      point_y = point.x*tm[1]+point.y*tm[3]+shift_y
      #print point_x, point_y, point_num
      if point_y < point_bot[1]:
        point_bot = (point_x, point_y, point_num)
      if point_y > point_top[1]:
        point_top = (point_x, point_y, point_num)
      if point_x < point_left[0]:
        point_left = (point_x, point_y, point_num)
      if point_x > point_right[0]:
        point_right = (point_x, point_y, point_num)
      if point_y <= point_bot[1]:
        point_bot2 = (point_x, point_y, point_num)
      if point_y >= point_top[1]:
        point_top2 = (point_x, point_y, point_num)
      point_num += 1

def ref_data(ref, ref_cont, glyfname):
  global shift_x, shift_y, cont_num, point_num, ref_type, basedata, accdata, point_bot, point_left, point_top, point_right, point_bot2, point_top2
  #print ref[0], ref_cont,  len(font[ref[0]].references)
  cont_num_prev = cont_num
  cont_num += ref_cont
  reftemp = extrema_points(ref[0])
  if ref_type == 'Ll' or ref_type == 'Lu':
    basedata += (point_bot, point_left, point_top, point_right, \
    range(cont_num_prev,cont_num), glyfname, point_bot2, point_top2)
  elif ref_type == 'Mn' or ref_type == 'Sk' or ref_type == 'Lm':
    accdata += (point_bot, point_left, point_top, point_right, \
    range(cont_num_prev,cont_num), glyfname, point_bot2, point_top2),

def dig_subrefs(refs, glyfname):
  global font, shift_x, shift_y, cont_num, point_num, ref_type, basedata, accdata, cont_num_prev, tm
  for ref in refs:
    tm_prev = tm
    shift_x_prev = shift_x
    shift_y_prev = shift_y
    tm = mat_mult(ref[1][0:4], tm) # multiply transform matrices
    #det = ref[1][0]*ref[1][3] - ref[1][1]*ref[1][2]
    #repm = (ref[1][3]/det, -ref[1][2]/det, -ref[1][1]/det, ref[1][0]/det)
    shift_x = ref[1][4]*tm_prev[0] + ref[1][5]*tm_prev[2] + shift_x_prev
    shift_y = ref[1][4]*tm_prev[1] + ref[1][5]*tm_prev[3] + shift_y_prev
    ref_cont = len(font[ref[0]].foreground)
    ref_ref = font[ref[0]].references
    if ref_cont > 0:
      cont_num += ref_cont
      reftemp = extrema_points(ref[0])
    elif len(ref_ref) >= 1:
      dig_subrefs(ref_ref, glyfname)
    shift_x = shift_x_prev
    shift_y = shift_y_prev
    tm = tm_prev
    #tm = mat_mult(repm, tm)

def print_center_accent(f, point_base_left, point_base_right, point_acc_left, point_acc_right):
  global glyph_head_printed, macfun
  if not(glyph_head_printed):
    glyph_head_printed = 1
    f.write(glyph_head % glyf.glyphname)
  f.write("  <set-vectors axis=\"x\"/>\n")
  f.write("  <"+macfun+" name=\"center-accent\">\n")
  f.write("   <with-param name=\"point-base-left\" value=\"%d\"/>\n" % point_base_left)
  f.write("   <with-param name=\"point-base-right\" value=\"%d\"/>\n" % point_base_right)
  f.write("   <with-param name=\"point-acc-left\" value=\"%d\"/>\n" % point_acc_left)
  f.write("   <with-param name=\"point-acc-right\" value=\"%d\"/>\n" % point_acc_right)
  f.write("  </"+macfun+">\n  <shift>\n   <reference>\n    <point num=\"%d\"/>\n   </reference>\n" % point_acc_left)
  for i in t[4]:
    f.write("   <contour num=\"%d\"/>\n" % i)
  f.write("  </shift>\n")

def print_shift_accent(f, point_base_left, point_base_right, point_acc_left, point_acc_right):
  global glyph_head_printed, macfun
  if not(glyph_head_printed):
    glyph_head_printed = 1
    f.write(glyph_head % glyf.glyphname)
  f.write("  <set-vectors axis=\"x\"/>\n")
  f.write("  <"+macfun+" name=\"shift-accent\">\n")
  f.write("   <with-param name=\"point-base-left\" value=\"%d\"/>\n" % point_base_left)
  f.write("   <with-param name=\"point-base-right\" value=\"%d\"/>\n" % point_base_right)
  f.write("   <with-param name=\"point-acc-left\" value=\"%d\"/>\n" % point_acc_left)
  f.write("   <with-param name=\"point-acc-right\" value=\"%d\"/>\n" % point_acc_right)
  f.write("  </"+macfun+">\n  <shift>\n   <reference>\n    <point num=\"%d\"/>\n   </reference>\n" % point_acc_left)
  for i in t[4]:
    f.write("   <contour num=\"%d\"/>\n" % i)
  f.write("  </shift>\n")

def usage():
  print " -i file, --input=file     input truetype font file"
  print " -o file, --output=file    output xgridfit file"
  print " -s file, --skipfile=file  skip from instructing glyphs whose names are listed in file"
  print " -v , --only-vertical      add only instructions for vertical placement (off)"
  print " -c , --center             add instructions for centering some accents (off)"
  print " -j , --instruct-j         instruct \"j\" (off)"
  print " -f , --function           use function tags instead of macros (off)"

try:
  opts, args = getopt.getopt(sys.argv[1:], "hvcjfi:o:s:", ["help", "only-vertical", "center", "instruct-j", "function", "input=", "output=", "skipfile="])
except getopt.GetoptError, err:
  print "unrecognized option"
  usage()
  sys.exit(2)
outfile = None
font_name = None
skipfile = None
only_vertical = 0
inst_sym = 0
inst_j = 0
skiplist = []
skip = 0
for (o, a) in opts:
  if o in ("-i", "--input"):
    font_name = a
  elif o in ("-h", "--help"):
    usage()
    sys.exit()
  elif o in ("-o", "--output"):
    outfile = a
  elif o in ("-v", "--only-vertical"):
    only_vertical = 1
  elif o in ("-c", "--center") and not only_vertical:
    inst_sym = 1
  elif o in ("-j", "--instruct-j") and not only_vertical:
    inst_j = 1
  elif o in ("-f", "--function") and not only_vertical:
    macfun="call-function"
  elif o in ("-s", "skipfile"):
    skipfile = a
#font_name = sys.argv[1]
if skipfile:
  f = open(skipfile, 'r')
  skiplist = re.split('\s',f.read())
  f.close()
  skip = len(skiplist)
font = fontforge.open(font_name)
f = open(outfile, 'w')
font.selection.all()
#font.selection.select("aacute","edieresis","uni1E69","afii10110","uni04F3","Ncaron","uni0213")
selection = font.selection.byGlyphs
f.write("<?xml version=\"1.0\"?>\n<xgridfit xmlns=\"http://xgridfit.sourceforge.net/Xgridfit2\">\n<!-- GENERATED FILE, DO NOT EDIT -->\n")
for glyf in selection:
  if glyf.isWorthOutputting and not(len(glyf.ttinstrs)):
    if skip and glyf.glyphname in skiplist:
      continue
    #print glyf.glyphname
    refs = glyf.references
    #print len(refs), refs, len(glyf.foreground)
    subref = 0
    cont_num = 0
    point_num = 0
    basedata = ()
    accdata = ()
    for ref in refs:
      tm = ref[1][0:4] # transform matrix of reference
      shift_x = ref[1][4]
      shift_y = ref[1][5]
      ref_cont = len(font[ref[0]].foreground)
      uni_index = fontforge.unicodeFromName(strip_suff.split(ref[0])[0])
      #print uni_index,
      if ref[0] == "cyrbreve" or ref[0] == "cyrBreve":
	ref_type = 'Mn'
      elif uni_index >= 0:
	ref_type = unicodedata.category(unichr(uni_index))
      else:
        break
      #print ref_type
      if ref_cont > 0:
        subref = 0
	ref_data(ref, ref_cont, ref[0])
      elif len(font[ref[0]].references) >= 1:
        subref = 1
	point_bot = (0.0, 32768.0, 0)
	point_top = (0.0, -32768.0, 0)
	point_left = (32768.0, 0.0, 0)
	point_right = (-32768.0, 0.0, 0)
	point_bot2 = (0.0, 32768.0, 0)
	point_top2 = (0.0, -32768.0, 0)
        cont_num_prev = cont_num
        dig_subrefs(font[ref[0]].references, ref[0])
	if ref_type == 'Ll' or ref_type == 'Lu':
	  basedata += (point_bot, point_left, point_top, point_right, \
	  range(cont_num_prev,cont_num), ref[0], point_bot2, point_top2)
	elif ref_type == 'Mn' or ref_type == 'Sk' or ref_type == 'Lm':
	  accdata += (point_bot, point_left, point_top, point_right, \
	  range(cont_num_prev,cont_num), ref[0], point_bot2, point_top2),
    #print basedata, accdata
    glyph_head_printed = 0
    glyph_head = " <glyph ps-name=\"%s\" init-graphics=\"yes\">\n"
    if basedata and accdata:
      for t in accdata:
        if not len(t[4]):
	  continue
	if t[0][1] > basedata[2][1]: # above accent
	  if not(glyph_head_printed):
	    glyph_head_printed = 1
	    f.write(glyph_head % glyf.glyphname)
	  f.write("  <set-vectors axis=\"y\"/>\n")
	  f.write("  <set-equal target=\"temp\" source=\"%d -- %d\"/>\n" % (basedata[2][2], t[0][2]))
	  f.write("  <if test=\"temp &lt; 0.6p\">\n")
	  f.write("   <shift-absolute pixel-distance=\"negative(round(temp)) + 1.0p\">\n    <point num=\"%d\"/>\n" % t[0][2])
	  f.write("   </shift-absolute>\n   <shift>\n    <reference>\n     <point num=\"%d\"/>\n    </reference>\n" % t[0][2])
	  for i in t[4]:
	    f.write("    <contour num=\"%d\"/>\n" % i)
	  f.write("   </shift>\n  </if>\n")
	elif t[2][1] < basedata[0][1]: # below accent
	  if not(glyph_head_printed):
	    glyph_head_printed = 1
	    f.write(glyph_head % glyf.glyphname)
	  f.write("  <set-vectors axis=\"y\"/>\n")
	  f.write("  <set-equal target=\"temp\" source=\"%d -- %d\"/>\n" % (t[2][2], basedata[0][2]))
	  f.write("  <if test=\"temp &lt; 0.6p\">\n   <command name=\"RDTG\"/>\n" )
	  f.write("   <shift-absolute pixel-distance=\"round(temp) - 1.0p\">\n    <point num=\"%d\"/>\n" % t[2][2])
	  f.write("   </shift-absolute>\n   <command name=\"RTG\"/>\n   <shift>\n    <reference>\n     <point num=\"%d\"/>\n    </reference>\n" % t[2][2])
	  for i in t[4]:
	    f.write("    <contour num=\"%d\"/>\n" % i)
	  f.write("   </shift>\n  </if>\n")
	base_unum = fontforge.unicodeFromName(strip_suff.split(basedata[5])[0])
	if base_unum > 0:
	  ubase = unichr(base_unum)
	else:
	  ubase = u' '
	if inst_j and glyf.glyphname == "j": # instruct j
	  if not(glyph_head_printed):
	    glyph_head_printed = 1
	    f.write(glyph_head % glyf.glyphname)
	  f.write("  <set-vectors axis=\"x\"/>\n")
	  f.write("  <set-equal target=\"temp\" source=\"round(%d -- %d)\"/>\n" % (basedata[3][2], t[3][2]))
	  f.write("  <if test=\"temp != 0.0\">\n   <shift-absolute pixel-distance=\"negative(temp)\">\n")
	  f.write("    <point num=\"%d\"/>\n   </shift-absolute>\n" % t[3][2])
	  f.write("   <shift>\n    <reference>\n     <point num=\"%d\"/>\n    </reference>\n" % t[3][2])
	  f.write("    <contour num=\"%d\"/>\n" % t[4][0])
	  f.write("   </shift>\n  </if>\n")
	elif inst_sym and strip_suff.split(t[5])[0] in sym_accents and ubase in sym_bases: # center accent along x
	  print_center_accent(f, basedata[1][2], basedata[3][2], t[1][2], t[3][2])
	elif inst_sym and strip_suff.split(t[5])[0] in sym_accents and ubase in up_anc_bases and t[0][1] > basedata[2][1]: # center accent against extremum
	  diff_max = basedata[7][2] - basedata[2][2]
	  if diff_max == 1:
	    print_center_accent(f, basedata[2][2], basedata[7][2], t[1][2], t[3][2])
	  elif diff_max == 2 or diff_max == 0:
	    if not(glyph_head_printed):
	      glyph_head_printed = 1
	      f.write(glyph_head % glyf.glyphname)
	    f.write("  <set-vectors axis=\"x\"/>\n")
	    f.write("  <"+macfun+" name=\"center-accent-extremum\">\n")
	    f.write("   <with-param name=\"point-base-anchor\" value=\"%d\"/>\n" % ((basedata[2][2] + basedata[7][2])/2))
	    f.write("   <with-param name=\"point-acc-left\" value=\"%d\"/>\n" % t[1][2])
	    f.write("   <with-param name=\"point-acc-right\" value=\"%d\"/>\n" % t[3][2])
	    f.write("  </"+macfun+">\n  <shift>\n   <reference>\n    <point num=\"%d\"/>\n   </reference>\n" % t[1][2])
	    for i in t[4]:
	      f.write("   <contour num=\"%d\"/>\n" % i)
	    f.write("  </shift>\n")
	elif t[1][0] >= basedata[1][0] and t[3][0] <= basedata[3][0] and not(only_vertical): # shift accent along x
	  print_shift_accent(f, basedata[1][2], basedata[3][2], t[1][2], t[3][2])
      if glyph_head_printed:
	f.write(" </glyph>\n")
f.write("</xgridfit>")
f.close()

