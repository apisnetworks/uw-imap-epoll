
# Fedora review: http://bugzilla.redhat.com/166008

%if 0%{?fedora} || 0%{?rhel} != 6
%define _with_devel 1
# ship static lib, matches default upstream config
# as convenience to users, since our hacked shlib can potentially break 
# abi semi-often
%define _with_static 1
%endif

%if 0%{?rhel} == 6
%define _with_system_libc_client 1
%endif

Summary: UW Server daemons for IMAP and POP network mail protocols
Name:	 uw-imap 
Version: 2007f
Release: 4%{?dist}.1

# See LICENSE.txt, http://www.apache.org/licenses/LICENSE-2.0
License: ASL 2.0 
Group: 	 System Environment/Daemons
URL:	 http://www.washington.edu/imap/
# Old (non-latest) releases live at  ftp://ftp.cac.washington.edu/imap/old/
Source0: ftp://ftp.cac.washington.edu/imap/imap-%{version}%{?beta}%{?dev}%{?snap}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%define soname    c-client
#define somajor   %{version} 
%define somajor   2007
%define shlibname lib%{soname}.so.%{somajor}
%if 0%{?fedora} > 2 || 0%{?rhel} > 5
%define imap_libs lib%{soname}
%else
# rhel (4,5) requires parallel-installable shlib, to not conflict with 
# os-provided libc-client
%define imap_libs lib%{soname}%{somajor}
%endif

# FC4+ uses %%_sysconfdir/pki/tls, previous releases used %%_datadir/ssl
%global ssldir  %(if [ -d %{_sysconfdir}/pki/tls ]; then echo "%{_sysconfdir}/pki/tls"; else echo "%{_datadir}/ssl"; fi)

# imap -> uw-imap rename
Obsoletes: imap < 1:%{version}

# newest pam setup, using password-auth common PAM
Source20: imap-password.pam
# new pam setup, using new "include" feature
Source21: imap.pam
# legacy/old pam setup, using pam_stack.so
Source22: imap-legacy.pam

Patch1: imap-2007-paths.patch
# See http://bugzilla.redhat.com/229781 , http://bugzilla.redhat.com/127271
Patch2: imap-2004a-doc.patch
Patch5: imap-2007e-overflow.patch
Patch9: imap-2007e-shared.patch
Patch10: imap-2007e-authmd5.patch
Patch11: imap-2007e-system_c_client.patch
Patch12: imap-2007e-epoll.patch
Patch13: 1006_openssl1.1_autoverify.patch
Patch14: imap-2007f-format-security.patch

BuildRequires: krb5-devel
BuildRequires: openssl-devel
BuildRequires: pam-devel

Requires(post): openssl

%if 0%{?_with_system_libc_client}
BuildRequires: libc-client-devel = %{version}
Requires: %{imap_libs}%{?_isa} = %{version}
%else
Requires: %{imap_libs}%{?_isa} = %{version}-%{release}
%endif

%description
The %{name} package provides UW server daemons for both the IMAP (Internet
Message Access Protocol) and POP (Post Office Protocol) mail access
protocols.  The POP protocol uses a "post office" machine to collect
mail for users and allows users to download their mail to their local
machine for reading. The IMAP protocol allows a user to read mail on a
remote machine without downloading it to their local machine.

%package -n %{imap_libs} 
Summary: UW C-client mail library 
Group:	 System Environment/Libraries
Obsoletes: libc-client2004d < 1:2004d-2
Obsoletes: libc-client2004e < 2004e-2
Obsoletes: libc-client2004g < 2004g-7
Obsoletes: libc-client2006 < 2006k-2
%if "%{imap_libs}" != "libc-client2007"
Obsoletes: libc-client2007 < 2007-2
%endif
%description -n %{imap_libs} 
Provides a common API for accessing mailboxes. 

%package devel
Summary: Development tools for programs which will use the UW IMAP library
Group: 	 Development/Libraries
Requires: %{imap_libs}%{?_isa} = %{version}-%{release}
# imap -> uw-imap rename
Obsoletes: imap-devel < 1:%{version}
%if "%{imap_libs}" == "libc-client"
Obsoletes: libc-client-devel < %{version}-%{release}
Provides:  libc-client-devel = %{version}-%{release}
%else
Conflicts: libc-client-devel < %{version}-%{release}
%endif
%description devel
Contains the header files and libraries for developing programs 
which will use the UW C-client common API.

%package static 
Summary: UW IMAP static library
Group:   Development/Libraries
Requires: %{name}-devel = %{version}-%{release}
#Provides: libc-client-static = %{version}-%{release}
Requires: krb5-devel openssl-devel pam-devel
%description static 
Contains static libraries for developing programs 
which will use the UW C-client common API.

%package utils
Summary: UW IMAP Utilities to make managing your email simpler
Group: 	 Applications/System 
%if ! 0%{?_with_system_libc_client}
Requires: %{imap_libs}%{?_isa} = %{version}-%{release}
%endif
# imap -> uw-imap rename
Obsoletes: imap-utils < 1:%{version}
%description utils
This package contains some utilities for managing UW IMAP email,including:
* dmail : procmail Mail Delivery Module
* mailutil : mail utility program
* mtest : C client test program
* tmail : Mail Delivery Module
* mlock



%prep
%setup -q -n imap-%{version}%{?dev}%{?snap}

%patch1 -p1 -b .paths
%patch2 -p1 -b .doc

%patch5 -p1 -b .overflow

%patch9 -p1 -b .shared
%patch10 -p1 -b .authmd5
%patch12 -p1 -b .epoll
%patch13 -p1 -b .ssl
%patch14 -p1 -b .security

%if 0%{?fedora} > 11 || 0%{?rhel} > 5
install -p -m644 %{SOURCE20} imap.pam
%else 
%if 0%{?fedora} > 4 || 0%{?rhel} > 4
install -p -m644 %{SOURCE21} imap.pam
%else
install -p -m644 %{SOURCE22} imap.pam
%endif
%endif

%if 0%{?_with_system_libc_client}
%patch11 -p1 -b .system_c_client
%endif


%build

# Kerberos setup
test -f %{_sysconfdir}/profile.d/krb5-devel.sh && source %{_sysconfdir}/profile.d/krb5-devel.sh
test -f %{_sysconfdir}/profile.d/krb5.sh && source %{_sysconfdir}/profile.d/krb5.sh
GSSDIR=$(krb5-config --prefix)

# SSL setup, probably legacy-only, but shouldn't hurt -- Rex
export EXTRACFLAGS="$EXTRACFLAGS $(pkg-config --cflags openssl 2>/dev/null)"
# $RPM_OPT_FLAGS
export EXTRACFLAGS="$EXTRACFLAGS -fPIC $RPM_OPT_FLAGS"
# jorton added these, I'll assume he knows what he's doing. :) -- Rex
export EXTRACFLAGS="$EXTRACFLAGS -fno-strict-aliasing"
%if 0%{?fedora} > 4 || 0%{?rhel} > 4
export EXTRACFLAGS="$EXTRACFLAGS -Wno-pointer-sign"
%endif

echo -e "y\ny" | \
make %{?_smp_mflags} lnp \
IP=6 \
EXTRACFLAGS="$EXTRACFLAGS" \
EXTRALDFLAGS="$EXTRALDFLAGS" \
EXTRAAUTHENTICATORS=gss \
SPECIALS="GSSDIR=${GSSDIR} LOCKPGM=%{_sbindir}/mlock SSLCERTS=%{ssldir}/certs SSLDIR=%{ssldir} SSLINCLUDE=%{_includedir}/openssl SSLKEYS=%{ssldir}/private SSLLIB=%{_libdir}" \
SSLTYPE=unix \
%if 0%{?_with_system_libc_client}
CCLIENTLIB=%{_libdir}/%{shlibname} \
%else
CCLIENTLIB=$(pwd)/c-client/%{shlibname} \
%endif
SHLIBBASE=%{soname} \
SHLIBNAME=%{shlibname} \
%if 0%{?_with_system_libc_client}
%endif
# Blank line


%install
rm -rf $RPM_BUILD_ROOT

mkdir -p $RPM_BUILD_ROOT%{_libdir}/

%if ! 0%{?_with_system_libc_client}
%if 0%{?_with_static:1}
install -p -m644 ./c-client/c-client.a $RPM_BUILD_ROOT%{_libdir}/
ln -s c-client.a $RPM_BUILD_ROOT%{_libdir}/libc-client.a
%endif

install -p -m755 ./c-client/%{shlibname} $RPM_BUILD_ROOT%{_libdir}/

# %%ghost'd c-client.cf
touch c-client.cf
install -p -m644 -D c-client.cf $RPM_BUILD_ROOT%{_sysconfdir}/c-client.cf
%endif

%if 0%{?_with_devel:1}
ln -s %{shlibname} $RPM_BUILD_ROOT%{_libdir}/lib%{soname}.so

mkdir -p $RPM_BUILD_ROOT%{_includedir}/imap/
install -m644 ./c-client/*.h $RPM_BUILD_ROOT%{_includedir}/imap/
# Added linkage.c to fix (#34658) <mharris>
install -m644 ./c-client/linkage.c $RPM_BUILD_ROOT%{_includedir}/imap/
install -m644 ./src/osdep/tops-20/shortsym.h $RPM_BUILD_ROOT%{_includedir}/imap/
%endif

install -p -D -m644 src/imapd/imapd.8 $RPM_BUILD_ROOT%{_mandir}/man8/imapd.8uw
install -p -D -m644 src/ipopd/ipopd.8 $RPM_BUILD_ROOT%{_mandir}/man8/ipopd.8uw

mkdir -p $RPM_BUILD_ROOT%{_sbindir}
install -p -m755 ipopd/ipop{2d,3d} $RPM_BUILD_ROOT%{_sbindir}/
install -p -m755 imapd/imapd $RPM_BUILD_ROOT%{_sbindir}/
install -p -m755 mlock/mlock $RPM_BUILD_ROOT%{_sbindir}/

mkdir -p $RPM_BUILD_ROOT%{_bindir}/
install -p -m755 dmail/dmail mailutil/mailutil mtest/mtest tmail/tmail $RPM_BUILD_ROOT%{_bindir}/
mkdir -p $RPM_BUILD_ROOT%{_mandir}/man1/
install -p -m644 src/{dmail/dmail,mailutil/mailutil,tmail/tmail}.1 $RPM_BUILD_ROOT%{_mandir}/man1/

install -p -m644 -D imap.pam $RPM_BUILD_ROOT%{_sysconfdir}/pam.d/imap
install -p -m644 -D imap.pam $RPM_BUILD_ROOT%{_sysconfdir}/pam.d/pop

# %ghost'd *.pem files
mkdir -p $RPM_BUILD_ROOT%{ssldir}/certs
touch $RPM_BUILD_ROOT%{ssldir}/certs/{imapd,ipop3d}.pem


# FIXME, do on first launch (or not at all?), not here -- Rex
%post
{
cd %{ssldir}/certs &> /dev/null || :
for CERT in imapd.pem ipop3d.pem ;do
   if [ ! -e $CERT ];then
      if [ -e stunnel.pem ];then
         cp stunnel.pem $CERT &> /dev/null || :
      elif [ -e Makefile ];then
         make $CERT << EOF &> /dev/null || :
--
SomeState
SomeCity
SomeOrganization
SomeOrganizationalUnit
localhost.localdomain
root@localhost.localdomain
EOF
      fi
   fi
done
} || :
/sbin/service xinetd reload > /dev/null 2>&1 || :

%postun
/sbin/service xinetd reload > /dev/null 2>&1 || :

%post -n %{imap_libs} -p /sbin/ldconfig

%postun -n %{imap_libs} -p /sbin/ldconfig


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc docs/SSLBUILD
%config(noreplace) %{_sysconfdir}/pam.d/imap
%config(noreplace) %{_sysconfdir}/pam.d/pop
# These need to be replaced (ie, can't use %%noreplace), or imaps/pop3s can fail on upgrade
# do this in a %trigger or something not here... -- Rex
%attr(0600,root,root) %ghost %config(missingok,noreplace) %verify(not md5 size mtime) %{ssldir}/certs/imapd.pem
%attr(0600,root,root) %ghost %config(missingok,noreplace) %verify(not md5 size mtime) %{ssldir}/certs/ipop3d.pem
%{_mandir}/man8/*
%{_sbindir}/ipop2d
%{_sbindir}/ipop3d
%{_sbindir}/imapd

%files utils
%defattr(-,root,root,-)
%{_bindir}/*
%attr(2755, root, mail) %{_sbindir}/mlock
%{_mandir}/man1/*

%if ! 0%{?_with_system_libc_client}
%files -n %{imap_libs} 
%defattr(-,root,root)
%doc LICENSE.txt NOTICE SUPPORT 
%doc docs/RELNOTES docs/*.txt
%ghost %config(missingok,noreplace) %{_sysconfdir}/c-client.cf
%{_libdir}/lib%{soname}.so.*
%endif

%if 0%{?_with_devel:1}
%files devel
%defattr(-,root,root,-)
%{_includedir}/imap/
%{_libdir}/lib%{soname}.so
%endif

%if 0%{?_with_static:1}
%files static
%defattr(-,root,root,-)
%{_libdir}/c-client.a
%{_libdir}/libc-client.a
%endif


%changelog
* Tue Jan 14 2014 Remi Collet <remi@fedoraproject.org> - 2007f-4.1
- EPEL-7 build (RHEL-7 don't have libc-client)

* Fri Feb 15 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2007f-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Sun Jul 22 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2007f-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2007f-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Aug 02 2011 Rex Dieter <rdieter@fedoraproject.org> 2007f-1
- imap-2007f

* Mon Jun 13 2011 Rex Dieter <rdieter@fedoraproject.org> 2007e-13
- _with_system_libc_client option (el6+) 
- tight deps via %%?_isa
- drop extraneous Requires(post,postun): xinetd

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2007e-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Tue Apr 27 2010 Rex Dieter <rdieter@fedoraproject.org> - 2007e-11
- SSL connection through IPv6 fails (#485860)
- fix SSLDIR, set SSLKEYS

* Wed Sep 16 2009 Tomas Mraz <tmraz@redhat.com> - 2007e-10
- use password-auth common PAM configuration instead of system-auth
  where available

* Mon Aug 31 2009 Rex Dieter <rdieter@fedoraproject.org> 
- omit -devel, -static bits in EPEL builds (#518885)

* Fri Aug 21 2009 Tomas Mraz <tmraz@redhat.com> - 2007e-9
- rebuilt with new openssl

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2007e-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Jul 08 2009 Rex Dieter <rdieter@fedoraproject.org> - 2007e-7
- fix shared.patch to use CFLAGS for osdep.c too

* Tue Jul 07 2009 Rex Dieter <rdieter@fedoraproject.org> - 2007e-6
- build with -fPIC
- rebase patches (patch fuzz=0)

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2007e-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sun Jan 18 2009 Tomas Mraz <tmraz@redhat.com> 2007e-4
- rebuild with new openssl

* Mon Jan 12 2009 Rex Dieter <rdieter@fedoraproject.org> 2007e-3
- main/-utils: +Req: %%imap_libs = %%version-%%release

* Fri Dec 19 2008 Rex Dieter <rdieter@fedoraproject.org> 2007e-1
- imap-2007e

* Fri Oct 31 2008 Rex Dieter <rdieter@fedoraproject.org> 2007d-1
- imap-2007d

* Wed Oct 01 2008 Rex Dieter <rdieter@fedoraproject.org> 2007b-2
- fix build (patch fuzz) (#464985)

* Fri Jun 13 2008 Rex Dieter <rdieter@fedoraproject.org> 2007b-1
- imap-2007b

* Tue May 18 2008 Rex Dieter <rdieter@fedoraproject.org> 2007a1-3
- libc-client: incomplete list of obsoletes (#446240)

* Wed Mar 19 2008 Rex Dieter <rdieter@fedoraproject.org> 2007a1-2
- uw-imap conflicts with cyrus-imapd (#222486)

* Wed Mar 19 2008 Rex Dieter <rdieter@fedoraproject.org> 2007a1-1
- imap-2007a1
- include static lib
- utils: update %%description

* Thu Mar 13 2008 Rex Dieter <rdieter@fedoraproject.org> 2007a-1
- imap-2007a

* Fri Feb 08 2008 Rex Dieter <rdieter@fedoraproject.org> 2007-3 
- respin (gcc43)

* Wed Jan 23 2008 Rex Dieter <rdieter@fedoraproject.org> 2007-2
- Obsoletes: libc-client2006 (#429796)
- drop libc-client hacks for parallel-installability, fun while it lasted

* Fri Dec 21 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2007-1
- imap-2007

* Tue Dec 04 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2006k-2
- respin for new openssl

* Fri Nov 09 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2006k-1
- imap-2006k (final)

* Wed Sep 19 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2006k-0.1.0709171900
- imap-2006k.DEV.SNAP-0709171900

* Tue Aug 21 2007 Joe Orton <jorton@redhat.com> 2006j-3
- fix License

* Tue Jul 17 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2006j-2
- imap-2006j2

* Mon Jul 09 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2006j-1
- imap-2006j1

* Wed Jun 13 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2006i-1
- imap-2006i

* Wed May 09 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2006h-1
- imap-2006h
- Obsolete pre-merge libc-client pkgs

* Fri Apr 27 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2006g-3
- imap-2004a-doc.patch (#229781,#127271)

* Mon Apr  2 2007 Joe Orton <jorton@redhat.com> 2006g-2
- use $RPM_OPT_FLAGS during build

* Mon Apr 02 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2006g-1
- imap-2006g

* Wed Feb 07 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2006e-3
- Obsoletes: libc-client2004g
- cleanup/simplify c-client.cf handling

* Fri Jan 26 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2006e-2
- use /etc/profile.d/krb5-devel.sh

* Fri Jan 26 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2006e-1
- imap-2006e

* Mon Dec 18 2006 Rex Dieter <rdieter[AT]fedoraproject.org> 2006d-1
- imap-2006d (#220121)

* Wed Oct 25 2006 Rex Dieter <rexdieter[AT]users.sf.net> 2006c1-1
- imap-2006c1

* Fri Oct 06 2006 Rex Dieter <rexdieter[AT]users.sf.net> 2006b-1
- imap-2006b
- %%ghost %%config(missingok,noreplace) %%{_sysconfdir}/c-client.cf

* Fri Oct 06 2006 Rex Dieter <rexdieter[AT]users.sf.net> 2006a-6
- omit EOL whitespace from c-client.cf

* Thu Oct 05 2006 Rex Dieter <rexdieter[AT]users.sf.net> 2006a-5
- %%config(noreplace) all xinetd.d/pam.d bits

* Thu Oct 05 2006 Rex Dieter <rexdieter[AT]users.sf.net> 2006a-4
- eek, pam.d/xinet.d bits were all mixed up, fixed.

* Wed Oct 04 2006 Rex Dieter <rexdieter[AT]users.sf.net> 2006a-3
- libc-client: move c-client.cf here
- c-client.cf: +set new-folder-format same-as-inbox

* Wed Oct 04 2006 Rex Dieter <rexdieter[AT]users.sf.net> 2006a-2
- omit mixproto patch (lvn bug #1184)

* Tue Sep 26 2006 Rex Dieter <rexdieter[AT]users.sf.net> 2006a-1
- imap-2006a
- omit static lib (for now, at least)

* Mon Sep 25 2006 Rex Dieter <rexdieter[AT]users.sf.net> 2006-4
- -devel-static: package static lib separately. 

* Mon Sep 25 2006 Rex Dieter <rexdieter[AT]users.sf.net> 2006-3
- License: Apache 2.0

* Fri Sep 15 2006 Rex Dieter <rexdieter[AT]users.sf.net> 2006-2
- imap-2006
- change default (CREATEPROTO) driver to mix
- Obsolete old libc-clients

* Tue Aug 29 2006 Rex Dieter <rexdieter[AT]users.sf.net> 2004g-6 
- fc6 respin

* Fri Aug 18 2006 Rex Dieter <rexdieter[AT]users.sf.net> 2004g-5
- cleanup, respin for fc6

* Wed Mar 1 2006 Rex Dieter <rexdieter[AT]users.sf.net> 
- fc5: gcc/glibc respin

* Thu Nov 17 2005 Rex Dieter <rexdieter[AT]users.sf.net> 2004g-4
- use pam's "include" feature on fc5
- cleanup %%doc handling, remove useless bits

* Thu Nov 17 2005 Rex Dieter <rexdieter[AT]users.sf.net> 2004g-3
- omit trailing whitespace in default c-client.cf

* Wed Nov 16 2005 Rex Dieter <rexdieter[AT]users.sf.net> 2004g-2 
- rebuild for new openssl

* Mon Sep 26 2005 Rex Dieter <rexdieter[AT]users.sf.net> 2004g-1
- imap-2004g
- /etc -> %%_sysconfdir
- use %%{?_smp_mflags}

* Mon Aug 15 2005 Rex Dieter <rexdieter[AT]users.sf.net> 2004e-1
- imap-2004e
- rename: imap -> uw-imap (yay, we get to drop the Epoch)
- sslcerts=%%{_sysconfdir}/pki/tls/certs if exists, else /usr/share/ssl/certs

* Fri Apr 29 2005 Rex Dieter <rexdieter[AT]users.sf.net> 1:2004d-1
- 2004d
- imap-libs -> lib%%{soname}%%{version} (ie, libc-client2004d), so we can 
  have multiple versions (shared-lib only) installed
- move mlock to -utils.
- revert RFC2301, locks out too many folks where SSL is unavailable

* Thu Apr 28 2005 Rex Dieter <rexdieter[AT]users.sf.net> 1:2004-0.fdr.11.c1
- change default driver from mbox to mbx
- comply with RFC 3501 security: Unencrypted plaintext passwords are prohibited

* Fri Jan 28 2005 Rex Dieter <rexdieter[AT]users.sf.net> 1:2004-0.fdr.10.c1
- imap-2004c1 security release:
  http://www.kb.cert.org/vuls/id/702777

* Thu Jan 20 2005 Rex Dieter <rexdieter[AT]users.sf.net> 1:2004-0.fdr.9.c
- imap2004c
- -utils: dmail,mailutil,tmail
- -libs: include mlock (so it's available for other imap clients, like pine)
- remove extraneous patches
- %%_sysconfigdir/c-client.cf: use to set MailDir (but don't if upgrading from
  an older version (ie, if folks don't want/expect a change in behavior)

* Mon Sep 13 2004 Rex Dieter <rexdieter at sf.net. 1:2004-0.fdr.8.a
- don't use mailsubdir patch (for now)

* Wed Aug 11 2004 Rex Dieter <rexdieter at sf.net> 1:2004-0.fdr.7.a
- mailsubdir patch (default to ~/Mail instead of ~)

* Fri Jul 23 2004 Rex Dieter <rexdieter at sf.net> 1:2004-0.fdr.6.a
- remove Obsoletes/Provides: libc-client (they can, in fact, co-xist)
- -devel: remove O/P: libc-client-devel -> Conflicts: libc-client-devel

* Thu Jul 16 2004 Rex Dieter <rexdieter at sf.net> 1:2004-0.fdr.5.a
- imap2004a

* Tue Jul 13 2004 Rex Dieter <rexdieter at sf.net> 1:2004-0.fdr.4
- -devel: Req: %%{name}-libs

* Tue Jul 13 2004 Rex Dieter <rexdieter at sf.net> 1:2004-0.fdr.3
- previous imap pkgs had Epoch: 1, we need it too.

* Wed Jul 07 2004 Rex Dieter <rexdieter at sf.net> 2004-0.fdr.2
- use %%version as %%somajver (like how openssl does it)

* Wed Jul 07 2004 Rex Dieter <rexdieter at sf.net> 2004-0.fdr.1
- imap-2004
- use mlock, if available.
- Since libc-client is an attrocious name choice, we'll trump it, 
  and provide imap, imap-libs, imap-devel instead (redhat bug #120873)

* Wed Apr 07 2004 Kaj J. Niemi <kajtzu@fi.basen.net> 2002e-4
- Use CFLAGS (and RPM_OPT_FLAGS) during the compilation
- Build the .so through gcc instead of directly calling ld 

* Fri Mar  5 2004 Joe Orton <jorton@redhat.com> 2002e-3
- install .so with permissions 0755
- make auth_md5.c functions static to avoid symbol conflicts
- remove Epoch: 0

* Tue Mar 02 2004 Kaj J. Niemi <kajtzu@fi.basen.net> 0:2002e-2
- "lnp" already uses RPM_OPT_FLAGS
- have us conflict with imap, imap-devel

* Tue Mar  2 2004 Joe Orton <jorton@redhat.com> 0:2002e-1
- add post/postun, always use -fPIC

* Tue Feb 24 2004 Kaj J. Niemi <kajtzu@fi.basen.net>
- Name change from c-client to libc-client

* Sat Feb 14 2004 Kaj J. Niemi <kajtzu@fi.basen.net> 0:2002e-0.1
- c-client 2002e is based on imap-2002d
- Build shared version, build logic is copied from FreeBSD net/cclient

