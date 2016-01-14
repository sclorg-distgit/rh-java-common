%{!?scl_name_base:%global scl_name_base rh-java-common}
%{!?scl:%global scl %{scl_name_base}}
%scl_package %scl

%global debug_package %{nil}

Name:       %scl_name
Version:    1.1
Release:    43%{?dist}
Summary:    Package that installs %scl

License:    GPLv2+
Source1:    macros.%{scl_name}
Source2:    %{scl_name}-javapackages-provides-wrapper
Source3:    %{scl_name}-javapackages-requires-wrapper
Source4:    README
Source5:    LICENSE

BuildRequires:  help2man
BuildRequires:  python-devel
BuildRequires:  scl-utils-build

%description
This is the main package for the %scl Software Collection.

%package runtime
Summary:    Package that handles %scl Software Collection.
Requires:   scl-utils
Requires:   %{name}-javapackages-tools

%description runtime
Package shipping essential scripts to work with the %scl Software Collection.

%package build
Summary:    Build support tools for the %scl Software Collection.
Requires:   scl-utils-build
Requires:   %{name}-scldevel = %{version}-%{release}

%description build
Package shipping essential configuration marcros/files in order to be able
to build %scl Software Collection.

%package scldevel
Summary:    Package shipping development files for %scl
Requires:   %{name}-runtime = %{version}-%{release}
Requires:   %{scl_prefix_maven}scldevel

%description scldevel
Package shipping development files, especially useful for development of
packages depending on %scl Software Collection.

%prep
%setup -c -T
#===================#
# SCL enable script #
#===================#
cat <<EOF >enable
# Generic variables
export PATH="%{_bindir}:\${PATH:-/bin:/usr/bin}"
export MANPATH="%{_mandir}:\${MANPATH}"
export PYTHONPATH="%{_scl_root}%{python_sitelib}\${PYTHONPATH:+:}\${PYTHONPATH:-}"

export JAVACONFDIRS="%{_sysconfdir}/java\${JAVACONFDIRS:+:}\${JAVACONFDIRS:-}"
export XDG_CONFIG_DIRS="%{_sysconfdir}/xdg\${XDG_CONFIG_DIRS:+:}\${XDG_CONFIG_DIRS:-}"
export XDG_DATA_DIRS="%{_datadir}\${XDG_DATA_DIRS:+:}\${XDG_DATA_DIRS:-}"
EOF

# Generate Eclipse configuration file
cat <<EOF >eclipse.conf
eclipse.bundles=%{_javadir},%{_jnidir}
scl.namespace=%{?scl}
scl.root=%{?_scl_root}
EOF

# This section generates README file from a template and creates man page
# from that file, expanding RPM macros in the template file.
cat >README <<'EOF'
%{expand:%(cat %{SOURCE4})}
EOF

# copy the license file so %%files section sees it
cp %{SOURCE5} .

cp %{SOURCE1} macros.%{scl_name}
cat >> macros.%{scl_name} << EOF
%%_sysconfdir_java_common %_sysconfdir
%%_prefix_java_common %_prefix
%%_exec_prefix_java_common %_exec_prefix
%%_bindir_java_common %_bindir
%%_libdir_java_common %_libdir
%%_libexecdir_java_common %_libexecdir
%%_sbindir_java_common %_sbindir
%%_sharedstatedir_java_common %_sharedstatedir
%%_datarootdir_java_common %_datarootdir
%%_datadir_java_common %_datadir
%%_includedir_java_common %_includedir
%%_infodir_java_common %_infodir
%%_mandir_java_common %_mandir
%%_localstatedir_java_common %_localstatedir
%%_initddir_java_common %_initddir
%%_javadir_java_common %_javadir
%%_jnidir_java_common %_jnidir
%%_javadocdir_java_common %_javadocdir
%%_mavenpomdir_java_common %_mavenpomdir
%%_jvmdir_java_common %_jvmdir
%%_jvmsysconfdir_java_common %_jvmsysconfdir
%%_jvmcommonsysconfdir_java_common %_jvmcommonsysconfdir
%%_jvmjardir_java_common %_jvmjardir
%%_jvmprivdir_java_common %_jvmprivdir
%%_jvmlibdir_java_common %_jvmlibdir
%%_jvmdatadir_java_common %_jvmdatadir
%%_jvmcommonlibdir_java_common %_jvmcommonlibdir
%%_jvmcommondatadir_java_common %_jvmcommondatadir
%%_javaconfdir_java_common %_javaconfdir
EOF


%build
# generate a helper script that will be used by help2man
cat >h2m_helper <<'EOF'
#!/bin/bash
[ "$1" == "--version" ] && echo "%{scl_name} %{version} Software Collection" || cat README
EOF
chmod a+x h2m_helper

# generate the man page
help2man -N --section 7 ./h2m_helper -o %{scl_name}.7
# Fix single quotes in man page.
sed -i "s/'/\\\\(aq/g" %{scl_name}.7

%install
%scl_install

install -d -m 755 %{buildroot}%{_scl_scripts}
install -p -m 755 enable %{buildroot}%{_scl_scripts}/

# install rpm magic
install -Dpm0644 macros.%{scl_name} %{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl_name_base}-scldevel
install -Dpm0755 %{SOURCE2} %{buildroot}%{_rpmconfigdir}/%{name}-javapackages-provides-wrapper
install -Dpm0755 %{SOURCE3} %{buildroot}%{_rpmconfigdir}/%{name}-javapackages-requires-wrapper

# install dirs used by some deps
install -dm0755 %{buildroot}%{_prefix}/lib/rpm
install -dm0755 %{buildroot}%{_scl_root}%{python_sitelib}

# install generated man page
mkdir -p %{buildroot}%{_mandir}/man7/
install -m 644 %{scl_name}.7 %{buildroot}%{_mandir}/man7/%{scl_name}.7

# eclipse.conf
install -m 755 -d %{buildroot}%{_javaconfdir}
install -m 644 -p eclipse.conf %{buildroot}%{_javaconfdir}/

# XMvn configuration symlink
install -m 755 -d %{buildroot}%{_sysconfdir}/xdg/xmvn
ln -s %{_datadir}/xmvn/configuration.xml %{buildroot}%{_sysconfdir}/xdg/xmvn/configuration.xml

install -m 755 -d %{buildroot}%{_mandir}/man1
install -m 755 -d %{buildroot}%{_mandir}/man7

install -m 755 -d %{buildroot}%{_javaconfdir}
install -m 755 -d %{buildroot}%{_javadir}
install -m 755 -d %{buildroot}%{_javadocdir}
install -m 755 -d %{buildroot}%{_jnidir}
install -m 755 -d %{buildroot}%{_mavenpomdir}
install -m 755 -d %{buildroot}%{_datadir}/maven-metadata
install -m 755 -d %{buildroot}%{_datadir}/xmvn

%files runtime
%doc README LICENSE
%{scl_files}
%{_prefix}/lib/python2.*
%{_prefix}/lib/rpm
%{_mandir}/man7/%{scl_name}.*
%dir %{_javaconfdir}
%dir %{_javadir}
%dir %{_javadocdir}
# %%{scl_files} macro owns all %%{_prefix}/lib subdirs/files with 555 perms
# we need to override this to prevent file conflict with javapackages-tools
%attr(755,root,root) %dir %{_jnidir}
%dir %{_mavenpomdir}
%dir %{_datadir}/maven-metadata
%dir %{_datadir}/xmvn
%{_javaconfdir}/eclipse.conf
%{_sysconfdir}/xdg
%dir %{_mandir}/man1
%dir %{_mandir}/man7

%files build
%{_root_sysconfdir}/rpm/macros.%{scl}-config

%files scldevel
%{_root_sysconfdir}/rpm/macros.%{scl_name_base}-scldevel
%{_root_prefix}/lib/rpm/%{name}-javapackages-provides-wrapper
%{_root_prefix}/lib/rpm/%{name}-javapackages-requires-wrapper

%changelog
* Tue Jul 21 2015 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.1-43
- Fix syntax errors in manpage

* Thu Jul 02 2015 Michael Simacek <msimacek@redhat.com> - 1.1-42
- Ensure 755 permissions on _jnidir

* Wed Jun 10 2015 Michal Srb <msrb@redhat.com> - 1.1-41
- Convert back to arch

* Tue Jun  9 2015 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.1-40
- Convert to noarch

* Mon Apr 27 2015 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.1-39
- Rebuild for final RHSCL 2.0 release

* Wed Feb 11 2015 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.1-38
- Be more careful when setting env variables in enable script

* Tue Feb  3 2015 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.1-37
- Add missing requirement on javapackages-tools

* Fri Jan 16 2015 Michal Srb <msrb@redhat.com> -1.1-36
- Fix README

* Fri Jan 16 2015 Michal Srb <msrb@redhat.com> - 1.1-35
- Fill the README file with some content

* Fri Jan 16 2015 Michal Srb <msrb@redhat.com> - 1.1-34
- Also own %%{_jnidir}

* Thu Jan 15 2015 Michael Simacek <msimacek@redhat.com> - 1.1-33
- Own java-related directories

* Wed Jan 14 2015 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.1-32
- Revert adding directory ownership

* Wed Jan 14 2015 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.1-31
- Add explicit directory attributes

* Wed Jan 14 2015 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.1-30
- Own directories created by other packages

* Tue Jan 13 2015 Michael Simacek <msimacek@redhat.com> - 1.1-29
- Mass rebuild 2015-01-13

* Tue Jan 13 2015 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.1-28
- Fix patterns used in req/prov wrappers

* Tue Jan 13 2015 Michael Simacek <msimacek@redhat.com>
- Generates macros for directories

* Tue Jan 13 2015 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.1-27
- Remove temporary hacks

* Mon Jan 12 2015 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.1-26
- Add temp requires on atinject and guava

* Fri Jan  9 2015 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.1-25
- Fix pattern matching in depgenerator scripts

* Fri Jan 09 2015 Michal Srb <msrb@redhat.com> - 1.1-24
- Mass rebuild 2015-01-09

* Wed Jan  7 2015 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.1-23
- Don't install -build subpackage as dependency of -scldevel

* Wed Jan  7 2015 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.1-22
- Add tepmorary requires on all rh-java-common packages

* Wed Jan  7 2015 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.1-21
- Install XMvn configuration symlink

* Mon Jan  5 2015 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.1-20
- Export RPM_BUILD_ROOT in wrapper scripts

* Fri Jan  2 2015 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.1-19
- Update wrapper scripts to current javapackages

* Fri Jan 02 2015 Michal Srb <msrb@redhat.com> - 1.1-18
- Fix invocation of RPM generators

* Wed Dec 24 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.1-17
- Disable bash -e when running scl_source

* Wed Dec 24 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.1-16
- Enable SCL prior to calling dependency generators

* Tue Dec 23 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.1-15
- Make wrapper scripts kill PPID on error

* Mon Dec 22 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.1-13
- Pass RPM_BUILD_ROOT as argument to wrapper script

* Thu Dec 18 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.1-12
- Add eclipse.conf file
- Remove temporary workaround for XMvn bug

* Wed Dec 17 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.1-11
- Add temporary workaround for XMvn bug

* Wed Dec 17 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.1-10
- Switch dependency generators from depmaps to new metadata

* Wed Dec 17 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.1-9
- Add requires on maven30-scldevel

* Wed Dec 17 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.1-8
- Drop temporary requires on maven30

* Mon Dec 15 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.1-7
- Add temp requires on maven-local

* Mon Dec 15 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.1-6
- Fix mavendepmapfragdir location in javapackages-requires-wrapper

* Mon Dec 15 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.1-5
- Fix variable escaping in enable script

* Mon Dec 15 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.1-4
- Fix %%scl_prefix_java_common macro declaration
- Fix other related macros

* Mon Dec 15 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.1-3
- Tepmorarly enable maven30 from rh-java-common enable script

* Mon Dec 15 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.1-2
- Add temporary requires on maven30-scldevel

* Mon Dec 15 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.1-1
- Initial packaging
