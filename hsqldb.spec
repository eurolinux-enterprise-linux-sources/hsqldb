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

%global cvs_version 1_8_1_3

Name:           hsqldb
Version:        1.8.1.3
Release:        12%{?dist}
Epoch:          1
Summary:        HyperSQL Database Engine
License:        BSD
URL:            http://hsqldb.sourceforge.net/
Group:          Applications/Databases

BuildArch:      noarch

Source0:        http://downloads.sourceforge.net/hsqldb/%{name}_%{cvs_version}.zip
Source1:        %{name}-1.8.0-standard.cfg
Source2:        %{name}-1.8.0-standard-server.properties
Source3:        %{name}-1.8.0-standard-webserver.properties
Source4:        %{name}-1.8.0-standard-sqltool.rc
Source5:        http://mirrors.ibiblio.org/pub/mirrors/maven2/%{name}/%{name}/1.8.0.10/%{name}-1.8.0.10.pom
# Custom systemd files - talking with upstream about incorporating them, see
# http://sourceforge.net/projects/hsqldb/forums/forum/73673/topic/5367103
Source6:        %{name}.systemd
Source7:        %{name}-wrapper
Source8:        %{name}-post
Source9:        %{name}-stop

Patch0:         %{name}-1.8.0-scripts.patch
Patch1:         hsqldb-tmp.patch
Patch2:         %{name}-1.8.0-specify-su-shell.patch
Patch3:         %{name}-jdbc-4.1.patch

BuildRequires:  ant
BuildRequires:  jpackage-utils >= 0:1.5
BuildRequires:  junit
BuildRequires:  systemd-units
BuildRequires:  tomcat-servlet-3.0-api

Requires:       java
Requires:       tomcat-servlet-3.0-api
Requires(pre):  shadow-utils
Requires(post): systemd-sysv
Requires(post): systemd-units
Requires(preun):  initscripts
Requires(preun):  systemd-units
Requires(postun): systemd-units


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
Summary:    Manual for %{name}
Group:      Documentation

%description manual
Documentation for %{name}.

%package javadoc
Summary:    Javadoc for %{name}
Group:      Documentation
Requires:   jpackage-utils

%description javadoc
Javadoc for %{name}.

%package demo
Summary:    Demo for %{name}
Group:      Development/Tools
Requires:   %{name} = %{epoch}:%{version}-%{release}

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
%patch2
%patch3 -p1

cp %{SOURCE5} ./pom.xml

%build
export CLASSPATH=$(build-classpath \
servlet \
junit)
pushd build
ant jar javadoc
popd

%install
# jar
install -d -m 755 %{buildroot}%{_javadir}
install -m 644 lib/%{name}.jar %{buildroot}%{_javadir}/%{name}.jar
# bin
install -d -m 755 %{buildroot}%{_bindir}
install -m 755 bin/runUtil.sh %{buildroot}%{_bindir}/%{name}RunUtil
# systemd
install -d -m 755 %{buildroot}%{_unitdir}
install -d -m 755 %{buildroot}%{_prefix}/lib/%{name}
install -m 644 %{SOURCE6} %{buildroot}%{_unitdir}/%{name}.service
install -m 755 %{SOURCE7} %{buildroot}%{_prefix}/lib/%{name}/%{name}-wrapper
install -m 755 %{SOURCE8} %{buildroot}%{_prefix}/lib/%{name}/%{name}-post
install -m 755 %{SOURCE9} %{buildroot}%{_prefix}/lib/%{name}/%{name}-stop
# config
install -d -m 755 %{buildroot}%{_sysconfdir}/sysconfig
install -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/sysconfig/%{name}
# serverconfig
install -d -m 755 %{buildroot}%{_localstatedir}/lib/%{name}
install -m 644 %{SOURCE2} %{buildroot}%{_localstatedir}/lib/%{name}/server.properties
install -m 644 %{SOURCE3} %{buildroot}%{_localstatedir}/lib/%{name}/webserver.properties
install -m 600 %{SOURCE4} %{buildroot}%{_localstatedir}/lib/%{name}/sqltool.rc
# lib
install -d -m 755 %{buildroot}%{_localstatedir}/lib/%{name}/lib
install -m 644 lib/functions %{buildroot}%{_localstatedir}/lib/%{name}/lib
# data
install -d -m 755 %{buildroot}%{_localstatedir}/lib/%{name}/data
# demo
install -d -m 755 %{buildroot}%{_datadir}/%{name}/demo
install -m 755 demo/*.sh %{buildroot}%{_datadir}/%{name}/demo
install -m 644 demo/*.html %{buildroot}%{_datadir}/%{name}/demo
# javadoc
install -d -m 755 %{buildroot}%{_javadocdir}/%{name}
cp -r doc/src/* %{buildroot}%{_javadocdir}/%{name}
rm -rf doc/src
# manual
install -d -m 755 %{buildroot}%{_docdir}/%{name}-%{version}
cp -r doc/* %{buildroot}%{_docdir}/%{name}-%{version}
cp index.html %{buildroot}%{_docdir}/%{name}-%{version}

# Maven metadata
install -pD -T -m 644 pom.xml %{buildroot}%{_mavenpomdir}/JPP-%{name}.pom
%add_maven_depmap

pushd %{buildroot}%{_localstatedir}/lib/%{name}/lib
    # build-classpath can not be used as the jar is not
    # yet present during the build
    ln -s %{_javadir}/hsqldb.jar hsqldb.jar
    ln -s $(build-classpath servlet) servlet.jar
popd

%preun
%systemd_preun hsqldb.service

%pre
# Add the "hsqldb" user and group
# we need a shell to be able to use su - later
%{_sbindir}/groupadd -g 96 -f -r %{name} 2> /dev/null || :
%{_sbindir}/useradd -u 96 -g %{name} -s /sbin/nologin \
    -d %{_localstatedir}/lib/%{name} -r %{name} 2> /dev/null || :

%post
%systemd_post hsqldb.service

%postun
%systemd_postun_with_restart hsqldb.service

%triggerun -- hsqldb < 1.8.1.3-9
# Save the current service runlevel info
# User must manually run systemd-sysv-convert --apply httpd
# to migrate them to systemd targets
/usr/bin/systemd-sysv-convert --save hsqldb >/dev/null 2>&1 ||:

# If the package is allowed to autostart:
/bin/systemctl --no-reload enable hsqldb.service >/dev/null 2>&1 ||:

# Run these because the SysV package being removed won't do them
/sbin/chkconfig --del hsqldb >/dev/null 2>&1 || :
/bin/systemctl try-restart hsqldb.service >/dev/null 2>&1 || :

%files
%defattr(-,root,root,-)
%doc doc/hsqldb_lic.txt
%{_javadir}/*
%attr(0755,root,root) %{_bindir}/*
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%{_unitdir}/%{name}.service
%{_prefix}/lib/%{name}/%{name}-wrapper
%{_prefix}/lib/%{name}/%{name}-post
%{_prefix}/lib/%{name}/%{name}-stop
%attr(0700,hsqldb,hsqldb) %{_localstatedir}/lib/%{name}/data
%{_localstatedir}/lib/%{name}/lib
%{_localstatedir}/lib/%{name}/server.properties
%{_localstatedir}/lib/%{name}/webserver.properties
%attr(0600,hsqldb,hsqldb) %{_localstatedir}/lib/%{name}/sqltool.rc
%dir %{_localstatedir}/lib/%{name}
%{_mavendepmapfragdir}/*
%{_mavenpomdir}/*

%files manual
%doc %{_docdir}/%{name}-%{version}
%doc doc/hsqldb_lic.txt

%files javadoc
%{_javadocdir}/%{name}
%doc doc/hsqldb_lic.txt

%files demo
%{_datadir}/%{name}

%changelog
* Fri Jun 28 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 1:1.8.1.3-12
- Rebuild to regenerate API documentation
- Resolves: CVE-2013-1571

* Fri May 17 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 1:1.8.1.3-11
- Fix incorrect permissions on systemd unit file
- Resolves: rhbz#963911

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:1.8.1.3-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Fri Aug 24 2012 Tomas Radej <tradej@redhat.com> - 1:1.8.1.3-9
- Switched from SysV to systemd
- Spec rearrangements

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:1.8.1.3-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Apr 6 2012 Alexander Kurtakov <akurtako@redhat.com> 1:1.8.1.3-7
- Switch to servlet 3.0 by default.

* Thu Mar 08 2012 Tomas Radej <tradej@redhat.com> - 1:1.8.1.3-6
- Fixed symlink

* Tue Jan 24 2012 Deepak Bhole <dbhole@redhat.com> - 1:1.8.1.3-5
- Added patch to support JDBC 4.1/Java 7

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:1.8.1.3-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:1.8.1.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Tue Jan 25 2011 Alexander Kurtakov <akurtako@redhat.com> 1:1.8.1.3-2
- More merge review fixes.

* Mon Jan 24 2011 Alexander Kurtakov <akurtako@redhat.com> 1:1.8.1.3-1
- Update to new upstream version.
- Fixes for the merge review.

* Wed Oct 6 2010 Alexander Kurtakov <akurtako@redhat.com> 1:1.8.0.10-6
- Update to use tomcat6 servlet implementation.

* Mon Jan 11 2010 Mary Ellen Foster <mefoster at gmail.com> - 1.8.0.10-5
- Add maven2 pom and metadata

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
- added BuildRequires: servletapi3 ant
- added Requires:      servletapi3 ant

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
