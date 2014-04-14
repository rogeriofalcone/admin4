# The Admin4 Project
# (c) 2013-2014 Andreas Pflug
#
# Licensed under the Apache License, 
# see LICENSE.TXT for conditions of usage


resourcePatterns=['.png', '.ico', '.xrc']
filePatterns=['.png', '.ico', '.xrc', '.py']
ignoredirs=['xrced', 'build', 'dist']


requiredMods=['wx.lib.ogl', 'xml']
appEntry='admin4.py'
packages=['wx']
includes=[]
excludes=['lib2to3', 'hotshot', 'distutils', 'ctypes', 'unittest']
distDir="../admin4-release"
buildDir=".build"
appName="Admin4"

if __name__ == '__main__':
  import sys, os
  import platform
  import shutil
  import version
  
  platform=platform.system()
  
  if len(sys.argv) > 1 and sys.argv[1] in ['srcUpdate', 'py2exe', 'py2app']:
    installer=sys.argv[1]
  else:
    if platform == "Windows":
      installer='py2exe'
    else:
      if platform == "Darwin":
        installer='py2app'
      else:
        print "Platform %s not supported" % platform
        sys.exit(1)
    sys.argv.insert(1, installer)
      
    
  def cleanWxDir(dir):
    remainder=0
    for fn in os.listdir(dir):
      path=os.path.join(dir, fn)
      if os.path.isdir(path):
        r=cleanWxDir(path)
        if path.endswith(requiredDirs):
          remainder += 1
        else:
          if not r:
            shutil.rmtree(path)
        remainder += r
      elif path.endswith( ('.pyc', 'pyo')):
        os.unlink(path)
    return remainder
        
  def searchFiles(dir):
    lst=[]
    filenames=[]
    for fn in os.listdir(dir):
      if fn.startswith('.'):
        continue
      path=os.path.join(dir, fn)
      if os.path.isdir(path):
        lst.extend(searchFiles(path))
      else:
        ext=path[path.rfind('.'):].lower()
        if ext in filePatterns:
          filenames.append(path)
    
    if filenames:
      lst.append( (dir, filenames) )
    return lst

  def writeVersion():
    try: 
      import git, time
    except:
      print "\nWARNING: No GIT installed\n\n"
      return False
    git01=git.__version__.startswith("0.1")
    repo=git.Repo(os.path.dirname(os.path.abspath(sys.argv[0])))

    tags={}
    for t in repo.tags:
      tags[str(t.commit)] = t

    if git01:
      lastOriginCommit=repo.commits('origin/master', max_count=1)[0]
      lastCommit=repo.commits('master', max_count=1)[0]
    else:
      lastOriginCommit=repo.commit('origin/master')
      lastCommit=repo.commit('master')
    
    def findTag(c):
      if str(c) in tags:
        return tags[str(c)]
      if c.parents:
        for c in c.parents:
          tag=findTag(c)
          if tag:
            return tag
      return False
    tag=findTag(lastOriginCommit)
    if tag:
      f=open("__version.py", "w")
      f.write("# Automatically created by createBundle from GIT\n\n")
      f.write("version='%s'\n" % tag.name)
      if git01:
        f.write("tagDate='%s'\n" % time.strftime("%Y-%m-%d %H:%M:%S", tag.commit.committed_date))
        f.write("revDate='%s'\n" % time.strftime("%Y-%m-%d %H:%M:%S", lastOriginCommit.committed_date))
      else:
        f.write("tagDate='%s'\n" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(tag.commit.committed_date)))
        f.write("revDate='%s'\n" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(lastOriginCommit.committed_date)))
      if repo.is_dirty or str(lastCommit) != str(lastOriginCommit):
        f.write("revLocalChange=True\n")
      else:
        f.write("revLocalChange=False\n")
      if repo.is_dirty:
        f.write("revDirty=True\n")
      else:
        f.write("revDirty=False\n")
      f.close()
      
      return repo.is_dirty
        
    

  # Start of code
  if writeVersion():
    print "\nWARNING: Repository has uncommitted data\n\n"
  sys.skipSetupInit=True
  

  data_files=[]
  admResources=[]
  
  if installer == 'srcUpdate':
    resourcePatterns = filePatterns
    
  for fn in os.listdir("."):
    if fn.startswith('.') or fn in ignoredirs:
      continue
    if os.path.isdir(fn):
      if os.path.exists("%s/_requires.py" % fn):
        mod=__import__("%s._requires" % fn)
        try:
          requires=getattr(mod, "_requires")
          rq=requires.GetPrerequisites(True)
          if rq:
            if isinstance(rq, str):
              rq=rq.split(' ')
            requiredMods.extend(rq)
            packages.extend(rq)
        except:
          pass
        
      data_files.extend(searchFiles(fn))
    else:
      if fn.startswith('ctl_') and fn.endswith('.py'):
        admResources.append(fn)
      else:
        ext=fn[fn.rfind('.'):].lower()
        if ext in resourcePatterns:
          admResources.append(fn)
  
  data_files.append( (".", admResources) )
  data_files.reverse()
  requiredDirs = tuple(d.replace('.', '/') for d in requiredMods)
  packages.extend(requiredMods)
  packages=sorted(set(packages))

  print "Required:", ", ".join(packages)
  
  if installer == 'srcUpdate':
    distDir='dist'
    print "Collecting update into %s" %distDir
    try:
      shutil.rmtree(distDir)
      os.mkdir(distDir)
    except:
      pass
    try:
      os.mkdir(distDir)
    except:
      pass
    for d in data_files:
      if d[0] == '.':
        destDir = distDir
      else:
        destDir=os.path.join(distDir, d[0])
        os.mkdir(destDir)
      for file in d[1]:
        shutil.copy2(file, destDir)
    
  else:
    import distutils.core
    __import__(installer)
    info=dict( data_files=data_files,
                         name=appName,
                         author=version.author,
                         license=version.copyright,
                         version=version.version,
                         options={'py2exe': {'packages': packages,
                                             'includes': includes,
                                             'excludes': excludes,
                                             'dist_dir': distDir
                                             },
                                            
                                  'py2app': {'argv_emulation': False,
                                             'packages': packages,
                                             'includes': includes,
                                             'iconfile': '%s.icns' % appName,
                                             'dist_dir': distDir,
                                             'plist': { 'CFBundleIdentifier': 'org.%s' % appName.lower() }
                                             },
                                  'build': {'build_base': buildDir},
                                  }
                         )
  
    if platform == "Windows":
      distutils.core.setup(windows=[{'script': appEntry, 'icon_resources': [(1, '%s.ico' % appName)] }], **info)
    elif platform == "Darwin":
      distutils.core.setup(app=[appEntry], **info)
      libdir='%s/%s.app/Contents/Resources/lib/python2.7/wx' % (distDir, appName)
      if not '-A' in sys.argv:
        cleanWxDir(libdir)
        shutil.rmtree('%s/%s.app/Contents/Resources/mpl-data' % (distDir, appName))
  print "done."
