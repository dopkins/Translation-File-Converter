# This program creates a log of all files/dirs that are different between two
# directories specified in the UI.
import wx, os, re, shutil, codecs, sys
from markdown import markdown
from time import strftime,localtime
from re import search
from zipfile import ZipFile



def selSwitcher(e):
#If the conversion mode is one designed for folders, use the
#directory picker. If it is for files, use the file picker.
    if lblASource.Label == text['aSourceF']:
        selectFile(e)
    elif lblASource.Label == text['aSourceD']:
        selectDir(e)

# Choose a directory and enter it to the field
def selectDir(e):
    dlg = wx.DirDialog(None, text['dirDlg'])
    if dlg.ShowModal() == wx.ID_OK:
        if e.GetId() == 1:
            fieldASource.SetValue(dlg.GetPath())
        elif e.GetId() == 2:
            fieldBSource.SetValue(dlg.GetPath())
        elif e.GetId() == 3:
            fieldCSource.SetValue(dlg.GetPath())

# Choose a file and enter it to the field
def selectFile(e):
    dlg = wx.FileDialog(None, text['fileDlg'])
    if dlg.ShowModal() == wx.ID_OK:
        if e.GetId() == 1:
            fieldASource.SetValue(dlg.GetPath())
        elif e.GetId() == 2:
            fieldBSource.SetValue(dlg.GetPath())
        elif e.GetId() == 3:
            fieldCSource.SetValue(dlg.GetPath())
        
def runProgram(e):
    lblStatus.SetLabel(text['statusWorking'])
    nr = conversionMode.CurrentSelection
    source = fieldASource.Value
    origDir = fieldCSource.Value
    if fieldBSource.Value == '':
        target = os.path.join(os.curdir,strftime('%Y-%m-%d', localtime()))
        make_dir(target)
    else:
        target = fieldBSource.Value
        
    if nr == 0:
        md2html(source, target)
    elif nr == 1:
        html2md(source, origDir, target)
    elif nr == 2:
        uit2xml(source, target)
    elif nr == 3:
        xml2uit(source, target)
    elif nr == 4:
        jdoc2across(source, target)
    elif nr == 5:
        across2jdoc(source, origDir, target)
        
    dlg = wx.MessageDialog(None, text['lblFinished'], text['progname'], wx.OK)
    dlg.ShowModal()
    lblStatus.SetLabel(text['statusIdle'])
    

def md2html(source, target):
    """Converts all MD files in a dir to a single across-capable HTML file"""
    print source
    print target
    if source != target and os.path.isfile(source) and \
       os.path.isdir(target):
        xml = codecs.open(os.path.join(target,strftime('%Y-%m-%d-', localtime()) + os.path.basename(os.path.normpath(source))[:-4] + '.html'), mode='w', encoding='utf-8')
        xml.write(u'\ufeff')
        xml.write('<?xml version="1.0"?>\n')
        xml.write('<xml>\n')
        z = ZipFile(source, 'r')
        for f in z.namelist():
            if f.endswith('.md'):
                xml.write('<md_doc name="' + f.replace('\\','/') + '">\n')
                with z.open(f, 'r') as d:
                    content = d.read()
                    html = markdown(codecs.decode(content, 'utf-8'))
                    xml.write(html)
                xml.write('\n</md_doc>\n')
        xml.write('</xml>')
        xml.close()
    else:
        dlg = wx.MessageDialog(None, text['dirErr'], text['ttlErr'], wx.OK|wx.ICON_ERROR)
        dlg.ShowModal()
        return

def html2md(source, origDir, target):
    """Converts a html file checked out of Across back into an MD structure"""
    print source
    print origDir
    print target
    if source != target and os.path.isfile(source) and \
       os.path.isdir(target) and origDir.endswith('.zip') and not os.path.exists(os.path.join(target, 'Markdown')):            
        target = make_dir(os.path.join(target, 'Markdown'))
        start = '<md_doc name="(.+)">'
        end = '</md_doc>'
        with open(source) as translation:
            lines = translation.readlines()
            for index,line in enumerate(lines):
                newFile = re.match(start,line) # look for the start of the individual files
                if newFile:
                    newPair = os.path.split(newFile.group(1)) # extract tuple of path and file name
                    make_dir(os.path.join(target, newPair[0])) # create directory structure
                    if newFile.group(1)[0] != '/':
                        html = codecs.open(os.path.join(target, newFile.group(1)), 'w', encoding='utf-8')
                    else:
                        html = codecs.open(target + newFile.group(1), 'w', encoding='utf-8') #create individual mds
                    
                try:
                    if not re.match(end, line):
                        if not re.match(start, line):
                            html.write(line) # if the line is neither start nor end of a file, write the contents to the current html file
                    else:
                        html.close()
                except:
                    print '...' # this occurs e.g. at the start of the javadoc.html when no html var has been initialized
        origfiles = ZipFile(origDir, 'r')
        for orig_file in origfiles.infolist():
            if not orig_file.filename.endswith('.md'):
                print os.path.join(target, orig_file.filename[:orig_file.filename.rfind('/')+1])
                if orig_file.file_size == 0:
                    make_dir(os.path.join(target, orig_file.filename))
                else:
                    print 'extracting: ' + os.path.join(target, orig_file.filename)
                    data= origfiles.read(orig_file.filename)
                    temp = open(os.path.join(target, orig_file.filename), 'wb')
                    temp.write(data)
                    temp.close()
        origfiles.close()
    elif os.path.exists(os.path.join(target, 'Markdown')):
        dlg = wx.MessageDialog(None, text['dirErr'] + '\n' + text['dirExistsErr'] % os.path.join(target, 'Markdown')\
                               , text['ttlErr'], wx.OK|wx.ICON_ERROR)
        dlg.ShowModal()
        return
    else:
        dlg = wx.MessageDialog(None, text['dirErr'], text['ttlErr'], wx.OK|wx.ICON_ERROR)
        dlg.ShowModal()
        return

def jdoc2across(source, target):
    """Converts an HTML Javadoc directory to a single Across-capable HTML file"""
    print source
    print target
    if source != target and os.path.isfile(source) and \
       os.path.isdir(target):
        xml = open(os.path.join(target,strftime('%Y-%m-%d-', localtime()) + os.path.basename(os.path.normpath(source))[:-4] + '.html'), 'w')
        xml.write('<?xml version="1.0"?>\n')
        xml.write('<xml>\n')
        z = ZipFile(source, 'r')
        for f in z.namelist():
            if f.endswith('.html') or f.endswith('.htm'):
                xml.write('<jdoc name="' + f.replace('\\','/') + '">\n')
                with z.open(f,'r') as d:
                        content = d.readlines()
                        for index, line in enumerate(content):
                            xml.write(line)
                xml.write('</jdoc>\n')
        xml.write('</xml>')
        xml.close()

    else:
        dlg = wx.MessageDialog(None, text['dirErr'], text['ttlErr'], wx.OK|wx.ICON_ERROR)
        dlg.ShowModal()
        return

def across2jdoc(source, origDir, target):
    """Converts an HTML checked out of Across back into a functioning Javadoc"""
    if source != target and os.path.isfile(source) and \
       os.path.isdir(target) and os.path.isfile(origDir) and not os.path.exists(os.path.join(target, 'Javadoc')):            
        target = make_dir(os.path.join(target, 'Javadoc'))
        start = '<jdoc name="(.+)">'
        end = '</jdoc>'
        with open(source) as translation:
            lines = translation.readlines()
            for index,line in enumerate(lines):
                newFile = re.match(start,line) # look for the start of the individual files
                if newFile:
                    newPair = os.path.split(newFile.group(1)) # extract tuple of path and file name
                    make_dir(os.path.join(target, newPair[0])) # create directory structure
                    if newFile.group(1)[0] != '/':
                        html = open(os.path.join(target, newFile.group(1)), 'w')
                    else:
                        html = open(target + newFile.group(1), 'w') #create individual htmls
                try:
                    if not re.match(end, line):
                        if not re.match(start, line):
                            html.write(line) # if the line is neither start nor end of a file, write the contents to the current html file
                    else:
                        html.close()
                except:
                    print '...' # this occurs e.g. at the start of the javadoc.html when no html var has been initialized
        origfiles = ZipFile(origDir, 'r')
        for non_html in origfiles.infolist():
            if not non_html.filename.endswith('.html'):
                print os.path.join(target,non_html.filename[:non_html.filename.rfind('/')+1])
                if non_html.file_size == 0:
                    make_dir(os.path.join(target,non_html.filename))
                else:
                    print 'extracting: ' + os.path.join(target, non_html.filename)
                    data = origfiles.read(non_html.filename)
                    temp = open(os.path.join(target, non_html.filename), 'wb')
                    temp.write(data)
                    temp.close()
        origfiles.close()
    elif os.path.exists(os.path.join(target, 'Javadoc')):
        dlg = wx.MessageDialog(None, text['dirErr'] + '\n' + text['dirExistsErr'] % os.path.join(target, 'Javadoc')\
                               , text['ttlErr'], wx.OK|wx.ICON_ERROR)
        dlg.ShowModal()
        return
    else:
        dlg = wx.MessageDialog(None, text['dirErr'], text['ttlErr'], wx.OK|wx.ICON_ERROR)
        dlg.ShowModal()
        return


def uit2xml(source,target):
    """Converts UIT to Across XML files"""
    dlg = wx.MessageDialog(None, 'Not yet implemented. Use classic TFC for now', 'Error', wx.OK)
    dlg.ShowModal()
    return

def xml2uit(source,target):
    """Converts Across XML files to UITs"""
    dlg = wx.MessageDialog(None, 'Not yet implemented. Use classic TFC for now', 'Error', wx.OK)
    dlg.ShowModal()
    return

def exit_program():
    sys.exit(0)


def switchUI(e): 
    nr = conversionMode.CurrentSelection
    if nr == 0: # md2html
        lblASource.SetLabel(text['aSourceF'])
        lblBSource.SetLabel(text['bSourceD'])
        topSizer.Hide(lineTwo)
    elif nr == 1: # html2md
        lblASource.SetLabel(text['aSourceF'])
        lblBSource.SetLabel(text['bSourceD'])
        topSizer.Show(lineTwo)
    elif nr == 2: # uit2xml
        lblASource.SetLabel(text['aSourceF'])
        lblBSource.SetLabel(text['bSourceF'])
        topSizer.Hide(lineTwo)
    elif nr == 3: # xml2uit
        lblASource.SetLabel(text['aSourceF'])
        lblBSource.SetLabel(text['bSourceF'])
        topSizer.Hide(lineTwo)
    elif nr == 4: # jdoc2across
        lblASource.SetLabel(text['aSourceF'])
        lblBSource.SetLabel(text['bSourceF'])
        topSizer.Hide(lineTwo)
    elif nr == 5: # across2jdoc
        lblASource.SetLabel(text['aSourceF'])
        lblBSource.SetLabel(text['bSourceD'])
        topSizer.Show(lineTwo)
    panel.Layout()

# Function looks for an existing dir with the input name, creates it if it doesn't exist
def make_dir(rawdir):
    try:
        os.stat(rawdir)
    except:
        os.makedirs(rawdir)
    return rawdir

def copypath(src, dst, ignore):
    """This is a reformulation / simplification of the shutil.copytree function, with some adjustments
I needed to make it work for my purposes."""
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore
    else:
        ignored_names = ''

    make_dir(dst)
    for name in names:
        if re.match(ignore, name):
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if os.path.isdir(srcname):
                copypath(srcname, dstname, ignore)
            else:
                shutil.copy2(srcname, dstname)
        except Error as err:
            return 'Error: ' + err.args[0]

    try:
        copystat(src, dst)
    except:
        print '...'


# Some drag-and-drop automatic operations
# if a file type is detected correctly, it is converted automatically
dnd = sys.argv[1:]
if dnd == []:
    pass
else:
    firstarg = dnd[0]
    directory = firstarg[:firstarg.rfind('\\')] # get dir of input file
    if len(dnd) == 1:
        for f in dnd:
            #directory = f[:f.rfind('\\')] # get current dir
            
            if f.endswith('.zip'): # either Javadoc or Markdown currently
                arc = ZipFile(f, 'r')
                for name in arc.namelist():
                    print name
                    if 'index.html' in name:
                        arc.close()
                        jdoc2across(f, directory)
                        exit_program()
                    elif name.endswith('.md'):
                        arc.close()
                        md2html(f, directory)
                        exit_program()
                    else:
                        pass
    elif len(dnd) == 2:
        if dnd[0].endswith('.zip') and dnd[1].endswith('.html'):
            zipsource = dnd[0]
            htmlsource = dnd[1]
        elif dnd[1].endswith('.zip') and dnd[0].endswith('.html'):
            zipsource = dnd[1]
            htmlsource = dnd[0]
        else:
            pass
        ziplist = ZipFile(zipsource, 'r')
        for f in ziplist.namelist():
            if f.endswith('.md'):
                print firstarg
                html2md(htmlsource, zipsource, directory)
                exit_program()
            elif f.endswith('index.html'):
                across2jdoc(htmlsource, zipsource, directory)
                exit_program()
            else:
                pass
    exit(1)


# Check for translation file
if not os.path.exists('lang.txt'):
    app = wx.App()
    err = wx.MessageDialog(None, 'Could not find lang.txt. Please create or rename a file in this directory to "lang.txt".', 'Error', wx.OK|wx.ICON_ERROR)
    if err.ShowModal() == wx.ID_OK:
        exit(1)

# Read translation file into dict
text = {}
with open('lang.txt') as texts:
    for line in texts.readlines():
        raw = search('(.+?)=(.*)', line)
        if raw:
            text[raw.group(1)]=raw.group(2)

# UI elements
app = wx.App(False)
frame = wx.Frame(None, wx.ID_ANY, text['progname']) 
panel = wx.Panel(frame, wx.ID_ANY)

font = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.BOLD)
lblASource = wx.StaticText(panel, wx.ID_ANY, text['aSourceF'])
lblASource.SetFont(font)
fieldASource = wx.TextCtrl(panel, wx.ID_ANY, style= wx.EXPAND )
btnASource = wx.Button(panel, id=1, label=text['browse'])
btnASource.Bind(wx.EVT_BUTTON, selSwitcher)

lblBSource = wx.StaticText(panel, wx.ID_ANY, text['bSourceF'])
lblBSource.SetFont(font)
fieldBSource = wx.TextCtrl(panel, wx.ID_ANY, style= wx.EXPAND )
btnBSource = wx.Button(panel, id=2, label=text['browse'])
btnBSource.Bind(wx.EVT_BUTTON, selSwitcher)

lblCSource = wx.StaticText(panel, wx.ID_ANY, text['cSourceF'])
lblCSource.SetFont(font)
fieldCSource=wx.TextCtrl(panel, wx.ID_ANY, style= wx.EXPAND)
btnCSource = wx.Button(panel, id=3, label=text['browse'])
btnCSource.Bind(wx.EVT_BUTTON, selectFile)

btnConvert = wx.Button(panel, wx.ID_ANY, text['run'])
btnConvert.Bind(wx.EVT_BUTTON, runProgram)
convertOpts = ['MD -> HTML', 'HTML -> MD', 'uit -> XML', 'XML -> UIT', 'Javadoc -> HTML', \
               'HTML -> Javadoc']
conversionMode = wx.ComboBox(panel, value=convertOpts[0], choices=convertOpts, style=wx.CB_READONLY)
conversionMode.Bind(wx.EVT_TEXT, switchUI)

lblStatus = wx.StaticText(panel, wx.ID_ANY, text['statusIdle'], size=(-1,50))

#Sizer elements
lineOne = wx.BoxSizer()
lineOne.Add(lblASource, 0, wx.ALL, 5)
lineOne.Add(fieldASource, 1, wx.ALL | wx.EXPAND, 5)
lineOne.Add(btnASource, 0, wx.ALL, 5)

lineTwo = wx.BoxSizer()
lineTwo.Add(lblCSource, 0, wx.ALL, 5)
lineTwo.Add(fieldCSource, 1, wx.ALL | wx.EXPAND, 5)
lineTwo.Add(btnCSource, 0, wx.ALL, 5)

lineThree = wx.BoxSizer()
lineThree.Add(lblBSource, 0, wx.ALL, 5)
lineThree.Add(fieldBSource, 1, wx.ALL | wx.EXPAND, 5)
lineThree.Add(btnBSource, 0, wx.ALL, 5)



lineFour = wx.BoxSizer()
lineFour.Add(btnConvert, 0, wx.ALL, 5)
lineFour.Add(conversionMode, 0, wx.ALL, 5)

lineFive = wx.BoxSizer()
lineFive.Add(lblStatus, 1, wx.ALL|wx.EXPAND, 5)

topSizer = wx.BoxSizer(wx.VERTICAL)
topSizer.Add(lineOne, 0, wx.LEFT|wx.EXPAND, 5)
topSizer.Add(lineTwo, 0, wx.LEFT|wx.EXPAND, 5)
topSizer.Hide(lineTwo) # Only show if the original dir is required
topSizer.Add(lineThree, 0, wx.LEFT|wx.EXPAND, 5)
topSizer.Add(lineFour, 0, wx.LEFT|wx.EXPAND, 5)
topSizer.Add(lineFive, 0, wx.LEFT|wx.LEFT|wx.LEFT|wx.LEFT, 5)

panel.SetSizer(topSizer)
topSizer.Fit(panel)
panel.Layout()
frame.Show(True)     
app.MainLoop()
