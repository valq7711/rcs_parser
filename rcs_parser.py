# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Val
#
# Created:     29.10.2016
# Copyright:   (c) Val 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import re, os
from subprocess import Popen, PIPE
import argparse

RapydML_cmd = 'D:\\Program Files\\RapydML-master\\rml_build_nopause.bat'
RapydRS_cmd = 'D:\\Program Files\\RapydScript-master\\rs_build.bat'
tmp_ml_fname =       'd:\\tmp\\tmp_test.' # ml & html
tmp_templ_fname = 'd:\\tmp\\tmp_templ.' # ml & html




class ShellError(Exception):
	"""
	Helper class for standardizing error messages
	"""

	def __init__(self, message):
		self.message = message

	def __str__(self):
		return self.message

def buff_split(s):
    """
    split in 3 parts
    - html_tst
    - templates
    - RS script
    """
    _re = re.compile('^#-{3,} *< *(?:TEMPLATES|RS_SCRIPT) *> *-{3,}', flags = re.MULTILINE)
    return _re.split(s)

def write_html_tst(ml_s, html_fname):
    """
    ml_s - RapydML string
    """
    cmd = RapydML_cmd
    with open(tmp_ml_fname+'ml', 'w') as f:
    	f.write(ml_s)

    result = Popen([cmd, tmp_ml_fname+'ml', '&&',
                    'move', '/Y',tmp_ml_fname+'html',  html_fname],
    				stdout = PIPE, stderr = PIPE, shell = True).communicate()
    if result[1]:
        #print result[1].decode('cp866')
    	raise ShellError("'%s' triggered the following OS error: %s" %
       					('write_html_tst', result[1]))
    print 'write_html_tst: %s\n'% (tmp_ml_fname+'html'),
    print  result[0]
def ml_templ_to_html(ml_s):
    """
    ml_s - RapydML string
    """

    cmd = RapydML_cmd

    with open(tmp_templ_fname+'ml', 'w') as f:
    	f.write(ml_s)

    result = Popen([cmd, tmp_templ_fname+'ml','&&','type', tmp_templ_fname+'html'],
    				stdout = PIPE, stderr = PIPE, shell = True).communicate()
    if result[1]:
        #print result[1].decode('cp866')
    	raise ShellError("'%s' triggered the following OS error: %s" %
    					('ml_templ_to_html', result[1]))

    return result[0] #.decode('cp866') # html content


def split_templates_css(ml_s):
    ml_s = re.sub('^ *\n', '', ml_s, flags = re.MULTILINE)
    _re = re.compile(
        "^script *\( *type *= *(?:\"|')text */ *ractive(?:\"|') *, *id *= *(?:\"|')(?P<id>[0-9a-z_\-.]+)(?:\"|') *\) *:",
                        flags = re.MULTILINE | re.IGNORECASE)
    templs = _re.split(ml_s)
    ret = {}
    i = 0
    if templs[0]=='':
        templs.pop(0)
    while i <len(templs):

        templ_html = re.sub('^(    )|( *\r\n\|\n)', '', templs[i+1], flags = re.MULTILINE) # remove indent and empty lines
        #templ_html = re.sub('^ *\n', '', templ_html, flags = re.MULTILINE) # remove indent
        css, templ_html =  split_css( templ_html)
        ret[templs[i]] = dict(templ ='', css='')
        ret[templs[i]]['css'] = css
        ret[templs[i]]['templ'] =  ml_templ_to_html(templ_html)
        i+=2
    return ret

def split_css(ml_templ):
    """
    return  [css, ml_template]
    """
    re_css = re.compile( r'^( *)css *\( *\) *: *((?:\n\1 +.+)*\n?)', flags=re.MULTILINE | re.IGNORECASE)
    lst = re_css.split(ml_templ)
    if  len(lst) < 4:
        ret = ['', ml_templ]
    else:
        pref = lst[0]
        # lst[1] == '   ' - indent spaces
        css_def = lst[2] # css content
        rest = lst[3] # templ content
        if not re.sub('\n|\r| ','',css_def):
            css_def = ''
        ret = [css_def, pref + rest]
    return ret

def insert_templ(rs_s, templs):
    def replacer(m):
        id = m.group(1)
        s = '"""%s"""' % (re.sub('\r\n|\n', '', templs[id]['templ']))
        return s
    ret  = re.sub('@TMPL\( *(\w+) *\)', replacer, rs_s,  flags = re.MULTILINE )
    return ret

def insert_templ_css_tab(rs_s, templs):
    def templ_replacer(m):
        id = m.group(2)
        indent = ' '*(len(m.group(1)) + 4)
        s = m.group(1) + '"""<!-- %s --> %s"""' % ( id,re.sub('\r\n|\n', '\n'+indent, templs[id]['templ']))
        return s
    ret  = re.sub('^(.+)@TMPL\( *(\w+) *\)', templ_replacer, rs_s,  flags = re.MULTILINE )

    def css_replacer(m):
        id = m.group(2)
        indent = ' '*(len(m.group(1)) + 4)

        css = templs[id]['css']
        if not css:
            s = m.group(1) +  ('None #%s.css\n' % id)
        else:
            s = m.group(1) + \
                '"""/* %s.css */ %s"""' % ( id, re.sub('\r\n|\n', '\n'+indent, css))
        return s
    ret  = re.sub('^(.+)@CSS\( *(\w+) *\)', css_replacer, ret,  flags = re.MULTILINE )

    return ret


def make_pyj_js(rs_s, dest_base_fname):
    """
    produce 2 files
        - dest_base_fname.pyj
        - dest_base_fname.js
    rs_s - RapydScript string
    dest_base_fname - 'd:/dfsdf/sdfsdf/out_name' - no ext!
    """
    from os  import path

    cmd = RapydRS_cmd
    pyj_fname =  path.normpath( dest_base_fname+'.pyj')
    js_fname = path.normpath(dest_base_fname+'.js')

    with open(pyj_fname, 'w') as f:
    	f.write(rs_s)

    result = Popen([cmd, pyj_fname,'&&', 'type', js_fname],
    				stdout = PIPE, stderr = PIPE, shell = True).communicate()
    if result[1]:
    	raise ShellError("'%s' triggered the following OS error: %s" %
    					('ml_templ_to_html', result[1]))
    return result[0]


def main():
    s = """
html:
    head:
        fdfsdf
        sdf
        sdf
#--------- dfsdf
        sdfdfsdf
#---------  < TEMPLATES > ----------
script(type='text/ractive",id="templ0" ) :
    css():
        th {
            color:red;
        }
    div():
        'привет'
        'sdfsf "sdfsdf"  dsfsdf'
script(type='text/ractive",id="templ1" ) :
    css():
    head:
        meta(charset='utf-8'):
    div():
        'жаба'

#---------  < RS_SCRIPT > ----------
def main():
    a = b+1
    sdf = { t1 :  @TMPL( templ0  ),
            t2 :  @TMPL( templ1  ),
            t3: @CSS(templ0),
            t4: @CSS(templ1)

        }

#-------  < RS_SCRIPT1 > ----------
    sdf
"""

    parser = argparse.ArgumentParser()
    parser.add_argument('src', type = str, help = 'file.ml_cmp')
    parser.add_argument('-od','--outdir', type = str,
                    default = '',
                    help = 'output dir: abs - "d:/dir" or  relative - "bar/foo"')
    args = parser.parse_args()
    NP = os.path.normpath

    cmp_absbase_fname, ext = os.path.splitext(os.path.abspath(args.src))
    cmp_path, cmp_base_fname = os.path.split(cmp_absbase_fname)
    out_path = NP(os.path.join(cmp_path, args.outdir ))
    html_test_fname =  NP(os.path.join(out_path, cmp_base_fname +'_test.html' ))
    pyj_js_base_fname = NP(os.path.join(out_path, cmp_base_fname))


    with open(cmp_absbase_fname+ext, 'r') as f:
    	 ml_cmp = f.read()
    ml_test, raw_templates, rs_script =  buff_split(ml_cmp)
    templates = split_templates_css(raw_templates)
    # replace @TEMPL() and @CSS() in rs_script
    rs_script = insert_templ_css_tab(rs_script, templates)
    # write & compile scripts  - .pyj, .js
    make_pyj_js(rs_script, pyj_js_base_fname)
    write_html_tst(ml_test, html_test_fname)


if __name__ == '__main__':
    main()
