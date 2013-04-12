# -*- coding: utf-8 -*-
# 
# Nitrate is copyright 2010 Red Hat, Inc.
# 
# Nitrate is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version. This program is distributed in
# the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranties of TITLE, NON-INFRINGEMENT,
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# 
# The GPL text is available in the file COPYING that accompanies this
# distribution and at <http://www.gnu.org/licenses>.
# 
# Authors:
#   David Malcolm <dmalcolm@redhat.com>

from pprint import pprint

class Variable:
    def __init__(self, name, values):
        self.name = name
        self.values = values

def cartesian_product(vars):
    # Generate cartesian product: all combinations:

    # Vars: list of Variable instances
    # Generate a list of dictionaries, expressing all possible
    # combinations using the given variables
    result = []

    # Generate all using first var:
    for val in vars[0].values:
        result.append(dict([(vars[0].name, val)]))

    # Now "multiply", extending with each subsequent variable's values:
    for var in vars[1:]:
        new_result = []
        
        for coord in result:
            for val in var.values:
                new_coord = dict(coord)
                new_coord[var.name] = val
                new_result.append(new_coord)
        result = new_result
    return result
    

class Environment:
    """
    coord: dictionary of strings (var name) to strings (var value)
    """
    def __init__(self, coord):
        self.coord = coord

    def is_a_refinement_of(self, coord):
        # Does the coord match the values in this env?
        # For example the environment:
        #    {'arch':'i386',
        #     'gpu' :'intel',
        #     'guestos' : 'WinXP'}
        # is a refinement of the coord
        #    {'arch':i386',
        #     'guestos' : 'WinXP'}
        for varname in coord.iterkeys():
            if varname in self.coord:
                # ...then they both have the attribute
                if coord[varname] != self.coord[varname]:
                    # ...but non-equal value
                    return False
            else:
                return False

        # All tests passed:
        return True
            
        

class CoverageMatrix:
    def __init__(self, vars, envs=None):
        """
        vars: list of Variable instances
        self.vars : dictionary from name to Variable inst

        envs: list of Environment instances: all possible variable combos
        """
        self.vars = vars
        self.var_names = []
        self.var_dict = {}
        for var in vars:
            self.var_names.append(var.name)
            self.var_dict[var.name] = var
            
        if envs:
            self.envs = envs
        else:
            self.envs = [Environment(coord) for coord in cartesian_product(vars)]

    def get_row_lengths(self):
        # Get the total number of chars required to render all values
        # We want to minimize the change that horizontal scrolling will be required
        lengths = {}
        for (key, vals) in self.vars.iteritems():
            total = 0
            for val in vals:
                total += len(val)
            lengths[key] = total

    def get_vals(self, varname):
        return self.var_dict[varname].values

    def get_num_vals(self, varname):
        return len(self.var_dict[varname].values)

    def has_coord(self, coord):
        # Is the given coord valid/meaningful for this matrix?
        # Linear search for now:
        for env in self.envs:
            if coord == env.coord:
                return True
        return False
    

class CoverageLayout:
    """
                        ColVars: | ColVar1 val1                 | ColVar1 val 2               |
    RowVars\/                    | ColVar2 val1 | Colvar2 val2  | ColVar2 val1 | Colvar2 val2 |
    -----------------------------+--------------+---------------+--------------+--------------+
    RowVar1 val1 | RowVar2 val 1 |              |               |              |              |
    -----------------------------+--------------+---------------+--------------+--------------+
    RowVar1 val1 | RowVar2 val 2 |
    -----------------------------+--------------+---------------+--------------+--------------+
    RowVar1 val2 | RowVar2 val 1 |
    -----------------------------+--------------+---------------+--------------+--------------+
    RowVar1 val2 | RowVar2 val 2 |
    -----------------------------+--------------+---------------+--------------+--------------+
    
    """
    def __init__(self, cm, rows, cols):
        self.cm = cm
        
        # FIXME: autogenerate these, based on heuristics:
        # They are in order from most-significant to least-significant
        self.rows = rows
        self.cols = cols

        self.row_vars = [self.cm.var_dict[varname] for varname in self.rows]
        self.col_vars = [self.cm.var_dict[varname] for varname in self.cols]

        # Generate headings, as lists of coords
        # Not all combinations will be possible, so we filter the list:
        self.row_headings = filter(lambda coord: self._is_good_heading(coord),
                                   cartesian_product(self.row_vars))
        self.col_headings = filter(lambda coord: self._is_good_heading(coord),
                                   cartesian_product(self.col_vars))

    def _is_good_heading(self, coord):
        # Only generate row/col headings for coords that are valid/meaningful:
        # Only coords that are represented within envs in self.cm.env are
        # "good":
        # For now, do a linear search
        for env in self.cm.envs:
            if env.is_a_refinement_of(coord):
                return True
        return False

    def get_y_size(self):
        # headings then values:
        return len(self.cols) + self.get_num_y_vals()

    def get_num_y_vals(self):
        return len(self.row_headings)

    def get_x_size(self):
        # headings then values:
        return len(self.rows) + self.get_num_x_vals()
        
    def get_num_x_vals(self):
        return len(self.col_headings)

    def get_num_vals(self, varname):
        return self.cm.get_num_vals(varname)

    def get_x_coords(self):
        return self.col_headings

    def get_y_coords(self):
        return self.row_headings

    def get_coord_for_col(self, y):
        if y >= len(self.cols):
            # main body:
            return self.get_y_coords()[y-len(self.cols)]
        else:
            # heading
            return {}
    
    def get_coord_for_row(self, x):
        if x >= len(self.rows):
            # main body:
            return self.get_x_coords()[x-len(self.rows)]
        else:
            # heading:
            return {}

    def get_coord_for_cell(self, x, y):
        result = self.get_coord_for_col(y)
        result.update(self.get_coord_for_row(x))
        return result

    def render(self, cell_renderer):
        # Organize into a table:
        result = '<table border="1">\n'
        for y in range(self.get_y_size()):
            result += '<!-- y=%i -->\n' % y
            result += '<tr>\n'
            for x in range(self.get_x_size()):
                result += '<!-- x=%i (y=%i) -->\n' % (x, y)
                coord = self.get_coord_for_cell(x, y)
                if y >= len(self.cols):
                    if x >= len(self.rows):
                        # main body:
                        result += '<td>\n'
                        if cell_renderer:
                            result += cell_renderer.make_html(self, coord)
                        result += '</td>\n'
                    else:
                        # left border:
                        result += self._make_row_heading(x, y)
                else:
                    # top heading:
                    if x >= len(self.rows):
                        result += self._make_col_heading(x, y)
                    else:
                        # top-left filler:
                        result += '<td></td>\n'
                
            result += '</tr>\n'
        result += '</table>\n'
        return result

    def _make_col_heading(self, x, y):
        if self._is_same_col_heading(x, y):
            # then the cell to the left was for the same value; suppress this <td>:
            return ''

        colspan = self._get_colspan(x, y)
        result = '<td colspan="%i">\n' % colspan
        result += '<b>%s</b>\n' % self._get_col_heading(x, y)
        result += '</td>\n'
        return result

    def _make_row_heading(self, x, y):
        if self._is_same_row_heading(x, y):
            # then the cell above was for the same value; suppress this <td>:
            return ''

        rowspan = self._get_rowspan(x, y)
        result = '<td rowspan="%i">\n' % rowspan
        result += '<b>%s</b>\n' % self._get_row_heading(x, y)
        result += '</td>\n'                        
        return result

    def _get_col_heading(self, x, y):
        coord = self.get_coord_for_cell(x, y)
        return coord[self.cols[y]]

    def _get_row_heading(self, x, y):
        coord = self.get_coord_for_cell(x, y)
        return coord[self.rows[x]]

    def _get_colspan(self, x, y):
        # Figure out how many cols share this heading (including this one):
        result = 1
        this_heading = self._get_col_heading(x, y)
        x += 1
        while x < self.get_x_size():
            if this_heading == self._get_col_heading(x, y):
                result += 1
                x += 1
                continue
            else:
                break
        return result
            
    def _is_same_col_heading(self, x, y):
        if x > len(self.rows):
            if self._get_col_heading(x, y) == self._get_col_heading(x-1, y):
                return True
            else:
                return False
        else:
            # Initial column:
            return False

    def _get_rowspan(self, x, y):
        # Figure out how many rows share this heading (including this one):
        result = 1
        this_heading = self._get_row_heading(x, y)
        y += 1
        while y < self.get_y_size():
            if this_heading == self._get_row_heading(x, y):
                result += 1
                y += 1
                continue
            else:
                break
        return result
            
    def _is_same_row_heading(self, x, y):
        if y > len(self.cols):
            if self._get_row_heading(x, y) == self._get_row_heading(x, y-1):
                return True
            else:
                return False
        else:
            # Initial row:
            return False
        

class CellRenderer(object):
    def make_html(self, cl, coord):
        """
        Generate the content of a <td> element, for the given coord,
        returning it as a string.
        'coord' is a dict, giving the values of a set of env vars
        """
        raise NotImplemented

class DebugCellRenderer(CellRenderer):
    def make_html(self, cl, coord):
        if cl.cm.has_coord(coord):
            return '%s\n' % coord
        else:
            return '(not possible)'


class CheckboxCellRenderer(CellRenderer):
    def make_html(self, cl, coord):
        if cl.cm.has_coord(coord):
            return '<input type="checkbox"></input>\n'
        else:
            return ''

class CoverageCellRenderer(CellRenderer):
    def make_html(self, cl, coord):
        # For now, random:
        return '*\n'

def test_001(out):
    vars = [Variable('Guest OS',
                     ['RHEL3', 'RHEL4', 'RHEL5',
                      'Windows 2003', 'Windows XP', 'Windows Vista']),
            Variable('Guest Memory',
                     ['512MB', '1GB', '4GB', '8GB']),
            Variable('Virt',
                     ['Full', 'Para']),
            Variable('CPU arch',
                     ['i386', 'x86_64', 'ppc'])
            ]
    envs = []
    for coord in cartesian_product(vars):
        if coord['Guest Memory'] == '8GB' and coord['CPU arch'] != 'x86_64':
            continue
        if coord['Guest OS'].startswith('Windows') and coord['Virt'] =='Para':
            continue
        if coord['Guest OS'].startswith('Windows') and coord['CPU arch'] =='ppc':
            continue
        envs.append(Environment(coord))
    cm = CoverageMatrix(vars, envs)
    cl = CoverageLayout(cm,
                        rows = ['Virt', 'Guest OS'], #, 'Network']
                        cols = ['Guest Memory', 'CPU arch']#, 'Graphics']
                        )
    print 'col_headings:', cl.col_headings
    print 'row_headings:', cl.row_headings
    out.write('<h1>test_001</h1>')
    out.write(cl.render(CheckboxCellRenderer()))

def test_002(out):
    vars = [Variable('Guest OS',
                     ['RHEL3', 'RHEL4', 'RHEL5',
                      'Windows 2003', 'Windows XP', 'Windows Vista']),
            Variable('Guest Memory',
                     ['512MB', '1GB', '4GB', '8GB']),
            Variable('Virt',
                     ['Full', 'Para']),
            Variable('CPU arch',
                     ['i386', 'x86_64', 'ppc']),
            Variable('vCPU count',
                     [1, 2, 4, 8]), #, 12, 16, 24, 32, 48, 64]),
            Variable('Storage',
                     ['local']), #, 'fc', 'iSCSI', 'USB']),
            Variable('Network speed',
                     ['100Mb/s']), #, '1Gb/s', '10Gb/s']),
            Variable('Network if count',
                     [1]), #, 2, 4]),
            Variable('Network bondage',
                     ['bonded']), #, 'unbonded']),
            Variable('Host CPU',
                     ['AMD', 'Intel', 'IBM']),
            # how to do processor families?  flags?  etc
            Variable('NPT',
                     ['-', 'npt']),
            Variable('Graphics',
                     ['nv', 'ati', 'intel']),
            ]
    
    envs = []
    # (generating cartesian product then filtering will generate too many values
    # we must filter as we go)
    for guest_os in vars[0].values:
        for guest_memory in vars[1].values:
            for virt in vars[2].values:
                if guest_os.startswith('Windows'):
                    if virt == 'Para':
                        continue
                for cpu_arch in vars[3].values:
                    if (guest_memory == '8GB' or guest_memory == '4GB') \
                           and cpu_arch != 'x86_64':
                        continue
                    if cpu_arch == 'ppc':
                        if guest_os.startswith('Windows'):
                            continue
                        if virt == 'Para':
                            continue
                    for host_cpu in vars[9].values:
                        if cpu_arch == 'ppc':
                            if host_cpu != 'IBM':
                                continue
                        else:
                            if host_cpu == 'IBM':
                                continue
                        for npt in vars[10].values:
                            # NPT is only for Intel:
                            if host_cpu != 'Intel' and npt == 'npt':
                                continue
                            for vcpu_count in vars[4].values:
                                for storage in vars[5].values:
                                    for net_speed in vars[6].values:
                                        for net_ifcount in vars[7].values:
                                            for net_bond in vars[8].values:
                                                for graphics in vars[11].values:
                                                    # All tests passed:
                                                    envs.append(Environment({
                                                        'Guest OS':guest_os,
                                                        'Guest Memory':guest_memory,
                                                        'Virt':virt,
                                                        'CPU arch':cpu_arch,
                                                        'vCPU count':vcpu_count,
                                                        'Storage':storage,
                                                        'Network speed':net_speed,
                                                        'Network if count':net_ifcount,
                                                        'Network bondage':net_bond,
                                                        'Host CPU':host_cpu,
                                                        'NPT':npt,
                                                        'Graphics':graphics,
                                                        }))
    print len(envs)
    cm = CoverageMatrix(vars, envs)
    cl = CoverageLayout(cm,
                        rows = ['Virt', 'Guest OS', 'vCPU count', 'Storage', 'Graphics'],
                        cols = ['CPU arch', 'Host CPU', 'NPT', 'Guest Memory', 'Network speed', 'Network if count', 'Network bondage']
                        )

    out.write('<h1>test_002</h1>')
    out.write(cl.render(CheckboxCellRenderer()))

def test_003(out):
    # Test of JBoss environments
    archs = ['x86',
             'x86_64',
             'ia64',
             'parisc',
             'sparc',
             'ppc',
             'ppc64'] # maybe
    oses = [
        'RHEL4', #(actually 4.5; we ought to capture this)
        'RHEL5', 
        'HPUX',
        'W2K3',
        'SOLARIS9',
        'SOLARIS10',
        ]

    jdkReleases = {
        'SUN': ['1.5.0_1.1', '1.5.0_08', '1.5.0_12'], # which version 1.5?  release versions?  1.6?
        'IBM': ['1.5.0'],
        'BEA': ['1.5.0_08'],
        }
    
    allJdkReleases = []
    for provider in jdkReleases:
        allJdkReleases += ["%s: %s" % (provider, version) for version in jdkReleases[provider]]
        print allJdkReleases

    installmethods = ['Zip', 'RPM', 'GUI']

    dbs = ['Oracle 9i',
           'Oracle 10g',
           'MySQL 5.0',
           'MS SQL Server 2005', # and version?
           'Sybase ASE 12.53' # and 15?
           'DB2 7.2',
           'DB2 9',
           'PostgreSQL', # and version
           'hsql' # not supported, so not tested: so how do we express that?
           ]

    # dbDrivers = driver version, separate from db version
    # so e.g.
    # database: Oracle 9i vs 10g
    # driver: Oracle driver 10
    
    #jmsProviders = ['JBM',
    #                'JBMQ',
    #                'thirdparty #1']  # etc

    class JBossEnvironment(Environment):
        def __init__(self, arch, os, jdk, installmethod, db):#, dbdriver):
            self.arch = arch
            self.os = os
            self.jdk = jdk
            self.installmethod = installmethod
            self.db = db
            #self.dbdriver = dbdriver
            Environment.__init__(self, {
                'CPU arch':self.arch,
                'Operating System':self.os,
                'JDK':self.jdk,
                #'Install Method':self.installmethod,
                'Database':self.db,
                #'DB Driver':self.dbdriver,
                })

        def is_rhel(self):
            return self.os[:4] == 'RHEL'
            
        def is_solaris(self):
            return self.os[:7] == 'SOLARIS'
    
        def is_valid(self):
            if self.installmethod == 'rpm' and not self.is_rhel():
                return False
            if self.arch == 'sparc' and not self.is_solaris():
                return False
            if self.arch == 'parisc' and self.os != 'HPUX':
                return False
            if self.arch[:3] == 'ppc' and self.is_solaris():
                return False
            return True

        def is_supported(self):
            return self.is_valid() # FIXME

    def __str__(self):
        if combo.is_supported():
            sup = "Supported"
        else:
            sup = "Not supported"
        return '%s, %s, %s, %s, %s %s' % (sup,
                                          arch,
                                          os,
                                          'JDK: "%s %s"' % (jdk, release),
                                          'installmethod: %s ' % installmethod,
                                          'DB: db %s, driver: %s' % (db, driverVersion))
        

    vars = [Variable('CPU arch', archs),
            Variable('Operating System', oses),
            Variable('JDK', allJdkReleases),
            #Variable('Install Method', installmethods),
            Variable('Database', dbs),
            #Variable('DB Driver', ['1', '2']),
            ]
    
    envs = []
    for arch in archs:
        for os in oses:
            for jdk in allJdkReleases:
                for installmethod in installmethods:
                    for db in dbs:
                        #for driverVersion in ['1', '2']:
                        env = JBossEnvironment(arch, os, jdk, installmethod, db)#, driverVersion)
                        if env.is_valid():
                            envs.append(env)
                                    
    print len(envs)
    print envs[0].coord
    cm = CoverageMatrix(vars, envs)
    cl = CoverageLayout(cm,
                        rows = ['JDK', 'Database'],#, 'DB Driver']
                        cols = ['CPU arch', 'Operating System']#, 'Install Method'],
                        )
    print 'col_vars:', [cv.name for cv in cl.col_vars]
    print 'col_headings:', cl.col_headings
    print 'row_headings:', cl.row_headings
    out.write('<h1>Sample coverage matrix: JBoss</h1>')
    out.write(cl.render(CheckboxCellRenderer()))

out = open('/tmp/matrix.html', 'w')
#test_001(out)
#test_002(out)
test_003(out)
out.close()


