#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
ponysay.py - Ponysay, cowsay reimplementation for ponies
Copyright (C) 2012  Erkin Batu Altunbaş et al.

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.


Authors of ponysay.py:

         Erkin Batu Altunbaş:              Project leader, helped write the first implementation
         Mattias "maandree" Andrée:        Major contributor of both implementions
         Elis "etu" Axelsson:              Major contributor of current implemention and patcher of the first implementation
         Sven-Hendrik "svenstaro" Haase:   Major contributor of the first implementation
         Jan Alexander "heftig" Steffens:  Major contributor of the first implementation
         Kyah "L-four" Rindlisbacher:      Patched the first implementation

'''

import os
import shutil
import sys
import random
from subprocess import Popen, PIPE



'''
The version of ponysay
'''
VERSION = 'dev'  # this line should not be edited, it is fixed by the build system



'''
Hack to enforce UTF-8 in output (in the future, if you see anypony not using utf-8 in programs by default, report them to Princess Celestia so she can banish them to the moon)
'''
def print(text = '', end = '\n'):
    sys.stdout.buffer.write((str(text) + end).encode('utf-8'))


'''
Checks whether a text ends with a specific text, but has more
'''
def endswith(text, ending):
    return text.endswith(ending) and not (text == ending);



'''
This is the mane class of ponysay
'''
class Ponysay():
    '''
    Starts the part of the program the arguments indicate
    '''
    def __init__(self, args):
        if (args.argcount == 0) and not pipelinein:
            args.help()
            return
        
        if   args.opts['-h']        is not None:  args.help()
        elif args.opts['--quoters'] is not None:  self.quoters()
        elif args.opts['--onelist'] is not None:  self.onelist()
        elif args.opts['-v']        is not None:  self.version()
        elif args.opts['-l']        is not None:  self.list()
        elif args.opts['-L']        is not None:  self.linklist()
        elif args.opts['-B']        is not None:  self.balloonlist()
        elif args.opts['++onelist'] is not None:  self.__extraponies(); self.onelist()
        elif args.opts['+l']        is not None:  self.__extraponies(); self.list()
        elif args.opts['+L']        is not None:  self.__extraponies(); self.linklist()
        elif args.opts['-A']        is not None:  self.list(); self.__extraponies(); self.list()
        elif args.opts['+A']        is not None:  self.linklist(); self.__extraponies(); self.linklist()
        else:
            self.__extraponies(args)
            self.__bestpony(args)
            self.__ucsremap(args)
            if args.opts['-q'] is not None:  self.quote(args)
            else:                            self.print_pony(args)
    
    
    ##
    ## Methods that run before the mane methods
    ##
    
    '''
    Use extra ponies
    '''
    def __extraponies(self, args = None):
        ## If extraponies are used, change ponydir to extraponydir
        if args is None:
            ponydirs[:] = extraponydirs
        elif args.opts['-F'] is not None:
            args.opts['-f'] = args.opts['-F']
            ponydirs[:] = extraponydirs
    
    
    '''
    Use best.pony if nothing else is set
    '''
    def __bestpony(self, args):
        ## Set best.pony as the pony to display if none is selected
        if (args.opts['-f'] is None) or (args.opts['-q'] is None) or (len(args.opts['-q']) == 0):
            for ponydir in ponydirs:
                if os.path.isfile(ponydir + 'best.pony') or os.path.islink(ponydir + 'best.pony'):
                    pony = os.path.realpath(ponydir + 'best.pony') # Canonical path
                    args.opts['-f' if args.opts['-q'] is None else '-q'] = [pony]
                    break
    
    
    '''
    Apply pony name remapping to args according to UCS settings
    '''
    def __ucsremap(self, args):
        ## Read UCS configurations
        env_ucs = os.environ['PONYSAY_UCS_ME'] if 'PONYSAY_UCS_ME' in os.environ else ''
        ucs_conf = 0
        if   env_ucs in ('yes',    'y', '1'):  ucs_conf = 1
        elif env_ucs in ('harder', 'h', '2'):  ucs_conf = 2
        
        ## Stop USC is not used
        if ucs_conf == 0:
            return
        
        ## Read all lines in all UCS → ASCII map files
        maplines = []
        for ucsmap in ucsmaps:
            if os.path.isfile(ucsmap):
                with open(ucsmap, 'rb') as mapfile:
                    maplines += [line.replace('\n', '') for line in mapfile.read().decode('utf8', 'replace').split('\n')]
        
        ## Create USC → ASCII mapping from read lines
        map = {}
        stripset = ' \t' # must be string, wtf! and way doesn't python's doc say so
        for line in maplines:
            if (len(line) > 0) and not (line[0] == '#'):
                s = line.index('→')
                ucs   = line[:s]    .strip(stripset)
                ascii = line[s + 1:].strip(stripset)
                map[ucs] = ascii
        
        ## Apply USC → ASCII mapping to -f and -q arguments
        for flag in ('-f', '-q'):
            if args.opts[flag] is not None:
                for i in range(0, len(args.opts[flag])):
                    if args.opts[flag][i] in map:
                        args.opts[flag][i] = map[args.opts[flag][i]]
    
    
    ##
    ## Auxiliary methods
    ##
    
    '''
    Apply USC:ise pony names according to UCS settings
    '''
    def __ucsise(self, ponies, links = None):
        ## Read UCS configurations
        env_ucs = os.environ['PONYSAY_UCS_ME'] if 'PONYSAY_UCS_ME' in os.environ else ''
        ucs_conf = 0
        if   env_ucs in ('yes',    'y', '1'):  ucs_conf = 1
        elif env_ucs in ('harder', 'h', '2'):  ucs_conf = 2
        
        ## Stop USC is not used
        if ucs_conf == 0:
            return
        
        ## Read all lines in all UCS → ASCII map files
        maplines = []
        for ucsmap in ucsmaps:
            if os.path.isfile(ucsmap):
                with open(ucsmap, 'rb') as mapfile:
                    maplines += [line.replace('\n', '') for line in mapfile.read().decode('utf8', 'replace').split('\n')]
        
        ## Create USC → ASCII mapping from read lines
        map = {}
        stripset = ' \t' # must be string, wtf! and way doesn't python's doc say so
        for line in maplines:
            if not line.startswith('#'):
                s = line.index('→')
                ucs   = line[:s]    .strip(stripset)
                ascii = line[s + 1:].strip(stripset)
                map[ascii] = ucs
        
        ## Apply USC → ACII mapping to ponies, by alias if weak settings
        if ucs_conf == 1:
            for pony in ponies:
                if pony in map:
                    ponies.append(map[pony])
                    if links is not None:
                        links[map[pony]] = pony
        else:
            for j in range(0, len(ponies)):
                if ponies[j] in map:
                    ponies[j] = map[ponies[j]]
    
    
    '''
    Returns one file with full path, names is filter for names, also accepts filepaths
    '''
    def __getponypath(self, names = None):
        ponies = {}
        
        ## List all pony files, without the .pony ending
        for ponydir in ponydirs:
            for ponyfile in os.listdir(ponydir):
                pony = ponyfile[:-5]
                if pony not in ponies:
                    ponies[pony] = ponydir + ponyfile
        
        ## Support for explicit pony file names
        if not names == None:
            for name in names:
                if os.path.exists(name):
                    ponies[name] = name
        
        ## If there is not select ponies, choose all of them
        if names == None:
            names = list(ponies.keys())
        
        ## Select a random pony of the choosen onles
        pony = names[random.randrange(0, len(names))]
        if pony not in ponies:
            sys.stderr.write('I have never heard of anypony named %s\n' % (pony));
            exit(1)
        else:
            return ponies[pony]
    
    
    '''
    Returns a set with all ponies that have quotes and are displayable
    '''
    def __quoters(self):
        ## List all unique quote files
        quotes = []
        quoteshash = set()
        _quotes = []
        for quotedir in quotedirs:
            _quotes += [item[:item.index('.')] for item in os.listdir(quotedir)]
        for quote in _quotes:
            if not quote == '':
                if not quote in quoteshash:
                    quoteshash.add(quote)
                    quotes.append(quote)
        
        ## Create a set of all ponyes that have quotes
        ponies = set()
        for ponydir in ponydirs:
            for pony in os.listdir(ponydir):
                if not pony[0] == '.':
                    p = pony[:-5] # remove .pony
                    for quote in quotes:
                        if ('+' + p + '+') in ('+' + quote + '+'):
                            if not p in ponies:
                                ponies.add(p)
        
        return ponies
    
    
    '''
    Returns a list with all (pony, quote file) pairs
    '''
    def __quotes(self):
        ## Get all ponyquote files
        quotes = []
        for quotedir in quotedirs:
            quotes += [quotedir + item for item in os.listdir(quotedir)]
        
        ## Create list of all pony–quote file-pairs
        rc = []
        for ponydir in ponydirs:
            for pony in os.listdir(ponydir):
                if not pony[0] == '.':
                    p = pony[:-5] # remove .pony
                    for quote in quotes:
                        q = quote[quote.rindex('/') + 1:]
                        q = q[:q.rindex('.')]
                        if ('+' + p + '+') in ('+' + q + '+'):
                            rc.append((p, quote))
        
        return rc
    
    
    '''
    Gets the size of the terminal in (rows, columns)
    '''
    def __gettermsize(self):
        ## Call `stty` to determine the size of the terminal, this way is better then using python's ncurses
        termsize = Popen(['stty', 'size'], stdout=PIPE, stdin=sys.stderr).communicate()[0]
        termsize = termsize.decode('utf8', 'replace')[:-1].split(' ') # [:-1] removes a \n
        termsize = [int(item) for item in termsize]
        return termsize
    
    
    
    ##
    ## Listing methods
    ##
    
    '''
    Columnise a list and prints it
    '''
    def __columnise(self, ponies):
        ## Get terminal width, and a 2 which is the space between columns
        termwidth = self.__gettermsize()[1] + 2
        ## Sort the ponies, and get the cells' widths, and the largest width + 2
        ponies.sort(key = lambda pony : pony[0])
        widths = [UCS.dispLen(pony[0]) for pony in ponies]
        width = max(widths) + 2 # longest pony file name + space between columns
        
        ## Calculate the number of rows and columns, can create a list of empty columns
        cols = termwidth // width # do not believe electricians, this means ⌊termwidth / width⌋
        rows = (len(ponies) + cols - 1) // cols
        columns = []
        for c in range(0, cols):  columns.append([])
        
        ## Fill the columns with cells of ponies
        (y, x) = (0, 0)
        for j in range(0, len(ponies)):
            cell = ponies[j][1] + ' ' * (width - widths[j]);
            columns[x].append(cell)
            y += 1
            if y == rows:
                x += 1
                y = 0
        
        ## Make the columnisation nicer by letting the last row be partially empty rather than the last column
        diff = rows * cols - len(ponies)
        if diff > 2:
            c = cols - 1
            diff -= 1
            while diff > 0:
                columns[c] = columns[c - 1][-diff:] + columns[c]
                c -= 1
                columns[c] = columns[c][:-diff]
                diff -= 1
                pass
        
        ## Create rows from columns
        lines = []
        for r in range(0, rows):
             lines.append([])
             for c in range(0, cols):
                 if r < len(columns[c]):
                     line = lines[r].append(columns[c][r])
        
        ## Print the matrix, with one extra blank row
        print('\n'.join([''.join(line)[:-2] for line in lines]))
        print()
    
    
    '''
    Lists the available ponies
    '''
    def list(self):
        ## Get all quoters
        quoters = self.__quoters()
        
        for ponydir in ponydirs: # Loop ponydirs
            ## Get all ponies in the directory
            _ponies = os.listdir(ponydir)
            
            ## Remove .pony from all files and skip those that does not have .pony
            ponies = []
            for pony in _ponies:
                if endswith(pony, '.pony'):
                    ponies.append(pony[:-5])
            
            ## UCS:ise pony names, they are already sorted
            self.__ucsise(ponies)
            
            ## If ther directory is not empty print its name and all ponies, columnised
            if len(ponies) == 0:
                continue
            print('\033[1mponies located in ' + ponydir + '\033[21m')
            self.__columnise([(pony, '\033[1m' + pony + '\033[21m' if pony in quoters else pony) for pony in ponies])
    
    
    '''
    Lists the available ponies with alternatives inside brackets
    '''
    def linklist(self):
        ## Get the size of the terminal and all ponies with quotes
        termsize = self.__gettermsize()
        quoters = self.__quoters()
        
        for ponydir in ponydirs: # Loop ponydirs
            ## Get all pony files in the directory
            _ponies = os.listdir(ponydir)
            
            ## Remove .pony from all files and skip those that does not have .pony
            ponies = []
            for pony in _ponies:
                if endswith(pony, '.pony'):
                    ponies.append(pony[:-5])
            
            ## If there are no ponies in the directory skip to next directory, otherwise, print the directories name
            if len(ponies) == 0:
                continue
            print('\033[1mponies located in ' + ponydir + '\033[21m')
            
            ## UCS:ise pony names
            pseudolinkmap = {}
            self.__ucsise(ponies, pseudolinkmap)
            
            ## Create target–link-pair, with `None` as link if the file is not a symlink or in `pseudolinkmap`
            pairs = []
            for pony in ponies:
                if pony in pseudolinkmap:
                    pairs.append((pony, pseudolinkmap[pony] + '.pony'));
                else:
                    pairs.append((pony, os.path.realpath(ponydir + pony + '.pony') if os.path.islink(ponydir + pony + '.pony') else None))
            
            ## Create map from source pony to alias ponies for each pony
            ponymap = {}
            for pair in pairs:
                if (pair[1] is None) or (pair[1] == ''):
                    if pair[0] not in ponymap:
                        ponymap[pair[0]] = []
                else:
                    target = pair[1][:-5]
                    if '/' in target:
                        target = target[target.rindex('/') + 1:]
                    if target in ponymap:
                        ponymap[target].append(pair[0])
                    else:
                        ponymap[target] = [pair[0]]
            
            ## Create list of source ponies concatenated with alias ponies in brackets
            ponies = {}
            for pony in ponymap:
                w = UCS.dispLen(pony)
                item = '\033[1m' + pony + '\033[21m' if (pony in quoters) else pony
                syms = ponymap[pony]
                syms.sort()
                if len(syms) > 0:
                    w += 2 + len(syms)
                    item += ' ('
                    first = True
                    for sym in syms:
                        w += UCS.dispLen(sym)
                        if first:  first = False
                        else:      item += ' '
                        item += '\033[1m' + sym + '\033[21m' if (sym in quoters) else sym
                    item += ')'
                ponies[(item.replace('\033[1m', '').replace('\033[21m', ''), item)] = w
            
            ## Print the ponies, columnised
            self.__columnise(list(ponies))
    
    
    '''
    Lists with all ponies that have quotes and are displayable, on one column without anything bold or otherwise formated
    '''
    def quoters(self):
        ## Get all quoters
        ponies = self.__quoters()
        
        ## USC:ise and sort
        self.__ucsise(ponies)
        ponies.sort()
        
        ## Print each one on a seperate line, but skip duplicates
        last = ''
        for pony in ponies:
            if not pony == last:
                last = pony
                print(pony)
    
    
    '''
    Lists the available ponies on one column without anything bold or otherwise formated
    '''
    def onelist(self):
        ## Get all pony files
        _ponies = []
        for ponydir in ponydirs: # Loop ponydirs
            _ponies += os.listdir(ponydir)
        
        ## Remove .pony from all files and skip those that does not have .pony
        ponies = []
        for pony in _ponies:
            if endswith(pony, '.pony'):
                ponies.append(pony[:-5])
        
        ## USC:ise and sort
        self.__ucsise(ponies)
        ponies.sort()
        
        ## Print each one on a seperate line, but skip duplicates
        last = ''
        for pony in ponies:
            if not pony == last:
                last = pony
                print(pony)
    
    
    
    ##
    ## Balloon methods
    ##
    
    '''
    Prints a list of all balloons
    '''
    def balloonlist(self):
        ## Get the size of the terminal
        termsize = self.__gettermsize()
        
        ## Get all balloons
        balloonset = set()
        for balloondir in balloondirs:
            for balloon in os.listdir(balloondir):
                ## Use .think if running ponythink, otherwise .say
                if isthink and endswith(balloon, '.think'):
                    balloon = balloon[:-6]
                elif (not isthink) and endswith(balloon, '.say'):
                    balloon = balloon[:-4]
                else:
                    continue
                
                ## Add the balloon if there is none with the same name
                if balloon not in balloonset:
                    balloonset.add(balloon)
        
        ## Print all balloos, columnised
        self.__columnise([(balloon, balloon) for balloon in list(balloonset)])
    
    
    '''
    Returns one file with full path, names is filter for style names, also accepts filepaths
    '''
    def __getballoonpath(self, names):
        ## Stop if their is no choosen balloon
        if names is None:
            return None
        
        ## Get all balloons
        balloons = {}
        for balloondir in balloondirs:
            for balloon in os.listdir(balloondir):
                balloonfile = balloon
                ## Use .think if running ponythink, otherwise .say
                if isthink and endswith(balloon, '.think'):
                    balloon = balloon[:-6]
                elif (not isthink) and endswith(balloon, '.say'):
                    balloon = balloon[:-4]
                else:
                    continue
                
                ## Add the balloon if there is none with the same name
                if balloon not in balloons:
                    balloons[balloon] = balloondir + balloonfile
        
        ## Support for explicit balloon file names
        for name in names:
            if os.path.exists(name):
                balloons[name] = name
        
        ## Select a random balloon of the choosen ones
        balloon = names[random.randrange(0, len(names))]
        if balloon not in balloons:
            sys.stderr.write('That balloon style %s does not exist\n' % (balloon));
            exit(1)
        else:
            return balloons[balloon]
    
    
    '''
    Creates the balloon style object
    '''
    def __getballoon(self, balloonfile):
        ## Use default balloon if none is specified
        if balloonfile is None:
            if isthink:
                return Balloon('o', 'o', '( ', ' )', [' _'], ['_'], ['_'], ['_'], ['_ '], ' )', ' )', ' )', ['- '], ['-'], ['-'], ['-'], [' -'], '( ', '( ', '( ')
            return Balloon('\\', '/', '< ', ' >', [' _'], ['_'], ['_'], ['_'], ['_ '], ' \\', ' |', ' /', ['- '], ['-'], ['-'], ['-'], [' -'], '\\ ', '| ', '/ ')
        
        ## Initialise map for balloon parts
        map = {}
        for elem in ('\\', '/', 'ww', 'ee', 'nw', 'nnw', 'n', 'nne', 'ne', 'nee', 'e', 'see', 'se', 'sse', 's', 'ssw', 'sw', 'sww', 'w', 'nww'):
            map[elem] = []
        
        ## Read all lines in the balloon file
        with open(balloonfile, 'rb') as balloonstream:
            data = [line.replace('\n', '') for line in balloonstream.read().decode('utf8', 'replace').split('\n')]
        
        ## Parse the balloon file, and fill the map
        last = None
        for line in data:
            if len(line) > 0:
                if line[0] == ':':
                    map[last].append(line[1:])
                else:
                    last = line[:line.index(':')]
                    value = line[len(last) + 1:]
                    map[last].append(value)
        
        ## Return the balloon
        return Balloon(map['\\'][0], map['/'][0], map['ww'][0], map['ee'][0], map['nw'], map['nnw'], map['n'],
                       map['nne'], map['ne'], map['nee'][0], map['e'][0], map['see'][0], map['se'], map['sse'],
                       map['s'], map['ssw'], map['sw'], map['sww'][0], map['w'][0], map['nww'][0])
    
    
    
    ##
    ## Displaying methods
    ##
    
    '''
    Prints the name of the program and the version of the program
    '''
    def version(self):
        ## Prints the "ponysay $VERSION", if this is modified, ./dev/dist.sh must be modified accordingly
        print('%s %s' % ('ponysay', VERSION))
    
    
    '''
    Print the pony with a speech or though bubble. message, pony and wrap from args are used.
    '''
    def print_pony(self, args):
        ## Get message and remove tailing whitespace from stdin (but not for each line)
        if args.message == None:
            msg = ''.join(sys.stdin.readlines()).rstrip()
        else:
            msg = args.message
        
        ## This algorithm should give some result as cowsay's (according to tests)
        if args.opts['-c'] is not None:
            buf = ''
            last = ' '
            CHARS = '\t \n'
            for c in msg:
                if (c in CHARS) and (last in CHARS):
                    if last == '\n':
                        buf += last
                    last = c
                else:
                    buf += c
                    last = c
            msg = buf.strip(CHARS)
            buf = ''
            for c in msg:
                if (c != '\n') or (last != '\n'):
                    buf += c
                    last = c
            msg = buf.replace('\n', '\n\n')
        
        ## Get the pony
        pony = self.__getponypath(args.opts['-f'])
        
        ## Use PNG file as pony file
        if endswith(pony.lower(), '.png'):
            pony = '\'' + pony.replace('\'', '\'\\\'\'') + '\''
            pngcmd = ('img2ponysay -p -- ' if linuxvt else 'img2ponysay -- ') + pony
            pngpipe = os.pipe()
            Popen(pngcmd, stdout=os.fdopen(pngpipe[1], 'w'), shell=True).wait()
            pony = '/proc/' + str(os.getpid()) + '/fd/' + str(pngpipe[0])
        
        ## If KMS is utilies, select a KMS pony file and create it if necessary
        pony = self.__kms(pony)
        
        ## If in Linux VT clean the terminal (See info/pdf-manual [Printing in TTY with KMS])
        if linuxvt:
            print('\033[H\033[2J', end='')
        
        ## Width Get truncation and wrapping
        env_width = os.environ['PONYSAY_FULL_WIDTH'] if 'PONYSAY_FULL_WIDTH' in os.environ else None
        if env_width is None:  env_width = ''
        widthtruncation = self.__gettermsize()[1] if env_width not in ('yes', 'y', '1') else None
        messagewrap = int(args.opts['-W'][0]) if args.opts['-W'] is not None else None
        
        ## Get balloon object
        balloon = self.__getballoon(self.__getballoonpath(args.opts['-b']))
        
        ## Run cowsay replacement
        backend = Backend(message = msg, ponyfile = pony, wrapcolumn = messagewrap if messagewrap is not None else 40, width = widthtruncation, balloon = balloon)
        backend.parse()
        output = backend.output
        if output.endswith('\n'):
            output = output[:-1]
        
        
        ## Load height trunction settings
        env_bottom = os.environ['PONYSAY_BOTTOM'] if 'PONYSAY_BOTTOM' in os.environ else None
        if env_bottom is None:  env_bottom = ''
        
        env_height = os.environ['PONYSAY_TRUNCATE_HEIGHT'] if 'PONYSAY_TRUNCATE_HEIGHT' in os.environ else None
        if env_height is None:  env_height = ''
        
        env_lines = os.environ['PONYSAY_SHELL_LINES'] if 'PONYSAY_SHELL_LINES' in os.environ else None
        if (env_lines is None) or (env_lines == ''):  env_lines = '2'
        
        ## Print the output, truncated on height is so set
        lines = self.__gettermsize()[0] - int(env_lines)
        if linuxvt or (env_height is ('yes', 'y', '1')):
            if env_bottom is ('yes', 'y', '1'):
                for line in output.split('\n')[: -lines]:
                    print(line)
            else:
                for line in output.split('\n')[: lines]:
                    print(line)
        else:
            print(output)
    
    
    '''
    Print the pony with a speech or though bubble and a self quote
    '''
    def quote(self, args):
        ## Get all quotes, and if any pony is choosen just keep them
        pairs = self.__quotes()
        if len(args.opts['-q']) > 0:
            ponyset = {}
            for pony in args.opts['-q']:
                if endswith(pony, '.pony'):
                    ponyname = pony[:-5]
                    if '/' in ponyname:
                        ponyname = ponyname[ponyname.rindex('/') + 1:]
                    ponyset[ponyname] = pony
                else:
                    ponyset[pony] = pony
            alts = []
            for pair in pairs:
                if pair[0] in ponyset:
                    alts.append((ponyset[pair[0]], pair[1]))
            pairs = alts
        
        ## Select a random pony–quote-pair, load it and print it
        if not len(pairs) == 0:
            pair = pairs[random.randrange(0, len(pairs))]
            with open(pair[1], 'rb') as qfile:
                args.message = qfile.read().decode('utf8', 'replace').strip()
            args.opts['-f'] = [pair[0]]
        elif len(args.opts['-q']) == 0:
            sys.stderr.write('Princess Celestia! All the ponies are mute!\n')
            exit(1)
        else:
            args.opts['-f'] = [args.opts['-q'][random.randrange(0, len(args.opts['-q']))]]
            args.message = 'Zecora! Help me, I am mute!'
        
        self.print_pony(args)
    
    
    '''
    Identifies whether KMS support is utilised
    '''
    @staticmethod
    def isUsingKMS():
        ## KMS is not utilised if Linux VT is not used
        if not linuxvt:
            return False
        
        ## Read the PONYSAY_KMS_PALETTE environment variable
        env_kms = os.environ['PONYSAY_KMS_PALETTE'] if 'PONYSAY_KMS_PALETTE' in os.environ else None
        if env_kms is None:  env_kms = ''
        
        ## Read the PONYSAY_KMS_PALETTE_CMD environment variable, and run it
        env_kms_cmd = os.environ['PONYSAY_KMS_PALETTE_CMD'] if 'PONYSAY_KMS_PALETTE_CMD' in os.environ else None
        if (env_kms_cmd is not None) and (not env_kms_cmd == ''):
            env_kms = Popen(shlex.split(env_kms_cmd), stdout=PIPE, stdin=sys.stderr).communicate()[0].decode('utf8', 'replace')
            if env_kms[-1] == '\n':
                env_kms = env_kms[:-1]
        
        ## If the palette string is empty KMS is not utilised
        return env_kms != ''
    
    
    '''
    Returns the file name of the input pony converted to a KMS pony, or if KMS is not used, the input pony itself
    '''
    def __kms(self, pony):
        ## If not in Linux VT, return the pony as is
        if not linuxvt:
            return pony
        
        ## KMS support version constant
        KMS_VERSION = '1'
        
        ## Read the PONYSAY_KMS_PALETTE environment variable
        env_kms = os.environ['PONYSAY_KMS_PALETTE'] if 'PONYSAY_KMS_PALETTE' in os.environ else None
        if env_kms is None:  env_kms = ''
        
        ## Read the PONYSAY_KMS_PALETTE_CMD environment variable, and run it
        env_kms_cmd = os.environ['PONYSAY_KMS_PALETTE_CMD'] if 'PONYSAY_KMS_PALETTE_CMD' in os.environ else None
        if (env_kms_cmd is not None) and (not env_kms_cmd == ''):
            env_kms = Popen(shlex.split(env_kms_cmd), stdout=PIPE, stdin=sys.stderr).communicate()[0].decode('utf8', 'replace')
            if env_kms[-1] == '\n':
                env_kms = env_kms[:-1]
        
        ## If not using KMS, return the pony as is
        if env_kms == '':
            return pony
        
        ## Store palette string and a clong with just the essentials
        palette = env_kms
        palettefile = env_kms.replace('\033]P', '')
        
        ## Get and in necessary make cache directory
        cachedir = '/var/cache/ponysay'
        shared = True
        if not os.path.isdir(cachedir):
            cachedir = HOME + '/.cache/ponysay'
            shared = False
            if not os.path.isdir(cachedir):
                os.makedirs(cachedir)
        _cachedir = '\'' + cachedir.replace('\'', '\'\\\'\'') + '\''
        
        ## KMS support version control, clean everything if not matching
        newversion = False
        if not os.path.isfile(cachedir + '/.version'):
            newversion = True
        else:
            with open(cachedir + '/.version', 'rb') as cachev:
                if cachev.read().decode('utf8', 'replace').replace('\n', '') != KMS_VERSION:
                    newversion = True
        if newversion:
            for cached in os.listdir(cachedir):
                cached = cachedir + '/' + cached
                if os.path.isdir(cached) and not os.path.islink(cached):
                    shutil.rmtree(cached, False)
                else:
                    os.remove(cached)
            with open(cachedir + '/.version', 'w+') as cachev:
                cachev.write(KMS_VERSION)
                if shared:
                    Popen('chmod 666 -- ' + _cachedir + '/.version', shell=True).wait()
        
        ## Get kmspony directory and kmspony file
        kmsponies = cachedir + '/kmsponies/' + palettefile
        kmspony = (kmsponies + pony).replace('//', '/')
        
        ## If the kmspony is missing, create it
        if not os.path.isfile(kmspony):
            ## Protokmsponies are uncolourful ttyponies
            protokmsponies = cachedir + '/protokmsponies/'
            protokmspony = (protokmsponies + pony).replace('//', '/')
            protokmsponydir = protokmspony[:protokmspony.rindex('/')]
            kmsponydir      =      kmspony[:     kmspony.rindex('/')]
            
            ## Change file names to be shell friendly
            _protokmspony = '\'' + protokmspony.replace('\'', '\'\\\'\'') + '\''
            _kmspony      = '\'' +      kmspony.replace('\'', '\'\\\'\'') + '\''
            _pony         = '\'' +         pony.replace('\'', '\'\\\'\'') + '\''
            
            ## Create protokmspony is missing
            if not os.path.isfile(protokmspony):
                if not os.path.isdir(protokmsponydir):
                    os.makedirs(protokmsponydir)
                    if shared:
                        Popen('chmod -R 6777 -- ' + _cachedir, shell=True).wait()
                if not os.system('ponysay2ttyponysay < ' + _pony + ' > ' + _protokmspony) == 0:
                    sys.stderr.write('Unable to run ponysay2ttyponysay successfully, you need util-say for KMS support\n')
                    exit(1)
                if shared:
                    Popen('chmod 666 -- ' + _protokmspony, shell=True).wait()
            
            ## Create kmspony
            if not os.path.isdir(kmsponydir):
                os.makedirs(kmsponydir)
                if shared:
                    Popen('chmod -R 6777 -- ' + _cachedir, shell=True).wait()
            if not os.system('tty2colourfultty -p ' + palette + ' < ' + _protokmspony + ' > ' + _kmspony) == 0:
                sys.stderr.write('Unable to run tty2colourfultty successfully, you need util-say for KMS support\n')
                exit(1)
            if shared:
                Popen('chmod 666 -- ' + _kmspony, shell=True).wait()
        
        return kmspony



ARGUMENTLESS = 0
ARGUMENTED = 1
VARIADIC = 2
'''
Simple argument parser
'''
class ArgParser():
    '''
    Constructor.
    The short description is printed on same line as the program name
    '''
    def __init__(self, program, description, usage, longdescription = None):
        self.__program = program
        self.__description = description
        self.__usage = usage
        self.__longdescription = longdescription
        self.__arguments = []
        self.opts = {}
        self.optmap = {}
    
    
    '''
    Add option that takes no arguments
    '''
    def add_argumentless(self, alternatives, help = None):
        ARGUMENTLESS
        self.__arguments.append((ARGUMENTLESS, alternatives, None, help))
        stdalt = alternatives[0]
        self.opts[stdalt] = None
        for alt in alternatives:
            self.optmap[alt] = (stdalt, ARGUMENTLESS)
    
    '''
    Add option that takes one argument
    '''
    def add_argumented(self, alternatives, arg, help = None):
        self.__arguments.append((ARGUMENTED, alternatives, arg, help))
        stdalt = alternatives[0]
        self.opts[stdalt] = None
        for alt in alternatives:
            self.optmap[alt] = (stdalt, ARGUMENTED)
    
    '''
    Add option that takes all following argument
    '''
    def add_variadic(self, alternatives, arg, help = None):
        self.__arguments.append((VARIADIC, alternatives, arg, help))
        stdalt = alternatives[0]
        self.opts[stdalt] = None
        for alt in alternatives:
            self.optmap[alt] = (stdalt, VARIADIC)
    
    
    '''
    Parse arguments
    '''
    def parse(self, argv = sys.argv):
        self.argcount = len(argv) - 1
        self.files = []
        
        argqueue = []
        optqueue = []
        deque = []
        for arg in argv[1:]:
            deque.append(arg)
        
        dashed = False
        tmpdashed = False
        get = 0
        dontget = 0
        
        def unrecognised(arg):
            sys.stderr.write('%s: warning: unrecognised option %s\n' % (self.__program, arg))
        
        while len(deque) != 0:
            arg = deque[0]
            deque = deque[1:]
            if (get > 0) and (dontget == 0):
                get -= 1
                argqueue.append(arg)
            elif tmpdashed:
                self.files.append(arg)
                tmpdashed = False
            elif dashed:        self.files.append(arg)
            elif arg == '++':   tmpdashed = True
            elif arg == '--':   dashed = True
            elif (len(arg) > 1) and (arg[0] in ('-', '+')):
                if (len(arg) > 2) and (arg[:2] in ('--', '++')):
                    if dontget > 0:
                        dontget -= 1
                    elif (arg in self.optmap) and (self.optmap[arg][1] == ARGUMENTLESS):
                        optqueue.append(arg)
                        argqueue.append(None)
                    elif '=' in arg:
                        arg_opt = arg[:arg.index('=')]
                        if (arg_opt in self.optmap) and (self.optmap[arg_opt][1] >= ARGUMENTED):
                            optqueue.append(arg_opt)
                            argqueue.append(arg[arg.index('=') + 1:])
                            if self.optmap[arg_opt][1] == VARIADIC:
                                dashed = True
                        else:
                            unrecognised(arg)
                    elif (arg in self.optmap) and (self.optmap[arg][1] == ARGUMENTED):
                        optqueue.append(arg)
                        get += 1
                    elif (arg in self.optmap) and (self.optmap[arg][1] == VARIADIC):
                        optqueue.append(arg)
                        argqueue.append(None)
                        dashed = True
                    else:
                        unrecognised(arg)
                else:
                    sign = arg[0]
                    i = 1
                    n = len(arg)
                    while i < n:
                        narg = sign + arg[i]
                        i += 1
                        if (narg in self.optmap):
                            if self.optmap[narg][1] == ARGUMENTLESS:
                                optqueue.append(narg)
                                argqueue.append(None)
                            elif self.optmap[narg][1] == ARGUMENTED:
                                optqueue.append(narg)
                                nargarg = arg[i:]
                                if len(nargarg) == 0:
                                    get += 1
                                else:
                                    argqueue.append(nargarg)
                                break
                            elif self.optmap[narg][1] == VARIADIC:
                                optqueue.append(narg)
                                nargarg = arg[i:]
                                argqueue.append(nargarg if len(nargarg) > 0 else None)
                                dashed = True
                                break
                        else:
                            unrecognised(arg)
            else:
                self.files.append(arg)
        
        i = 0
        n = len(optqueue)
        while i < n:
            opt = optqueue[i]
            arg = argqueue[i]
            i += 1
            opt = self.optmap[opt][0]
            if (opt not in self.opts) or (self.opts[opt] is None):
                self.opts[opt] = []
            self.opts[opt].append(arg)
        
        for arg in self.__arguments:
            if (arg[0] == VARIADIC):
                varopt = self.opts[arg[1][0]]
                if varopt is not None:
                    additional = ','.join(self.files).split(',') if len(self.files) > 0 else []
                    if varopt[0] is None:
                        self.opts[arg[1][0]] = additional
                    else:
                        self.opts[arg[1][0]] = varopt[0].split(',') + additional
                    self.files = []
                    break
        
        self.message = ' '.join(self.files) if len(self.files) > 0 else None
    
    
    '''
    Prints a colourful help message
    '''
    def help(self):
        print('\033[1m%s\033[21m %s %s' % (self.__program, '-' if linuxvt else '—', self.__description))
        print()
        if self.__longdescription is not None:
            print(self.__longdescription)
        print()
        
        print('\033[1mUSAGE:\033[21m', end='')
        first = True
        for line in self.__usage.split('\n'):
            if first:
                first = False
            else:
                print('    or', end='')
            print('\t%s' % (line))
        print()
        
        print('\033[1mSYNOPSIS:\033[21m')
        (lines, lens) = ([], [])
        for opt in self.__arguments:
            opt_type = opt[0]
            opt_alts = opt[1]
            opt_arg = opt[2]
            opt_help = opt[3]
            if opt_help is None:
                continue
            (line, l) = ('', 0)
            first = opt_alts[0]
            last = opt_alts[-1]
            alts = ('', last) if first is last else (first, last)
            for opt_alt in alts:
                if opt_alt is alts[-1]:
                    line += '%colour%' + opt_alt
                    l += len(opt_alt)
                    if   opt_type == ARGUMENTED:  line += ' \033[4m%s\033[24m'      % (opt_arg);  l += len(opt_arg) + 1
                    elif opt_type == VARIADIC:    line += ' [\033[4m%s\033[24m...]' % (opt_arg);  l += len(opt_arg) + 6
                else:
                    line += '    \033[2m%s\033[22m  ' % (opt_alt)
                    l += len(opt_alt) + 6
            lines.append(line)
            lens.append(l)
        
        col = max(lens)
        col += 8 - ((col - 4) & 7)
        index = 0
        for opt in self.__arguments:
            opt_help = opt[3]
            if opt_help is None:
                continue
            first = True
            colour = '36' if (index & 1) == 0 else '34'
            print(lines[index].replace('%colour%', '\033[%s;1m' % (colour)), end=' ' * (col - lens[index]))
            for line in opt_help.split('\n'):
                if first:
                    first = False
                    print('%s' % (line), end='\033[21;39m\n')
                else:
                    print('%s\033[%sm%s\033[39m' % (' ' * col, colour, line))
            index += 1
        
        print()



'''
Balloon format class
'''
class Balloon():
    '''
    Constructor
    '''
    def __init__(self, link, linkmirror, ww, ee, nw, nnw, n, nne, ne, nee, e, see, se, sse, s, ssw, sw, sww, w, nww):
        (self.link, self.linkmirror) = (link, linkmirror)
        (self.ww, self.ee) = (ww, ee)
        (self.nw, self.ne, self.se, self.sw) = (nw, ne, se, sw)
        (self.nnw, self.n, self.nne) = (nnw, n, nne)
        (self.nee, self.e, self.see) = (nee, e, see)
        (self.sse, self.s, self.ssw) = (sse, s, ssw)
        (self.sww, self.w, self.nww) = (sww, w, nww)
        
        _ne = max(ne, key = UCS.dispLen)
        _nw = max(nw, key = UCS.dispLen)
        _se = max(se, key = UCS.dispLen)
        _sw = max(sw, key = UCS.dispLen)
        
        minE = UCS.dispLen(max([_ne, nee, e, see, _se, ee], key = UCS.dispLen))
        minW = UCS.dispLen(max([_nw, nww, e, sww, _sw, ww], key = UCS.dispLen))
        minN = len(max([ne, nne, n, nnw, nw], key = len))
        minS = len(max([se, sse, s, ssw, sw], key = len))
        
        self.minwidth = minE + minE
        self.minheight = minN + minS
    
    
    '''
    Generates a balloon with a message
    '''
    def get(self, minw, minh, lines, lencalc):
        h = self.minheight + len(lines)
        w = self.minwidth + lencalc(max(lines, key = lencalc))
        if w < minw:  w = minw
        if h < minh:  h = minh
        
        if len(lines) > 1:
            (ws, es) = ({0 : self.nww, len(lines) - 1 : self.sww}, {0 : self.nee, len(lines) - 1 : self.see})
            for j in range(1, len(lines) - 1):
                ws[j] = self.w
                es[j] = self.e
        else:
            (ws, es) = ({0 : self.ww}, {0 : self.ee})
        
        rc = []
        
        for j in range(0, len(self.n)):
            outer = UCS.dispLen(self.nw[j]) + UCS.dispLen(self.ne[j])
            inner = UCS.dispLen(self.nnw[j]) + UCS.dispLen(self.nne[j])
            if outer + inner >= w:
                rc.append(self.nw[j] + self.nnw[j] + self.n[j] * (w - outer - inner) + self.nne[j] + self.ne[j])
            else:
                rc.append(self.nw[j] + self.n[j] * (w - outer) + self.ne[j])
        
        for j in range(0, len(lines)):
            rc.append(ws[j] + lines[j] + ' ' * (w - lencalc(lines[j]) - UCS.dispLen(self.w) - UCS.dispLen(self.e)) + es[j])
        
        for j in range(0, len(self.s)):
            outer = UCS.dispLen(self.sw[j]) + UCS.dispLen(self.se[j])
            inner = UCS.dispLen(self.ssw[j]) + UCS.dispLen(self.sse[j])
            if outer + inner >= w:
                rc.append(self.sw[j] + self.ssw[j] + self.s[j] * (w - outer - inner) + self.sse[j] + self.se[j])
            else:
                rc.append(self.sw[j] + self.s[j] * (w - outer) + self.se[j])
        
        return '\n'.join(rc)



'''
Replacement for cowsay
'''
class Backend():
    '''
    Constructor
    Takes message [string], ponyfile [filename string], wrapcolumn [None or an int], width [None or an int] and balloon [Balloon object]
    '''
    def __init__(self, message, ponyfile, wrapcolumn, width, balloon):
        self.message = message
        self.ponyfile = ponyfile
        self.wrapcolumn = wrapcolumn
        self.width = width
        self.balloon = balloon
        
        self.link = {'\\' : self.balloon.link, '/' : self.balloon.linkmirror}
        
        self.output = ''
        self.pony = None
    
    
    '''
    Process all data
    '''
    def parse(self):
        self.__expandMessage()
        self.__loadFile()
        self.__processPony()
        self.__truncate()
    
    
    '''
    Converts all tabs in the message to spaces by expanding
    '''
    def __expandMessage(self):
        lines = self.message.split('\n')
        buf = ''
        for line in lines:
            (i, n, x) = (0, len(line), 0)
            while i < n:
                c = line[i]
                i += 1
                if c == '\033':
                    colour = self.__getcolour(line, i - 1)
                    i += len(colour) - 1
                    buf += colour
                elif c == '\t':
                    nx = 8 - (x & 7)
                    buf += ' ' * nx
                    x += nx
                else:
                    buf += c
                    if not UCS.isCombining(c):
                        x += 1
            buf += '\n'
        self.message = buf[:-1]
    
    
    '''
    Loads the pony file
    '''
    def __loadFile(self):
        with open(self.ponyfile, 'rb') as ponystream:
            self.pony = ponystream.read().decode('utf8', 'replace')
    
    
    '''
    Truncate output to the width of the screen
    '''
    def __truncate(self):
        if self.width is None:
            return
        lines = self.output.split('\n')
        self.output = ''
        for line in lines:
            (i, n, x) = (0, len(line), 0)
            while i < n:
                c = line[i]
                i += 1
                if c == '\033':
                    colour = self.__getcolour(line, i - 1)
                    i += len(colour) - 1
                    self.output += colour
                else:
                    if x < self.width:
                        self.output += c
                        if not UCS.isCombining(c):
                            x += 1
            self.output += '\n'
        self.output = self.output[:-1]
    
    
    '''
    Process the pony file and generate output to self.output
    '''
    def __processPony(self):
        self.output = ''
        
        AUTO_PUSH = '\033[01010~'
        AUTO_POP  = '\033[10101~'
        
        variables = {'' : '$'}
        for key in self.link:
            variables[key] = AUTO_PUSH + self.link[key] + AUTO_POP
        
        indent = 0
        dollar = None
        balloonLines = None
        colourstack = ColourStack(AUTO_PUSH, AUTO_POP)
        
        (i, n, lineindex, skip, nonskip) = (0, len(self.pony), 0, 0, 0)
        while i < n:
            c = self.pony[i]
            if c == '\t':
                n += 8 - (indent & 7)
                ed = ' ' * (7 - (indent & 7))
                c = ' '
                self.pony = self.pony[:i] + ed + self.pony[i:]
            i += 1
            if c == '$':
                if dollar is not None:
                    if '=' in dollar:
                        name = dollar[:dollar.find('=')]
                        value = dollar[dollar.find('=') + 1:]
                        variables[name] = value
                    elif not dollar.startswith('balloon'):
                        data = variables[dollar].replace('$', '$$')
                        if data == '$$': # if not handled specially we will get an infinity loop
                            if (skip == 0) or (nonskip > 0):
                                if nonskip > 0:
                                    nonskip -= 1
                                self.output += '$'
                                indent += 1
                            else:
                                skip -= 1
                        else:
                            n += len(data)
                            self.pony = self.pony[:i] + data + self.pony[i:]
                    else:
                        (w, h) = (0, 0)
                        props = dollar[7:]
                        if len(props) > 0:
                            if ',' in props:
                                if props[0] is not ',':
                                    w = int(props[:props.index(',')])
                                h = int(props[props.index(',') + 1:])
                            else:
                                w = int(props)
                        balloon = self.__getballoon(w, h, indent)
                        balloon = balloon.split('\n')
                        for b in balloon[0]:
                            self.output += b + colourstack.feed(b)
                        if lineindex == 0:
                            balloonpre = '\n' + (' ' * indent)
                            for line in balloon[1:]:
                                self.output += balloonpre;
                                for b in line:
                                    self.output += b + colourstack.feed(b);
                            indent = 0
                        elif len(balloon) > 1:
                            balloonLines = balloon
                            balloonLine = 0
                            balloonIndent = indent
                            indent += self.__len(balloonLines[0])
                            balloonLines[0] = None
                    dollar = None
                else:
                    dollar = ''
            elif dollar is not None:
                if c == '\033':
                    c = self.pony[i]
                    i += 1
                dollar += c
            elif c == '\033':
                colour = self.__getcolour(self.pony, i - 1)
                for b in colour:
                    self.output += b + colourstack.feed(b);
                i += len(colour) - 1
            elif c == '\n':
                self.output += c
                indent = 0
                (skip, nonskip) = (0, 0)
                lineindex += 1
                if balloonLines is not None:
                    balloonLine += 1
                    if balloonLine == len(balloonLines):
                        balloonLines = None
            else:
                if (balloonLines is not None) and (balloonLines[balloonLine] is not None) and (balloonIndent == indent):
                    data = balloonLines[balloonLine]
                    datalen = self.__len(data)
                    skip += datalen
                    nonskip += datalen
                    data = data.replace('$', '$$')
                    n += len(data)
                    self.pony = self.pony[:i] + data + self.pony[i:]
                    balloonLines[balloonLine] = None
                else:
                    if (skip == 0) or (nonskip > 0):
                        if nonskip > 0:
                            nonskip -= 1
                        self.output += c + colourstack.feed(c);
                        if not UCS.isCombining(c):
                            indent += 1
                    else:
                        skip -= 1
        
        if balloonLines is not None:
            for line in balloonLines[balloonLine:]:
                data = ' ' * (balloonIndent - indent) + line + '\n'
                for b in data:
                    self.output += b + colourstack.feed(b);
                indent = 0
        
        self.output = self.output.replace(AUTO_PUSH, '').replace(AUTO_POP, '')
    
    
    '''
    Gets colour code att the currect offset in a buffer
    '''
    def __getcolour(self, input, offset):
        (i, n) = (offset, len(input))
        rc = input[i]
        i += 1
        if i == n: return rc
        c = input[i]
        i += 1
        rc += c
        
        if c == ']':
            if i == n: return rc
            c = input[i]
            i += 1
            rc += c
            if c == 'P':
                di = 0
                while (di < 7) and (i < n):
                    c = input[i]
                    i += 1
                    di += 1
                    rc += c
        elif c == '[':
            while i < n:
                c = input[i]
                i += 1
                rc += c
                if (c == '~') or (('a' <= c) and (c <= 'z')) or (('A' <= c) and (c <= 'Z')):
                    break
        
        return rc
    
    
    '''
    Calculates the number of visible characters in a text
    '''
    def __len(self, input):
        (rc, i, n) = (0, 0, len(input))
        while i < n:
            c = input[i]
            if c == '\033':
                i += len(self.__getcolour(input, i))
            else:
                i += 1
                if not UCS.isCombining(c):
                    rc += 1
        return rc
    
    
    '''
    Generates a balloon with the message
    '''
    def __getballoon(self, width, height, left):
        wrap = None
        if self.wrapcolumn is not None:
            wrap = self.wrapcolumn - left
            if wrap < 8:
                wrap = 8
        
        msg = self.message
        if wrap is not None:
            msg = self.__wrapMessage(msg, wrap)
        
        if '\033' in msg:
            AUTO_PUSH = '\033[01010~'
            AUTO_POP  = '\033[10101~'
            cstack = ColourStack(AUTO_PUSH, AUTO_POP)
            buf = ''
            for c in msg:
                if c == '\n':
                    for cc in ('%s\n%s' % (AUTO_PUSH, AUTO_POP)):
                        buf += cc
                        buf += cstack.feed(cc)
                else:
                    buf += c
                    buf += cstack.feed(c)
            msg = buf
        
        return self.balloon.get(width, height, msg.split('\n'), self.__len)
    
    
    '''
    Wraps the message
    '''
    def __wrapMessage(self, message, wrap):
        AUTO_PUSH = '\033[01010~'
        AUTO_POP  = '\033[10101~'
        lines = message.split('\n')
        buf = ''
        for line in lines:
            b = [None] * len(line)
            map = {}
            (bi, cols, w) = (0, 0, wrap)
            (indent, indentc) = (-1, 0)
            
            (i, n) = (0, len(line))
            while i <= n:
                d = None
                if i < n:
                    d = line[i]
                i += 1
                if d == '\033':  # TODO this should use self.__getcolour()
                    ## Invisible stuff
                    b[bi] = d
                    bi += 1
                    b[bi] = line[i]
                    d = line[i]
                    bi += 1
                    i += 1
                    if d == '[':
                        while True:
                            b[bi] = line[i]
                            d = line[i]
                            bi += 1
                            i += 1
                            if (('a' <= d) and (d <= 'z')) or (('A' <= d) and (d <= 'Z')) or (d == '~'):
                                break
                    elif d == ']':
                        b[bi] = line[i]
                        d = line[i]
                        bi += 1
                        i += 1
                        if d == 'P':
                            for j in range(0, 7):
                                b[bi] = line[i]
                                bi += 1
                                i += 1
                elif (d is not None) and (d != ' '):
                    ## Fetch word
                    if indent == -1:
                        indent = i - 1
                        for j in range(0, indent):
                            if line[j] == ' ':
                                indentc += 1
                    b[bi] = d
                    bi += 1
                    if (not UCS.isCombining(d)) and (d != '­'):
                        cols += 1
                    map[cols] = bi
                else:
                    ## Wrap?
                    mm = 0
                    bisub = 0
                    iwrap = wrap - (0 if indent == 1 else indentc)
                    
                    while ((w > 8) and (cols > w + 5)) or (cols > iwrap): # TODO make configurable
                        ## wrap
                        x = w;
                        nbsp = b[map[mm + x]] == ' '
                        m = map[mm + x]
                        
                        if ('­' in b[bisub : m]) and not nbsp:
                            hyphen = m - 1
                            while b[hyphen] != '­':
                                hyphen -= 1
                            while map[mm + x] > hyphen: ## Only looking backward, if foreward is required the word is probabily not hythenated correctly
                                x -= 1
                            x += 1
                            m = map[mm + x]
                        
                        mm += x - (0 if nbsp else 1) ## − 1 so we have space for a hythen
                        
                        for bb in b[bisub : m]:
                            buf += bb
                        buf += '\n' if nbsp else '\0\n'
                        cols -= x - (0 if nbsp else 1)
                        bisub = m
                        
                        w = iwrap
                        if indent != -1:
                            buf += line[:indent]
                    
                    for j in range(bisub, bi):
                        b[j - bisub] = b[j]
                    bi -= bisub
                    
                    if cols > w:
                        buf += '\n'
                        w = wrap
                        if indent != -1:
                            buf += line[:indent]
                            w -= indentc
                    for bb in b[:bi]:
                        buf += bb
                    w -= cols
                    cols = 0
                    bi = 0
                    if d is None:
                        i += 1
                    else:
                        if w > 0:
                            buf += ' '
                            w -= 1
                        else:
                            buf += '\n'
                            w = wrap
                            if indent != -1:
                                buf + line[:indent]
                                w -= indentc
            buf += '\n'
        
        rc = '\n'.join(line.rstrip() for line in buf[:-1].split('\n'));
        rc = rc.replace('­', ''); # remove soft hyphens
        rc = rc.replace('\0', '%s%s%s' % (AUTO_PUSH, '\033[31m-', AUTO_POP)) # TODO make configurable
        return rc


'''
ANSI colour stack
'''
class ColourStack():
    '''
    Constructor
    '''
    def __init__(self, autopush, autopop):
        self.autopush = autopush
        self.autopop  = autopop
        self.lenpush  = len(autopush)
        self.lenpop   = len(autopop)
        self.bufproto = ' ' * (self.lenpush if self.lenpush > self.lenpop else self.lenpop)
        self.stack    = []
        self.push()
        self.seq      = None
    
    
    def push(self):
        self.stack = [[self.bufproto, None, None, [False] * 9]] + self.stack
        if len(self.stack) == 1:
            return None
        return '\033[0m'
    
    
    def pop(self):
        old = self.stack[0]
        self.stack = self.stack[1:]
        rc = '\033[0;'
        new = self.stack[0]
        if new[1] is not None:  rc += new[1] + ';'
        if new[2] is not None:  rc += new[2] + ';'
        for i in range(0, 9):
            if new[3][i]:
                rc += str(i + 1) + ';'
        return rc[:-1] + 'm'
    
    
    def feed(self, char):
        if self.seq is not None:
            self.seq += char
            if (char == '~') or (('a' <= char) and (char <= 'z')) or (('A' <= char) and (char <= 'Z')):
                if (self.seq[0] == '[') and (self.seq[-1] == 'm'):
                    self.seq = self.seq[1:-1].split(';')
                    (i, n) = (0, len(self.seq))
                    while i < n:
                        part = self.seq[i]
                        p = 0 if part == '' else int(part)
                        i += 1
                        if p == 0:                       self.stack[0][1:] = [None, None, [False] * 9]
                        elif (1 <= p) and (p <= 9):      self.stack[0][3][p - 1] = True
                        elif (21 <= p) and (p <= 29):    self.stack[0][3][p - 21] = False
                        elif p == 39:                    self.stack[0][1] = None
                        elif p == 49:                    self.stack[0][2] = None
                        elif (30 <= p) and (p <= 37):    self.stack[0][1] = part
                        elif (90 <= p) and (p <= 97):    self.stack[0][1] = part
                        elif (40 <= p) and (p <= 47):    self.stack[0][2] = part
                        elif (100 <= p) and (p <= 107):  self.stack[0][2] = part
                        elif p == 38:
                            self.stack[0][1] = '%s;%s;%s' % (part, self.seq[i], self.seq[i + 1])
                            i += 2
                        elif p == 48:
                            self.stack[0][2] = '%s;%s;%s' % (part, self.seq[i], self.seq[i + 1])
                            i += 2
                self.seq = None
        elif char == '\033':
            self.seq = ''
        buf = self.stack[0][0]
        buf = buf[1:] + char
        rc = ''
        if   buf[-self.lenpush:] == self.autopush:  rc = self.push()
        elif buf[-self.lenpop:]  == self.autopop:   rc = self.pop()
        self.stack[0][0] = buf
        return rc



'''
UCS utility class
'''
class UCS():
    '''
    Checks whether a character is a combining character
    '''
    @staticmethod
    def isCombining(char):
        o = ord(char)
        if (0x0300 <= o) and (o <= 0x036F):  return True
        if (0x20D0 <= o) and (o <= 0x20FF):  return True
        if (0x1DC0 <= o) and (o <= 0x1DFF):  return True
        if (0xFE20 <= o) and (o <= 0xFE2F):  return True
        return False
    
    
    '''
    Gets the number of combining characters in a string
    '''
    @staticmethod
    def countCombining(string):
        rc = 0
        for char in string:
            if UCS.isCombining(char):
                rc += 1
        return rc
    
    
    '''
    Gets length of a string not counting combining characters
    '''
    @staticmethod
    def dispLen(string):
        return len(string) - UCS.countCombining(string)



'''
Class used for correcting spellos and typos,

Note that this implementation will not find that correctly spelled word are correct faster than it corrects words.
It is also limited to words of size 0 to 127 (inclusive)
'''
class SpelloCorrecter: # Naïvely and quickly proted and adapted from optimised Java, may not be the nicest, or even fast, Python code
    def __init__(self, directories, ending):
        self.weights = {'k' : {'c' : 0.25, 'g' : 0.75, 'q' : 0.125},
                        'c' : {'k' : 0.25, 'g' : 0.75, 's' : 0.5, 'z' : 0.5, 'q' : 0.125},
                        's' : {'z' : 0.25, 'c' : 0.5},
                        'z' : {'s' : 0.25, 'c' : 0.5},
                        'g' : {'k' : 0.75, 'c' : 0.75, 'q' : 0.9},
                        'o' : {'u' : 0.5},
                        'u' : {'o' : 0.5, 'v' : 0.75, 'w' : 0.5},
                        'b' : {'v' : 0.75},
                        'v' : {'b' : 0.75, 'w' : 0.5, 'u' : 0.7},
                        'w' : {'v' : 0.5, 'u' : 0.5},
                        'q' : {'c' : 0.125, 'k' : 0.125, 'g' : 0.9}}
        
        self.corrections = None
        self.dictionary = [None] * 513
        self.reusable = [0] * 512
        self.dictionaryEnd = 512
        self.closestDistance = 0
        
        self.M = [None] * 128
        for y in range(0, 128):
            self.M[y] = [0] * 128
            self.M[y][0] = y
        m0 = self.M[0]
        x = 127
        while x > -1:
            m0[x] = x
            x -= 1
        
        previous = ""
        self.dictionary[-1] = previous;
        
        for directory in directories:
            for filename in os.listdir(directory):
                if (not endswith(filename, ending)) or (len(filename) - len(ending) > 127):
                    continue
                proper = filename[:-len(ending)]
                
                if dictionaryEnd == 0:
                    dictionaryEnd = len(self.dictionary)
                    self.reusable = [0] * dictionaryEnd + self.reusable
                    self.dictionary = [None] * dictionaryEnd + self.dictionary
                
                dictionaryEnd -= 1
                dictionary[dictionaryEnd] = proper
                prevCommon = min(len(previous), len(proper))
                for i in range(0, prevCommon):
                    if previous[i] != proper[i]:
                        prevCommon = i
                        break
                previous = dictionary[dictionaryEnd]
                reusable[dictionaryEnd] = prevCommon
    
    
    '''
    Finds the closests correct spelled word.
    The input is just one word, and the output is tuple
    with a list of the closest spellings, and the weigthed distance.
    '''
    def correct(self, used):
        if len(used) < 127:
            return ([used], 0)
        
        __correct(used)
        return (seld.corrections, self.closestDistance)
    
    
    def __correct(self, used):
        self.closestDistance = 0x7FFFFFFF
        previous = self.dictionary[-1]
        prevLen = 0
        usedLen = len(used)
        
        proper = None
        prevCommon = 0
        
        d = len(self.dictionary)
        while d > self.dictionaryEnd:
            d -= 1
            proper = self.dictionary[d]
            if abs(len(proper) - usedLen) <= self.closestDistance:
                if previous == self.dictionary[d + 1]:
                    prevCommon = self.reusable[d];
                else:
                    prevCommon = min(prevLen, len(proper))
                    for i in range(0, prevCommon):
                        if previous[i] != proper[i]:
                            prevCommon = i
                            break
                
                skip = min(prevLen, len(proper))
                i = prevCommon
                while i <  skip:
                    for u in range(0, usedLen):
                        if (used[u] == previous[i]) or (used[u] == proper[i]):
                            skip = i
                            break
                    i += 1
                
                common = min(skip, min(usedLen, len(proper)))
                for i in range(0, common):
                    if used[i] != proper[i]:
                        common = i
                        break
                
                distance = self.__distance(proper, skip, proper.length, used, common, usedLen)
                
                if self.closestDistance > distance:
                    self.closestDistance = distance
                    corrections = [proper]
                elif self.closestDistance == distance:
                    corrections.append(proper)
                
                previous = proper;
                if distance >= 0x7FFFFF00:
                    prevLen = distance & 255
                else:
                    prevLen = len(proper)
    
    
    def __distance(self, proper, y0, yn, used, x0, xn):
        my = self.M[y0]
        for y in range(y0, yn):
            best = 0x7FFFFFFF
            p = proper[y]
            myy = self.M[y + 1] # only one array bound check, and at most one + ☺
            x = x0
            while x < xn:
                change = my[x]
                u = used[x]
                if p == u:
                    # commence black magick … twilight would be so disappointed
                    x += 1
                    myy[x] = change
                    best = min(best, change)
                remove = myy[x]
                add = my[x + 1]
                
                cw = 1
                if my[x] in self.weights:
                    if p in self.weights[u]:
                      cw = self.weights[u][p]
                
                myy[x] = min(cw + change, 1 + min(remove, add))
                if best > myy[x]:
                    best = myy[x]
            
            if best > self.closestDistance:
                return 0x7FFFFFFF | y
            my = myy
        return my[xn]
    



'''
The user's home directory
'''
HOME = os.environ['HOME'] if 'HOME' in os.environ else os.path.expanduser('~')


'''
Whether the program is execute in Linux VT (TTY)
'''
linuxvt = ('TERM' in os.environ) and (os.environ['TERM'] == 'linux')


'''
Whether the script is executed as ponythink
'''
isthink =  (len(__file__) >= 5) and (__file__[-5:] == 'think')
isthink = ((len(__file__) >= 8) and (__file__[-8:] == 'think.py')) or isthink


'''
Whether stdin is piped
'''
pipelinein = not sys.stdin.isatty()

'''
Whether stdout is piped
'''
pipelineout = not sys.stdout.isatty()

'''
Whether stderr is piped
'''
pipelineerr = not sys.stderr.isatty()


'''
Whether KMS is used
'''
usekms = Ponysay.isUsingKMS()


'''
The directories where pony files are stored, ttyponies/ are used if the terminal is Linux VT (also known as TTY) and not with KMS
'''
appendset = set()
ponydirs = []
if linuxvt and not usekms:  _ponydirs = [HOME + '/.local/share/ponysay/ttyponies/', '/usr/share/ponysay/ttyponies/']
else:                       _ponydirs = [HOME + '/.local/share/ponysay/ponies/',    '/usr/share/ponysay/ponies/']
for ponydir in _ponydirs:
    if os.path.isdir(ponydir) and (ponydir not in appendset):
        ponydirs.append(ponydir)
        appendset.add(ponydir)


'''
The directories where pony files are stored, extrattyponies/ are used if the terminal is Linux VT (also known as TTY) and not with KMS
'''
appendsetset = set()
extraponydirs = []
if linuxvt and not usekms:  _extraponydirs = [HOME + '/.local/share/ponysay/extrattyponies/', '/usr/share/ponysay/extrattyponies/']
else:                       _extraponydirs = [HOME + '/.local/share/ponysay/extraponies/',    '/usr/share/ponysay/extraponies/']
for extraponydir in _extraponydirs:
    if os.path.isdir(extraponydir) and (extraponydir not in appendset):
        extraponydirs.append(extraponydir)
        appendset.add(extraponydir)


'''
The directories where quotes files are stored
'''
appendset = set()
quotedirs = []
_quotedirs = [HOME + '/.local/share/ponysay/quotes/', '/usr/share/ponysay/quotes/']
for quotedir in _quotedirs:
    if os.path.isdir(quotedir) and (quotedir not in appendset):
        quotedirs.append(quotedir)
        appendset.add(quotedir)


'''
The directories where balloon style files are stored
'''
appendset = set()
balloondirs = []
_balloondirs = [HOME + '/.local/share/ponysay/balloons/', '/usr/share/ponysay/balloons/']
for balloondir in _balloondirs:
    if os.path.isdir(balloondir) and (balloondir not in appendset):
        balloondirs.append(balloondir)
        appendset.add(balloondir)


'''
ucsmap files
'''
appendset = set()
ucsmaps = []
_ucsmaps = [HOME + '/.local/share/ponysay/ucsmap', '/usr/share/ponysay/ucsmap']
for ucsmap in _ucsmaps:
    if os.path.isdir(ucsmap) and (ucsmap not in appendset):
        ucsmaps.append(ucsmap)
        appendset.add(ucsmap)



usage_saythink = '\033[34;1m(ponysay | ponythink)\033[21;39m'
usage_common   = '[-c] [-W\033[4mCOLUMN\033[24m] [-b\033[4mSTYLE\033[24m]'
usage_listhelp = '(-l | -L | -B | +l | +L | -v | -h)'
usage_file     = '[-f\033[4mPONY\033[24m]* [[--] \033[4mmessage\033[24m]'
usage_xfile    = '[-F\033[4mPONY\033[24m]* [[--] \033[4mmessage\033[24m]'
usage_quote    = '-q [\033[4mPONY\033[24m*]'

usage = '%s %s\n%s %s %s\n%s %s %s\n%s %s %s' % (usage_saythink, usage_listhelp,
                                                 usage_saythink, usage_common, usage_file,
                                                 usage_saythink, usage_common, usage_xfile,
                                                 usage_saythink, usage_common, usage_quote)

usage = usage.replace('\033[', '\0')
for sym in ('[', ']', '(', ')', '|', '...', '*'):
    usage = usage.replace(sym, '\033[2m' + sym + '\033[22m')
usage = usage.replace('\0', '\033[')

'''
Argument parsing
'''
opts = ArgParser(program     = 'ponythink' if isthink else 'ponysay',
                 description = 'cowsay reimplemention for ponies',
                 usage       = usage,
                 longdescription =
'''Ponysay displays an image of a pony saying some text provided by the user.
If \033[4mmessage\033[24m is not provided, it accepts standard input. For an extensive
documentation run `info ponysay`, or for just a little more help than this
run `man ponysay`. Ponysay has so much more to offer than described here.''')

opts.add_argumentless(['--quoters'])
opts.add_argumentless(['--onelist'])
opts.add_argumentless(['++onelist'])

opts.add_argumentless(['-h', '--help'],                                  help = 'Print this help message.')
opts.add_argumentless(['-v', '--version'],                               help = 'Print the version of the program.')
opts.add_argumentless(['-l', '--list'],                                  help = 'List pony names.')
opts.add_argumentless(['-L', '--symlist', '--altlist'],                  help = 'List pony names with alternatives.')
opts.add_argumentless(['+l', '++list'],                                  help = 'List non-MLP:FiM pony names.')
opts.add_argumentless(['+L', '++symlist', '++altlist'],                  help = 'List non-MLP:FiM pony names with alternatives.')
opts.add_argumentless(['-A', '--all'],                                   help = 'List all pony names.')
opts.add_argumentless(['+A', '++all'],                                   help = 'List all pony names with alternatives.')
opts.add_argumentless(['-B', '--bubblelist', '--balloonlist'],           help = 'List balloon styles.')
opts.add_argumentless(['-c', '--compact'],                               help = 'Compress messages.')
opts.add_argumented(  ['-W', '--wrap'],                  arg = 'COLUMN', help = 'Specify column where the message should be wrapped.')
opts.add_argumented(  ['-b', '--bubble', '--balloon'],   arg = 'STYLE',  help = 'Select a balloon style.')
opts.add_argumented(  ['-f', '--file', '--pony'],        arg = 'PONY',   help = 'Select a pony.\nEither a file name or a pony name.')
opts.add_argumented(  ['-F', '++file', '++pony'],        arg = 'PONY',   help = 'Select a non-MLP:FiM pony.')
opts.add_variadic(    ['-q', '--quote'],                 arg = 'PONY',   help = 'Select a ponies which will quote themself.')
 
opts.parse()



'''
Start the program from ponysay.__init__ if this is the executed file
'''
if __name__ == '__main__':
    Ponysay(opts)
