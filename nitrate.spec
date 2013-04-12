%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%define use_pylint 0

Name:           nitrate
Version:        3.3.4
Release:        1%{?dist}
Summary:        Test Case Management System

Group:          Development/Languages
License:        GPLv2+
URL:            https://fedorahosted.org/nitrate/browser/trunk/nitrate
Source0:        https://fedorahosted.org/releases/n/i/nitrate/%{name}-%{version}.tar.bz2
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:      noarch
BuildRequires:  python-setuptools
BuildRequires:  python-devel
%if %{use_pylint}
BuildRequires:  pylint
BuildRequires:  Django
%endif

Requires:       Django = 1.2.3
# Requires:     mod_python
Requires:       mod_ssl
Requires:       python-memcached
Requires:       python-kerberos
Requires:       python-hashlib
Requires:       kobo-django >= 0.2.0-3
Requires:       mod_auth_kerb
Requires:       mod_wsgi
Requires:       w3m

%description
Nitrate is a tool for tracking testing being done on a product.

It is a database-backed web application, implemented using Django

%prep
%setup -q

# Fixup the version field in the page footer so that it shows the precise
# RPM version-release:
sed --in-place \
  -r 's|NITRATE_VERSION|%{version}-%{release}|' \
  templates/tcms_base.html

%build
%{__python} setup.py build

%if %{use_pylint}
# Run pylint.  Halt the build if there are errors
# There doesn't seem to be a good way to get the result of pylint as an
# exit code.  (upstream bug: http://www.logilab.org/ticket/4691 )

# Capture the output:
pylint --rcfile=tcms/pylintrc tcms > pylint.log

# Ensure the pylint log makes it to the rpm build log:
cat pylint.log

# Analyse the "Messages by category" part of the report, looking for
# non-zero results:
# The table should look like this:
#   +-----------+-------+---------+-----------+
#   |type       |number |previous |difference |
#   +===========+=======+=========+===========+
#   |convention |0      |0        |=          |
#   +-----------+-------+---------+-----------+
#   |refactor   |0      |0        |=          |
#   +-----------+-------+---------+-----------+
#   |warning    |0      |0        |=          |
#   +-----------+-------+---------+-----------+
#   |error      |0      |0        |=          |
#   +-----------+-------+---------+-----------+
#   
# Halt the build if any are non-zero:
grep -E "^\|convention[ ]*\|0[ ]*\|" pylint.log || exit 1
grep -E "^\|refactor[ ]*\|0[ ]*\|" pylint.log || exit 1
grep -E "^\|warning[ ]*\|0[ ]*\|" pylint.log || exit 1
grep -E "^\|error[ ]*\|0[ ]*\|" pylint.log || exit 1
%endif


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

# Copy static content from 32/64bit-specific python dir to shared data dir:
mkdir -p ${RPM_BUILD_ROOT}%{_datadir}/%{name}
mkdir -p ${RPM_BUILD_ROOT}%{_docdir}/%{name}

for d in contrib templates media; do
    cp -r ${d} ${RPM_BUILD_ROOT}%{_datadir}/%{name};
    # chown -R root:root ${RPM_BUILD_ROOT}%{_datadir}/%{name}/${d};
done

for f in `find tcms/core/lib -name templates`; do
    cp -r ${f}/* ${RPM_BUILD_ROOT}%{_datadir}/%{name}/templates/;
done

# Install apache config for the app:
install -m 0644 -D -p contrib/conf/nitrate-httpd.conf  ${RPM_BUILD_ROOT}%{_sysconfdir}/httpd/conf.d/%{name}.conf

 
%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc docs/INSTALL docs/AUTHORS docs/ChangeLog docs/README docs/RELEASENOTES docs/UPGRADING docs/XMLRPC docs/testopia-dump-blank.sql docs/mysql_initial.sql
%{python_sitelib}/tcms/
%{python_sitelib}/Nitrate-%{version}-py*.egg-info/
%{_datadir}/%{name}
%config(noreplace) %{_sysconfdir}/httpd/conf.d/%{name}.conf



%changelog

*Fri Jul 11 2011 Chaobin Tang <ctang@redhat.com> - 3.5
- Usability Improvements (Refer to ChangeLog)

*Fri Mar 3 2011 Chaobin Tang <ctang@redhat.com> - 3.4.1
- Testing Report Implementation
- Several Bug Fixes (Refer to ChangeLog)

*Fri Mar 3 2011 Chaobin Tang <ctang@redhat.com> - 3.4
- Advance Search Implementation
- Several Bug Fixes (Refer to ChangeLog)

*Fri Feb 25 2011 Yuguang Wang <yuwang@redhat.com> - 3.3-3
- Upstream released new version

*Tue Feb 15 2011 Yuguang Wang <yuwang@redhat.com> - 3.3-2
- Upstream released new version

*Mon Jan 24 2011 Yuguang Wang <yuwang@redhat.com> - 3.3-1
- Upstream released new version
- Include apache QPID support
- Completed global signal processor

* Thu Dec 1 2010 Xuqing Kuang <xkuang@redhat.com> - 3.2-4
- Upstream released new version

* Tue Nov 30 2010 Xuqing Kuang <xkuang@redhat.com> - 3.2-3
- Upstream released new version

* Tue Nov 23 2010 Xuqing Kuang <xkuang@redhat.com> - 3.2-2
- Upstream released new version

* Tue Nov 9 2010 Xuqing Kuang <xkuang@redhat.com> - 3.2-1
- Upstream released new version

* Fri Sep 17 2010 Xuqing Kuang <xkuang@redhat.com> - 3.1.1-3
- Upstream released new version

* Wed Sep 15 2010 Xuqing Kuang <xkuang@redhat.com> - 3.1.1-2
- Upstream released new version

* Wed Sep 8 2010 Xuqing Kuang <xkuang@redhat.com> - 3.1.1-1
- Upstream released new version
- Add highcharts for future reporting
- Add django-pagination support.

* Thu Aug 12 2010 Xuqing Kuang <xkuang@redhat.com> - 3.1.0-2
- Upstream released new version

* Thu Aug 12 2010 Xuqing Kuang <xkuang@redhat.com> - 3.1.0-1
- Upstream released new version

* Fri Aug 2 2010 Xuqing Kuang <xkuang@redhat.com> - 3.0.4-3
- Upstream released new version

* Fri Jul 30 2010 Xuqing Kuang <xkuang@redhat.com> - 3.0.4-2
- Upstream released new version

* Wed Jul 21 2010 Xuqing Kuang <xkuang@redhat.com> - 3.0.4-1
- Upstream released new version

* Mon Jun 28 2010 Xuqing Kuang <xkuang@redhat.com> - 3.0.3-2.svn2859
- Upstream released new version

* Sat Jun 12 2010 Xuqing Kuang <xkuang@redhat.com> - 3.0.3-1.svn2841
- Upstream released new version

* Tue Jun 8 2010 Xuqing Kuang <xkuang@redhat.com> - 3.0.2-2.svn2819
- Upstream released new version

* Thu Jun 3 2010 Xuqing Kuang <xkuang@redhat.com> - 3.0.2-1.svn2805
- Upstream released new version
- Add JavaScript library 'livepiple'.

* Wed May 19 2010 Xuqing Kuang <xkuang@redhat.com> - 3.0.1-3.svn2748
- Upstream released new version

* Thu May 13 2010 Xuqing Kuang <xkuang@redhat.com> - 3.0.1-2.svn2736
- Upstream released new version

* Tue May 11 2010 Xuqing Kuang <xkuang@redhat.com> - 3.0.1-1.svn2728
- Upstream released new version

* Fri Apr 16 2010 Xuqing Kuang <xkuang@redhat.com> - 3.0-1b2.svn2665
- Upstream released new version

* Wed Apr 14 2010 Xuqing Kuang <xkuang@redhat.com> - 3.0-1b1.svn2650
- Upstream released new version

* Thu Apr 1 2010 Xuqing Kuang <xkuang@redhat.com> - 2.3-5.svn2599
- Upstream released new version

* Mon Mar 29 2010 Xuqing Kuang <xkuang@redhat.com> - 2.3-4.svn2594
- Upstream released new version

* Tue Mar 23 2010 Xuqing Kuang <xkuang@redhat.com> - 2.3-3.svn2577
- Upstream released new version

* Mon Mar 22 2010 Xuqing Kuang <xkuang@redhat.com> - 2.3-2.svn2568
- Upstream released new version

* Thu Mar 18 2010 Xuqing Kuang <xkuang@redhat.com> - 2.3-1.svn2564
- Upstream released new version

* Wed Mar 17 2010 Xuqing Kuang <xkuang@redhat.com> -2.2-4.svn2504
- Upstream released new version

* Fri Mar 12 2010 Xuqing Kuang <xkuang@redhat.com> - 2.2-3.svn2504
- Upstream released new version

* Thu Mar 4 2010 Xuqing Kuang <xkuang@redhat.com> - 2.2-2.svn2504
- Upstream released new version

* Mon Mar 1 2010 Xuqing Kuang <xkuang@redhat.com> - 2.2-1.svn2500
- Upstream released new version

* Thu Feb 11 2010 Xuqing Kuang <xkuang@redhat.com> - 2.1-4.svn2461
- Upstream released new version

* Tue Feb 2 2010 Xuqing Kuang <xkuang@redhat.com> - 2.1-3.svn2449
- Upstream released new version

* Tue Feb 2 2010 Xuqing Kuang <xkuang@redhat.com> - 2.1-2.svn2446
- Upstream released new version

* Mon Feb 1 2010 Xuqing Kuang <xkuang@redhat.com> - 2.1-1.svn2443
- Upstream released new version

* Mon Jan 18 2010 Xuqing Kuang <xkuang@redhat.com> - 2.0-3.svn2403
- Upstream released new version

* Mon Jan 18 2010 Xuqing Kuang <xkuang@redhat.com> - 2.0-2.svn2402
- Upstream released new version

* Fri Jan 15 2010 Xuqing Kuang <xkuang@redhat.com> - 2.0-1.svn2394
- Upstream released new version

* Mon Jan 11 2010 Xuqing Kuang <xkuang@redhat.com> - 2.0-1RC.svn2368
- Upstream released new version

* Tue Dec 29 2009 Xuqing Kuang <xkuang@redhat.com> - 2.0-1beta.svn2318
- Upstream released new version

* Fri Dec 18 2009 Xuqing Kuang <xkuang@redhat.com> - 1.3-3.svn2261
- Upstream released new version

* Tue Dec 8 2009 Xuqing Kuang <xkuang@redhat.com> - 1.3-2.svn2229
- Upstream released new version

* Fri Dec 4 2009 Xuqing Kuang <xkuang@redhat.com> - 1.3-1.svn2213
- Upstream released new version

* Wed Nov 25 2009 Xuqing Kuang <xkuang@redhat.com> - 1.2-3.svn2167
- Upstream released new version

* Wed Nov 25 2009 Xuqing Kuang <xkuang@redhat.com> - 1.2-2.svn2167
- Upstream released new version

* Fri Nov 20 2009 Xuqing Kuang <xkuang@redhat.com> - 1.2-1.svn2143
- Upstream released new version

* Mon Nov 9 2009 Xuqing Kuang <xkuang@redhat.com> - 1.1-1.svn2097
- Upstream released new version

* Mon Nov 9 2009 Xuqing Kuang <xkuang@redhat.com> - 1.0-9.svn2046
- Upstream released new version

* Thu Oct 22 2009 Xuqing Kuang <xkuang@redhat.com> - 1.0-7.svn2046.RC
- Upstream released new version

* Thu Oct 22 2009 Xuqing Kuang <xkuang@redhat.com> - 1.0-6.svn2046.RC
- Upstream released new version

* Wed Oct 21 2009 Xuqing Kuang <xkuang@redhat.com> - 1.0-5.svn2042.RC
- Upstream released new version

* Wed Oct 16 2009 Xuqing Kuang <xkuang@redhat.com> - 2.0-4.svn2006.RC
- Upstream released new version

* Wed Oct 14 2009 Xuqing Kuang <xkuang@redhat.com> - 2.0-3.svn1971
- Upstream released new version

* Wed Sep 30 2009 Xuqing Kuang <xkuang@redhat.com> - 2.0-2.svn1938
- Upstream released new version

* Tue Sep 23 2009 Xuqing Kuang <xkuang@redhat.com> - 2.0-2.svn1898
- Upstream released new version

* Tue Sep 15 2009 Xuqing Kuang <xkuang@redhat.com> - 2.0-1.svn1863
- Upstream released new version

* Tue Sep 1 2009 Xuqing Kuang <xkuang@redhat.com> - 2.0-1.svn1833
- Upstream released new version

* Wed Jul 22 2009 Xuqing Kuang <xkuang@redhat.com> - 2.0-1.svn1799
- Upstream released new version

* Thu Mar 19 2009 David Malcolm <dmalcolm@redhat.com> - 0.16-6.svn1547
- Upstream released new version

* Tue Mar 17 2009 David Malcolm <dmalcolm@redhat.com> - 0.16-5.svn1525
- Upstream released new version

* Tue Mar 17 2009 David Malcolm <dmalcolm@redhat.com> - 0.16-4.svn1525
- Upstream released new version

* Thu Mar 12 2009 David Malcolm <dmalcolm@redhat.com> - 0.16-3.svn1487
- Upstream released new version

* Thu Mar 12 2009 David Malcolm <dmalcolm@redhat.com> - 0.16-2.svn1487
- Upstream released new version

* Thu Mar 12 2009 David Malcolm <dmalcolm@redhat.com> - 0.16-1.svn1487
- Upstream released new version

* Tue Feb 24 2009 David Malcolm <dmalcolm@redhat.com> - 0.13-4
- Upstream released new version

* Tue Feb 24 2009 David Malcolm <dmalcolm@redhat.com> - 0.13-3
- Upstream released new version

* Wed Feb 18 2009 David Malcolm <dmalcolm@redhat.com> - 0.13-2.svn1309
- Upstream released new version
- add mod_python and python-memcached dependencies
- add apache config to correct location

* Thu Feb 12 2009 David Malcolm <dmalcolm@redhat.com> - 0.13-1.svn1294
- initial packaging
