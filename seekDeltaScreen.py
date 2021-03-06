#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sqlite3
import os
import sys
from pyh import *
import webbrowser

reload(sys)
sys.setdefaultencoding("utf-8")

OLD_SCREENLIB_PATH = 'oldscreenlib.sqlite'
NEW_SCREENLIB_PATH = 'newscreenlib.sqlite'
OLD_DB_PATH = '.\\_old_DB'
NEW_DB_PATH = '.\\_new_DB'
OLD_SCREEN_FILE_DIR = None
NEW_SCREEN_FILE_DIR = None

row0_bgcolor = 'DarkSlateGray'
row0_fgstyle = 'color:white;'
row2_bgcolor = 'DarkGreen'
row2_fgstyle = 'color:white;'

# Control values
REQUIRE_GENERATE_OLD_SCREENLIB = False
REQUIRE_GENERATE_NEW_SCREENLIB = True

scripter_dict = {
                      "yourID" : "Your Name",
                      }

def initializeOldScreenlib():
  print "****** Start to initialize Old Screenlib ******"
  global OLD_SCREEN_FILE_DIR, OLD_DB_PATH, OLD_SCREENLIB_PATH
  OLD_SCREEN_FILE_DIR = [] # Clear it before updating...
  for root,dirs,files in os.walk(OLD_DB_PATH):
    for filespath in files:
      if filespath.endswith('.sqlite'):
        OLD_SCREEN_FILE_DIR.append(os.path.join(root,filespath))

  conn = sqlite3.connect(OLD_SCREENLIB_PATH)
  cur = conn.cursor()
  cur.execute("create table screenlib (screenname text, scriptname text, build text, tags text)")
  conn.commit()
  conn.close()
  
  for i in range(1, len(OLD_SCREEN_FILE_DIR) + 1):
    conn = sqlite3.connect(OLD_SCREEN_FILE_DIR[i-1])
    cur = conn.cursor()
    cur.execute("select distinct screenname, scriptname, build, tags from screens where locale = "
                    + '\'' + 'en' + '\'')
    for f in cur.fetchall():
      conn = sqlite3.connect(OLD_SCREENLIB_PATH)
      cur = conn.cursor()
      cur.execute("insert into screenlib values (" + '\'' + f[0] + '\', \'' + f[1] + '\', \'' +
                      f[2] + '\', \'' + f[3] + '\' )')
      conn.commit()
      conn.close()
    conn.close()
    print "Analysed old sqlites " + str(i) + " / " + str(len(OLD_SCREEN_FILE_DIR))

def initializeNewScreenlib():
  print "****** Start to initialize New Screenlib ******"
  global NEW_SCREEN_FILE_DIR, NEW_DB_PATH, NEW_SCREENLIB_PATH

  NEW_SCREEN_FILE_DIR = [] # Clear it before updating...
  for root,dirs,files in os.walk(NEW_DB_PATH):
    for filespath in files:
      if filespath.endswith('.sqlite'):
        NEW_SCREEN_FILE_DIR.append(os.path.join(root,filespath))

  conn = sqlite3.connect(NEW_SCREENLIB_PATH)
  cur = conn.cursor()
  cur.execute("create table screenlib (screenname text, scriptname text, build text, tags text)")
  conn.commit()
  conn.close()
  
  for i in range(1, len(NEW_SCREEN_FILE_DIR)+1):
    conn = sqlite3.connect(NEW_SCREEN_FILE_DIR[i-1])
    cur = conn.cursor()
    cur.execute("select distinct screenname, scriptname, build, tags from screens where locale = "
                    + '\'' + 'en' + '\'')
    for f in cur.fetchall():
      conn = sqlite3.connect(NEW_SCREENLIB_PATH)
      cur = conn.cursor()
      cur.execute("insert into screenlib values (" + '\'' + f[0] + '\', \'' + f[1] + '\', \'' + f[2] + '\', \'' + f[3] + '\' )')
      conn.commit()
      conn.close()
    conn.close()

    print "Analysed new sqlites " + str(i) + " / " + str(len(NEW_SCREEN_FILE_DIR))

def seekDeltaScreen():
  new_conn = sqlite3.connect(NEW_SCREENLIB_PATH)
  new_cur = new_conn.cursor()
  new_cur.execute("select screenname from screenlib")
  new_screen_set = set([i[0] for i in new_cur.fetchall()])
  
  old_conn = sqlite3.connect(OLD_SCREENLIB_PATH)
  old_cur = old_conn.cursor()
  old_cur.execute("select screenname from screenlib")
  old_screen_set = set([i[0] for i in old_cur.fetchall()])
  
  missing_screen_list = list(old_screen_set - new_screen_set )
  missing_screen_list.sort()
  new_screen_list =  list(new_screen_set - old_screen_set)
  new_screen_list.sort()
  
  delta_screen_page = PyH('Check screen list change bewteen AViK Rounds')
  delta_screen_page << h1('Missing Screen List')
  
  # The HTML result page will be below
  # Missing Screen List
  #     tr0          No.          Screen            Script           Label         Scriptor
  #     tr1*n           1         ScreenA        mycode.js           Test_R1    Your Name
  # New Screen List
  #     tr2          No.          Screen            Script           Label         Scriptor
  #     tr3*n         1           ScreenB          mycode.js       Test_R1      Your Name
  
  if (0 == len(missing_screen_list)):
    delta_screen_page << p('No missing screen found.')
  else:
    missing_screen_tab = delta_screen_page << table(border = "1")
    tr0 = missing_screen_tab << tr()
    tr0 << td('No.', align="right", bgcolor=row0_bgcolor, 
                  style=row0_fgstyle) + td('Screen', bgcolor=row0_bgcolor, 
                  style=row0_fgstyle) + td('Script', bgcolor=row0_bgcolor, 
                  style=row0_fgstyle) + td('Label', bgcolor=row0_bgcolor,
                  style=row0_fgstyle) + td('Scriptor', bgcolor=row0_bgcolor,
                  style=row0_fgstyle)

    index = 1 # Give index to table of missing screen
    #~ for i in missing_screen_set:
    for i in range(0, len(missing_screen_list)):
      tr1 = missing_screen_tab << tr()
      old_cur.execute("select scriptname, build, tags from screenlib where screenname = "
                            + '\'' + missing_screen_list[i] + '\'')
      for j in old_cur.fetchall():
        tr1 << td(str(index)) << td(str(missing_screen_list[i])) << td(j[0]) << td(j[1])
        tag_dict = eval(j[2])
        if 'executor' in tag_dict:
          tr1 << td(scripter_dict[eval(j[2])['executor'].lower()])
        else:
          tr1 << td('null')
      index +=1
  old_conn.close()

  delta_screen_page << h1('New Screen List')
  if (0 == len(new_screen_list)):
    delta_screen_page << p('No new screen found.')
  else:
    new_screen_tab = delta_screen_page << table(border = "1")
    tr2 = new_screen_tab << tr()
    tr2 << td('No.', align="right", bgcolor=row2_bgcolor, 
                  style=row2_fgstyle) + td('Screen', bgcolor=row2_bgcolor, 
                  style=row2_fgstyle) + td('Script', bgcolor=row2_bgcolor, 
                  style=row2_fgstyle) + td('Label', bgcolor=row2_bgcolor,
                  style=row2_fgstyle) + td('Scriptor', bgcolor=row2_bgcolor,
                  style=row2_fgstyle)

    index = 1 # Give index to table of missing screen
    #~ for i in new_screen_set:
    for i in range(0, len(new_screen_list)):
      tr3 = new_screen_tab << tr()
      new_cur.execute("select scriptname, build, tags from screenlib where screenname = "
                              + '\'' + new_screen_list[i] + '\'')
      for f in new_cur.fetchall():
        tr3 << td(str(index)) << td(str(new_screen_list[i])) << td(f[0]) << td(f[1])
        tag_dict = eval(f[2])
        if 'executor' in tag_dict:
          tr3 << td(scripter_dict[tag_dict['executor'].lower()])
        else:
          tr3 << td('null')
      index +=1
  new_conn.close()
  
  delta_screen_page.printOut("test_delt_page.html")
  webbrowser.open("test_delt_page.html")
    
  
def main():

  if REQUIRE_GENERATE_OLD_SCREENLIB:
    initializeOldScreenlib()

  if REQUIRE_GENERATE_NEW_SCREENLIB:
    initializeNewScreenlib()
  
  seekDeltaScreen()

main()
