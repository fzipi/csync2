# csync2 - cluster synchronization tool, 2nd generation
# Copyright (C) 2004 - 2015 LINBIT Information Technologies GmbH
# http://www.linbit.com; see also AUTHORS
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

#
# spec file for package csync2 (Version 2.0)
#

# norootforbuild
# neededforbuild  openssl openssl-devel
%global with_systemd 0%{?fedora} || 0%{?rhel} > 6

BuildRequires: autoconf
BuildRequires: automake
BuildRequires: bison
BuildRequires: byacc
BuildRequires: flex
BuildRequires: openssl
BuildRequires: sqlite librsync gnutls-devel librsync-devel
BuildRequires: mysql-devel postgresql-devel
# Workarround for EL6
%if 0%{?el6}
BuildRequires: sqlite2-devel
%else
BuildRequires: sqlite-devel
%endif


Name:        csync2
License:     GPL
Group:       System/Monitoring
Requires:    sqlite openssl librsync
Autoreqprov: on
Version:     2.0
Release:     1%{?dist}
Source0:     http://oss.linbit.com/csync2/%{name}-%{version}.tar.gz
Source1:     %{name}.service
URL:         http://oss.linbit.com/csync2
BuildRoot:   %{_tmppath}/%{name}-%{version}-build
Summary:     Cluster sync tool

%description
Csync2 is a cluster synchronization tool. It can be used to keep files on 
multiple hosts in a cluster in sync. Csync2 can handle complex setups with 
much more than just 2 hosts, handle file deletions and can detect conflicts.
It is expedient for HA-clusters, HPC-clusters, COWs and server farms. 

%prep
%setup -q
%{?suse_update_config:%{suse_update_config}}

%build
export CFLAGS="$RPM_OPT_FLAGS -I/usr/kerberos/include"
if ! [ -f configure ]; then ./autogen.sh; fi
%configure --sysconfdir=%{_sysconfdir}/%{name} \
	   --enable-mysql \
	   --enable-postgres \
	   --enable-sqlite3

make %{?_smp_flags}

%install
rm -rf %{buildroot}
%{make_install}
%{__mkdir_p} %{buildroot}%{_var}/lib/%{name}
%if %with_systemd
%{__mkdir_p} %{buildroot}%{_unitdir}
%else
%{__mkdir_p} %{buildroot}%{_sysconfdir}/xinetd.d
%endif

%if %with_systemd
%{__install} -D -p -m 0755 %{SOURCE1} %{buildroot}%{_unitdir}/%{name}.service
%else
%{__install} -m 644 csync2.xinetd %{buildroot}%{_sysconfdir}/xinetd.d/csync2
%endif
%{__install} -m 644 doc/csync2_paper.pdf %{buildroot}%{_docdir}/%{name}/csync2_paper.pdf
%{__install} -m 644 csync2.cfg %{buildroot}%{_sysconfdir}/%{name}

%clean
rm -rf %{buildroot}

%post
%if %with_systemd
# add systemd service
%systemd_post %{name}.service
%else
if ! grep -q "^csync2" %{_sysconfdir}/services ; then
echo "csync2          30865/tcp" >>%{_sysconfdir}/services
fi
%endif

%preun
# Cleanup all databases upon last removal
if [ $1 -eq 0 ]; then
%{__rm} -f %{_var}/lib/csync2/*
fi

%if %with_systemd
%systemd_preun %{name}.service
%endif


%files
%defattr(-,root,root)
%dir %{_sysconfdir}/%{name}/
%{_sbindir}/csync2
%{_sbindir}/csync2-compare
%{_var}/lib/csync2
%doc %{_mandir}/man1/csync2.1.gz
%doc %{_docdir}/csync2/csync2_paper.pdf
%doc %{_docdir}/csync2/ChangeLog
%doc %{_docdir}/csync2/README
%doc %{_docdir}/csync2/AUTHORS
%if %with_systemd
%attr(750,root,root) %{_unitdir}/%{name}.service
%else
%config(noreplace) %{_sysconfdir}/xinetd.d/csync2
%endif
%config(noreplace) %{_sysconfdir}/%{name}/csync2.cfg

%changelog
* Thu Apr 13 2017 Felipe Zipitria <fzipi@fing.edu.uy> - 2.0-2
- Added systemd unit service
- Removed xinetd dependency

* Tue Jan 27 2015 Lars Ellenberg <lars.ellenberg@linbit.com> - 2.0-1
- New upstream release
