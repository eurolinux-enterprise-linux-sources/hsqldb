# Copyright (c) 2000-2007, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

%define _with_gcj_support 1

%define gcj_support %{?_with_gcj_support:1}%{!?_with_gcj_support:%{?_without_gcj_support:0}%{!?_without_gcj_support:%{?_gcj_support:%{_gcj_support}}%{!?_gcj_support:0}}}

%define section		devel

%define cvs_version	1_8_0_10

Name:		hsqldb
Version:	1.8.0.10
Release:	8%{?dist}
Epoch:		1
Summary:	Hsqldb Database Engine
License:	BSD
Url:		http://hsqldb.sourceforge.net/
#http://downloads.sourceforge.net/hsqldb/hsqldb_1_8_0_9.zip
Source0:	%{name}_%{cvs_version}.zip
Source1:	%{name}-1.8.0-standard.cfg
Source2:	%{name}-1.8.0-standard-server.properties
Source3:	%{name}-1.8.0-standard-webserver.properties
Source4:	%{name}-1.8.0-standard-sqltool.rc
Patch0:		%{name}-1.8.0-scripts.patch
Patch1:		hsqldb-tmp.patch
Patch2:		hsqldb-initscript.patch
Patch3:		%{name}-1.8.0-bitxor-bitor.patch
Patch4:		%{name}-1.8.0-autoincrement.patch
Requires:	apache-tomcat-apis
Requires(post):	/bin/rm,/bin/ln
Requires(post):	apache-tomcat-apis
Requires(preun): /bin/rm
Requires(pre):	shadow-utils
BuildRequires:	ant
BuildRequires:	junit
BuildRequires:	jpackage-utils >= 0:1.5
BuildRequires:	apache-tomcat-apis
Group:		Applications/Databases
%if ! %{gcj_support}
Buildarch:	noarch
%endif
Buildroot:	%{_tmppath}/%{name}-%{version}-buildroot

%if %{gcj_support}
BuildRequires:		java-gcj-compat-devel
Requires(post):		java-gcj-compat
Requires(postun):	java-gcj-compat
%endif

%description
HSQLdb is a relational database engine written in JavaTM , with a JDBC
driver, supporting a subset of ANSI-92 SQL. It offers a small (about
100k), fast database engine which offers both in memory and disk based
tables. Embedded and server modes are available. Additionally, it
includes tools such as a minimal web server, in-memory query and
management tools (can be run as applets or servlets, too) and a number
of demonstration examples.
Downloaded code should be regarded as being of production quality. The
product is currently being used as a database and persistence engine in
many Open Source Software projects and even in commercial projects and
products! In it's current version it is extremely stable and reliable.
It is best known for its small size, ability to execute completely in
memory and its speed. Yet it is a completely functional relational
database management system that is completely free under the Modified
BSD License. Yes, that's right, completely free of cost or restrictions!

%package manual
Summary:	Manual for %{name}
Group:		Applications/Databases

%description manual
Documentation for %{name}.

%package javadoc
Summary:	Javadoc for %{name}
Group:		Applications/Databases
# For /bin/rm and /bin/ln
Requires(post):	coreutils
Requires(preun):coreutils

%description javadoc
Javadoc for %{name}.

%package demo
Summary:	Demo for %{name}
Group:		Applications/Databases
Requires:	%{name} = %{epoch}:%{version}-%{release}

%description demo
Demonstrations and samples for %{name}.

%prep
%setup -T -c -n %{name}
(cd ..
unzip -q %{SOURCE0} 
)
# set right permissions
find . -name "*.sh" -exec chmod 755 \{\} \;
# remove all _notes directories
for dir in `find . -name _notes`; do rm -rf $dir; done
# remove all binary libs
find . -name "*.jar" -exec rm -f {} \;
find . -name "*.class" -exec rm -f {} \;
find . -name "*.war" -exec rm -f {} \;
# correct silly permissions
chmod -R go=u-w *

%patch0
%patch1 -p1
%patch2 -p2
%patch3 -p8
%patch4 -p3

%build
export CLASSPATH=$(build-classpath \
jsse/jsse \
jsse/jnet \
jsse/jcert \
jdbc-stdext \
apache-tomcat-apis/tomcat-servlet2.5-api \
junit)
pushd build
ant jar javadoc
popd

%install
rm -rf $RPM_BUILD_ROOT
# jar
install -d -m 755 $RPM_BUILD_ROOT%{_javadir}
install -m 644 lib/%{name}.jar $RPM_BUILD_ROOT%{_javadir}/%{name}-%{version}.jar
(cd $RPM_BUILD_ROOT%{_javadir} && for jar in *-%{version}.jar; do ln -sf ${jar} ${jar/-%{version}/}; done)
# bin
install -d -m 755 $RPM_BUILD_ROOT%{_bindir}
install -m 755 bin/runUtil.sh $RPM_BUILD_ROOT%{_bindir}/%{name}RunUtil
# sysv init
install -d -m 755 $RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d
install -m 755 bin/%{name} $RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d/%{name}
# config
install -d -m 755 $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
install -m 644 %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/%{name}
# serverconfig
install -d -m 755 $RPM_BUILD_ROOT%{_localstatedir}/lib/%{name}
install -m 644 %{SOURCE2} $RPM_BUILD_ROOT%{_localstatedir}/lib/%{name}/server.properties
install -m 644 %{SOURCE3} $RPM_BUILD_ROOT%{_localstatedir}/lib/%{name}/webserver.properties
install -m 600 %{SOURCE4} $RPM_BUILD_ROOT%{_localstatedir}/lib/%{name}/sqltool.rc
# lib
install -d -m 755 $RPM_BUILD_ROOT%{_localstatedir}/lib/%{name}/lib
install -m 644 lib/functions $RPM_BUILD_ROOT%{_localstatedir}/lib/%{name}/lib
# data
install -d -m 755 $RPM_BUILD_ROOT%{_localstatedir}/lib/%{name}/data
# demo
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/%{name}/demo
install -m 755 demo/*.sh $RPM_BUILD_ROOT%{_datadir}/%{name}/demo
install -m 644 demo/*.html $RPM_BUILD_ROOT%{_datadir}/%{name}/demo
# javadoc
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -r doc/src/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
rm -rf doc/src
# manual
install -d -m 755 $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}
cp -r doc/* $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}
cp index.html $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%pre
# Add the "hsqldb" user and group
# we need a shell to be able to use su - later
%{_sbindir}/groupadd -g 96 -f -r %{name} 2> /dev/null || :
%{_sbindir}/useradd -u 96 -g %{name} -s /sbin/nologin \
    -d %{_localstatedir}/lib/%{name} -r %{name} 2> /dev/null || :

%post
rm -f %{_localstatedir}/lib/%{name}/lib/hsqldb.jar
rm -f %{_localstatedir}/lib/%{name}/lib/servlet.jar
(cd %{_localstatedir}/lib/%{name}/lib
    ln -s $(build-classpath hsqldb) hsqldb.jar
    ln -s $(build-classpath apache-tomcat-apis/tomcat-servlet2.5-api) servlet.jar
)

%if %{gcj_support}
if [ -x %{_bindir}/rebuild-gcj-db ]
then
  %{_bindir}/rebuild-gcj-db
fi
%endif

%postun
%if %{gcj_support}
if [ -x %{_bindir}/rebuild-gcj-db ]
then
  %{_bindir}/rebuild-gcj-db
fi
%endif

%preun
if [ "$1" = "0" ]; then
    rm -f %{_localstatedir}/lib/%{name}/lib/hsqldb.jar
    rm -f %{_localstatedir}/lib/%{name}/lib/servlet.jar
    #%{_sbindir}/userdel %{name} >> /dev/null 2>&1 || :
    #%{_sbindir}/groupdel %{name} >> /dev/null 2>&1 || :
fi

%post javadoc
rm -f %{_javadocdir}/%{name}
ln -s %{name}-%{version} %{_javadocdir}/%{name}

%preun javadoc
if [ "$1" = "0" ]; then
    rm -f %{_javadocdir}/%{name}
fi

%files
%defattr(0644,root,root,0755)
%dir %{_docdir}/%{name}-%{version}
%doc %{_docdir}/%{name}-%{version}/hsqldb_lic.txt
%{_javadir}/*
%attr(0755,root,root) %{_bindir}/*
%attr(0755,root,root) %{_sysconfdir}/rc.d/init.d/%{name}
%attr(0644,root,root) %{_sysconfdir}/sysconfig/%{name}
%attr(0755,hsqldb,hsqldb) %{_localstatedir}/lib/%{name}/data
%{_localstatedir}/lib/%{name}/lib
%attr(0644,root,root) %{_localstatedir}/lib/%{name}/server.properties
%attr(0644,root,root) %{_localstatedir}/lib/%{name}/webserver.properties
%attr(0600,hsqldb,hsqldb) %{_localstatedir}/lib/%{name}/sqltool.rc
%dir %{_localstatedir}/lib/%{name}

%if %{gcj_support}
%attr(-,root,root) %{_libdir}/gcj/%{name}
%endif

%files manual
%defattr(0644,root,root,0755)
%doc %{_docdir}/%{name}-%{version}

%files javadoc
%defattr(0644,root,root,0755)
%{_javadocdir}/%{name}-%{version}

%files demo
%defattr(0644,root,root,0755)
%{_datadir}/%{name}

%changelog
* Mon Apr 26 2010 Jeff Johnston <jjohnstn@redhat.com> - 1.8.0.10-8
- Resolves: #585125
- Additional fixes to hsqldb script.

* Fri Apr 23 2010 Jeff Johnston <jjohnstn@redhat.com> - 1.8.0.10-7
- Resolves: #585125
- Fix hsqldb script to be LSB-compliant.

* Tue Feb 09 2010 Andrew Overholt <overholt@redhat.com> 1.8.0.10-6
- Use apache-tomcat-apis instead of servletapi5.

* Fri Jan 08 2010 Jeff Johnston <jjohnstn@redhat.com> - 1.8.0.10-5
- Resolves: #553802
- Fix rpmlint warnings.

* Thu Oct 22 2009 Jesse Keating <jkeating@redhat.com> - 1.8.0.10-4
- Add patches from Caolan for #523110 and #517839

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:1.8.0.10-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:1.8.0.10-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Thu Jul 10 2008 Jon Prindiville <jprindiv@redhat.com> - 1:1.8.0.10-1
- Upgrade to 1.8.0.10

* Wed Jul  9 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 1:1.8.0.9-3
- drop repotag

* Thu May 29 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 1:1.8.0.9-2jpp.2
- fix license tag

* Mon Feb 18 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 1:1.8.0.9-2jpp.1
- Autorebuild for GCC 4.3

* Tue Jan 22 2008 Jon Prindiville <jprindiv@redhat.com> 1.8.0.9-1jpp.1
- Fix for bz# 428520: Defining JAVA_HOME in /etc/sysconfig/hsqldb

* Thu Jan 17 2008 Jon Prindiville <jprindiv@redhat.com> 1.8.0.9-1jpp
- Upgrade to 1.8.0.9

* Tue Dec 04 2007 Jon Prindiville <jprindiv@redhat.com> 1.8.0.8-1jpp.5
- Backport patch, addressing CVE-2007-4576

* Tue Oct 16 2007 Deepak Bhole <dbhole@redhat.com> 1.8.0.8-1jpp.4
- Rebuild

* Tue Oct 16 2007 Deepak Bhole <dbhole@redhat.com> 1.8.0.8-1jpp.3
- Fix bz# 218135: Init script now specifies shell when starting service

* Thu Sep 20 2007 Deepak Bhole <dbhole@redhat.com> 1:1.8.0.8-1jpp.2
- Added %%{?dist} to release, as per Fedora policy

* Fri Aug 31 2007 Fernando Nasser <fnasser@redhat.com> 1:1.8.0.8-1jpp.1
- Merge with upstream

* Fri Aug 31 2007 Fernando Nasser <fnasser@redhat.com> 1:1.8.0.8-1jpp
- Upgrade to 1.8.0.8

* Mon Jan 22 2007 Deepak Bhole <dbhole@redhat.com> 1:1.8.0.7-2jpp
- Update copyright date

* Thu Jan 22 2007 Deepak Bhole <dbhole@redhat.com> 1:1.8.0.7-1jpp.2
- Bump release to build in rawhide

* Thu Jan 11 2007 Deepak Bhole <dbhole@redhat.com> 1:1.8.0.7-1jpp
- Updgrade to 1.8.0.7

* Thu Nov 30 2006 Deepak Bhole <dbhole@redhat.com> 1:1.8.0.4-4jpp.2
- Bump release to build in rawhide

* Wed Nov 29 2006 Deepak Bhole <dbhole@redhat.com> 1:1.8.0.4-4jpp
- Added missing entries to the files section
- From fnasser@redhat.com:
  - Add post requires for servletapi5 to ensure installation order
- From sgrubb@redhat.com:
  - Apply patch correcting tmp file usage

* Wed Oct 11 2006 Fernando Nasser <fnasser@redhat.com> 1:1.8.0.4-3jpp.4
- Add post requires for servletapi5 to ensure installation order

* Sun Oct 01 2006 Jesse Keating <jkeating@redhat.com> 1:1.8.0.4-3jpp.3
- rebuilt for unwind info generation, broken in gcc-4.1.1-21

* Wed Sep 20 2006 Steve Grubb <sgrubb@redhat.com> 1:1.8.0.4-3jpp.2
- Apply patch correcting tmp file usage

* Mon Aug 21 2006 Deepak Bhole <dbhole@redhat.com> 1:1.8.0.4-3jpp
- Add missing postun section.

* Tue Aug 08 2006 Deepak Bhole <dbhole@redhat.com> 1:1.8.0.4-2jpp.2
- Fix regression re: missing shadow-utils prereq.

* Fri Aug 04 2006 Deepak Bhole <dbhole@redhat.com> 1:1.8.0.4-2jpp
- Add missing requirements.
- Merge with fc spec.
  - From gbenson@redhat.com:
    - Change /etc/init.d to /etc/rc.d/init.d.
    - Create hsqldb user and group with low IDs (RH bz #165670).
    - Do not remove hsqldb user and group on uninstall.
    - Build with servletapi5.
  - From ashah@redhat.com:
    - Change hsqldb user shell to /sbin/nologin.
  - From notting@redhat.com
    - use an assigned user/group id

* Fri Apr 28 2006 Fernando Nasser <fnasser@redhat.com> 1:1.8.0.4-1jpp
- First JPP 1.7 build
- Upgrade to 1.8.0.4

* Tue Jul 26 2005 Fernando Nasser <fnasser@redhat.com> 0:1.80.1-1jpp
- Upgrade to 1.8.0.1

* Mon Mar 07 2005 Fernando Nasser <fnasser@redhat.com> 0:1.73.3-1jpp
- Upgrade to 1.7.3.3

* Wed Mar 02 2005 Fernando Nasser <fnasser@redhat.com> 0:1.73.0-1jpp
- Upgrade to 1.7.3.0

* Wed Aug 25 2004 Ralph Apel <r.apel at r-apel.de> 0:1.72.3-2jpp
- Build with ant-1.6.2

* Mon Aug 16 2004 Ralph Apel <r.apel at r-apel.de> 0:1.72.3-1jpp
- 1.7.2.3 stable

* Fri Jun 04 2004 Ralph Apel <r.apel at r-apel.de> 0:1.72-0.rc6b.1jpp
- 1.7.2 preview

* Tue May 06 2003 David Walluck <david@anti-microsoft.org> 0:1.71-1jpp
- 1.71
- update for JPackage 1.5

* Mon Mar 18 2002 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.61-6jpp 
- generic servlet support

* Mon Jan 21 2002 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.61-5jpp 
- versioned dir for javadoc
- no dependencies for javadoc package
- stricter dependencies for demo package
- section macro
- adaptation to new servlet3 package

* Mon Dec 17 2001 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.61-4jpp
- javadoc in javadoc package
- doc reorganisation
- removed Requires: ant
- patches regenerated and bzipped

* Wed Nov 21 2001 Christian Zoffoli <czoffoli@littlepenguin.org> 1.61-3jpp
- removed packager tag
- new jpp extension

* Fri Nov 09 2001 Christian Zoffoli <czoffoli@littlepenguin.org> 1.61-2jpp
- added BuildRequires:	servletapi3 ant
- added Requires:	servletapi3 ant

* Fri Nov 09 2001 Christian Zoffoli <czoffoli@littlepenguin.org> 1.61-1jpp
- complete spec restyle
- splitted & improved linuxization patch

* Fri Nov 09 2001 Christian Zoffoli <czoffoli@littlepenguin.org> 1.60-1jpp
- 1.60 first "official release" of Hsqldb

* Fri Nov 09 2001 Christian Zoffoli <czoffoli@littlepenguin.org> 1.43-2jpp
- fixed version

* Fri Nov 09 2001 Christian Zoffoli <czoffoli@littlepenguin.org> 1.43-1jpp
- first release
- linuxization patch (doc + script)

