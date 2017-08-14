%global origname docker

# moby
%global git_moby https://github.com/moby/moby
%global commit_moby f34e4d295d5c17a78c33beb14b65e5d001c16968
%global shortcommit_moby %(c=%{commit_moby}; echo ${c:0:7})

# cli
%global git_cli https://github.com/%{origname}/cli
%global commit_cli 4b61f560b5b0812fcebbe320a98baac9408a5dd4
%global shortcommit_cli %(c=%{commit_cli}; echo ${c:0:7})

# docker-runc
%global git_runc https://github.com/%{origname}/runc
%global commit_runc 2d41c047c83e09a6d61d464906feb2a2f3c52aa4
%global shortcommit_runc %(c=%{commit_runc}; echo ${c:0:7})

# docker-containerd
%global git_containerd https://github.com/containerd/containerd
%global commit_containerd 3addd840653146c90a254301d6c3a663c7fd6429
%global shortcommit_containerd %(c=%{commit_containerd}; echo ${c:0:7})

# docker-proxy / libnetwork
%global git_libnetwork https://github.com/%{origname}/libnetwork
%global commit_libnetwork 7b2b1feb1de4817d522cc372af149ff48d25028e
%global shortcommit_libnetwork %(c=%{commit_libnetwork}; echo ${c:0:7})

# tini
%global git_tini https://github.com/krallin/tini
%global commit_tini 949e6facb77383876aeff8a6944dde66b3089574
%global shortcommit_tini %(c=%{commit_tini}; echo ${c:0:7})

Name: moby
Version: 17.06.0
Release: 1.git%{shortcommit_moby}%{?dist}
Summary: The open-source application container engine
License: ASL 2.0
# no golang / go-md2man for ppc64
ExcludeArch: ppc64
Source0: %{git_moby}/archive/%{commit_moby}/moby-%{shortcommit_moby}.tar.gz
Source1: %{git_cli}/archive/%{commit_cli}/cli-%{shortcommit_cli}.tar.gz
Source2: %{git_runc}/archive/%{commit_runc}/runc-%{shortcommit_runc}.tar.gz
Source3: %{git_containerd}/archive/%{commit_containerd}/containerd-%{shortcommit_containerd}.tar.gz
Source4: %{git_libnetwork}/archive/%{commit_libnetwork}/libnetwork-%{shortcommit_libnetwork}.tar.gz
Source5: %{git_tini}/archive/%{commit_tini}/tini-%{shortcommit_tini}.tar.gz
Source6: %{origname}.service
Source7: %{origname}-containerd.service
URL: https://www.%{origname}.com

# DWZ problem with multiple golang binary, see bug
# https://bugzilla.redhat.com/show_bug.cgi?id=995136#c12
%global _dwz_low_mem_die_limit 0

BuildRequires: libtool-ltdl-devel
BuildRequires: pkgconfig(systemd)
BuildRequires: git
BuildRequires: sed
BuildRequires: cmake
BuildRequires: glibc-static
BuildRequires: gpgme-devel
BuildRequires: libassuan-devel
BuildRequires: %{?go_compiler:compiler(go-compiler)}%{!?go_compiler:golang >= 1.6.2}
BuildRequires: go-md2man
BuildRequires: device-mapper-devel
%if 0%{?fedora}
BuildRequires: godep
BuildRequires: libseccomp-static >= 2.3.0
%else %if 0%{?centos}
BuildRequires: libseccomp-devel
%endif
BuildRequires: pkgconfig(audit)
BuildRequires: btrfs-progs-devel
BuildRequires: sqlite-devel
BuildRequires: pkgconfig(systemd)

# required packages on install
Requires: container-selinux >= 2.9
Requires: iptables
Requires: libcgroup
Requires: systemd-units
Requires: tar
Requires: xz

# Resolves: rhbz#1165615
Requires: device-mapper-libs >= 1.02.90-1

# conflicting packages
Conflicts: %{origname}
Conflicts: %{origname}-io
Conflicts: %{origname}-engine-cs
Conflicts: %{origname}-ee

# Obsolete packages
Obsoletes: %{origname}-ce-selinux
Obsoletes: %{origname}-engine-selinux
Obsoletes: %{origname}-engine

# use rhel-push-plugin subpackage from "docker"
Requires: %{origname}-rhel-push-plugin

# use atomic-registries subpackage for registry configuration
Requires: atomic-registries

%description
Docker is an open source project to build, ship and run any application as a
lightweight container.

Docker containers are both hardware-agnostic and platform-agnostic. This means
they can run anywhere, from your laptop to the largest EC2 compute instance and
everything in between - and they don't require you to use a particular
language, framework or packaging system. That makes them great building blocks
for deploying and scaling web apps, databases, and backend services without
depending on a particular stack or provider.

%package fish-completion
Summary: fish completion files for Docker
Requires: %{name} = %{version}-%{release}
Requires: fish
Conflicts: %{origname}-fish-completion

%description fish-completion
This package installs %{summary}.

%package vim
Summary: vim syntax highlighting files for Moby
Requires: %{name} = %{version}-%{release}
Requires: vim
Conflicts: %{origname}-vim

%description vim
This package installs %{summary}.

%package zsh-completion
Summary: zsh completion files for Moby
Requires: %{name} = %{version}-%{release}
Requires: zsh
Conflicts: %{origname}-zsh-completion

%description zsh-completion
This package installs %{summary}.

%package nano
Summary: nano syntax highlighting files for Moby
Requires: %{name} = %{version}-%{release}
Requires: nano

%description nano
This package installs %{summary}.

%prep
%autosetup -Sgit -n %{name}-%{commit_moby}

# untar cli
tar zxf %{SOURCE1}

# untar runc
tar zxf %{SOURCE2}

# untar containerd
tar zxf %{SOURCE3}

# untar libnetwork
tar zxf %{SOURCE4}

# untar tini
tar zxf %{SOURCE5}

%build
mkdir _build
pushd _build
mkdir -p $(pwd)/src/github.com/%{origname}
ln -s $(dirs +1 -l) src/github.com/%{origname}/%{name}
ln -s $(dirs +1 -l) src/github.com/%{origname}/%{origname}
popd

# build %{origname}-runc
pushd runc-%{commit_runc}
mv vendor src
mkdir -p src/github.com/opencontainers
ln -s $(pwd) src/github.com/opencontainers/runc
#sed -i 's/go build -i/go build/g' Makefile
GOPATH=$(pwd) make BUILDTAGS="seccomp selinux"
popd

# build %{origname}-containerd
pushd containerd-%{commit_containerd}
mkdir -p src/github.com/containerd
ln -s $(pwd) src/github.com/containerd/containerd
GOPATH=$(pwd) make
popd

# build %{origname}-proxy / libnetwork
pushd libnetwork-%{commit_libnetwork}
mkdir -p src/github.com/%{origname}
ln -s $(pwd) src/github.com/%{origname}/libnetwork
GOPATH=$(pwd) go build -ldflags="-linkmode=external" -o %{origname}-proxy github.com/%{origname}/libnetwork/cmd/proxy
popd

# build tini
pushd tini-%{commit_tini}
cmake .
make tini-static
popd

#GOPATH=$(pwd) RUNC_BUILDTAGS="seccomp selinux" hack/%{origname}file/install-binaries.sh
export DOCKER_GITCOMMIT=%{shortcommit_moby}
export DOCKER_BUILDTAGS="seccomp selinux"
DOCKER_DEBUG=1 GOPATH=$(pwd)/_build:$(pwd)/vendor:%{gopath} bash -x hack/make.sh dynbinary
#rm -rf bundles/latest/dynbinary-daemon/*.{md5,sha256}

pushd cli-%{commit_cli}
mkdir -p src/github.com/%{origname}/cli
ln -s $(pwd)/* src/github.com/%{origname}/cli
export GOPATH=%{gopath}:$(pwd)
make VERSION=$(cat VERSION) GITCOMMIT=%{shortcommit_cli} dynbinary # cli
./man/md2man-all.sh
popd

%check
#cli/build/%{origname} -v
#engine/bundles/%{_origversion}/dynbinary-daemon/%{origname}d -v

%install
install -dp %{buildroot}%{_bindir}
install -dp %{buildroot}%{_libexecdir}/%{name}

# install binary
install -p -m 755 cli-%{commit_cli}/build/%{origname} %{buildroot}%{_bindir}/%{origname}
install -p -m 755 bundles/latest/dynbinary-daemon/%{origname}d %{buildroot}%{_bindir}/%{origname}d

# install proxy
install -p -m 755 libnetwork-%{commit_libnetwork}/%{origname}-proxy %{buildroot}%{_libexecdir}/%{name}/%{origname}-proxy

# install containerd
install -p -m 755 containerd-%{commit_containerd}/bin/containerd %{buildroot}%{_libexecdir}/%{name}/%{origname}-containerd
install -p -m 755 containerd-%{commit_containerd}/bin/containerd-shim %{buildroot}%{_libexecdir}/%{name}/%{origname}-containerd-shim
install -p -m 755 containerd-%{commit_containerd}/bin/ctr %{buildroot}%{_libexecdir}/%{name}/%{origname}-containerd-ctr

# install runc
install -p -m 755 runc-%{commit_runc}/runc %{buildroot}%{_libexecdir}/%{name}/%{origname}-runc

# install tini
install -p -m 755 tini-%{commit_tini}/tini-static %{buildroot}%{_libexecdir}/%{name}/%{origname}-init

# install udev rules
install -dp %{buildroot}%{_sysconfdir}/udev/rules.d
install -p -m 644 contrib/udev/80-%{origname}.rules %{buildroot}%{_sysconfdir}/udev/rules.d/80-%{origname}.rules

# add init scripts
install -dp %{buildroot}/%{_unitdir}
install -p -m 644 %{SOURCE6} %{buildroot}%{_unitdir}
install -p -m 644 %{SOURCE7} %{buildroot}%{_unitdir}

# add bash, zsh, and fish completions
install -dp %{buildroot}%{_datadir}/bash-completion/completions
install -dp %{buildroot}%{_datadir}/zsh/vendor-completions
install -dp %{buildroot}%{_datadir}/fish/vendor_completions.d
install -p -m 644 cli-%{commit_cli}/contrib/completion/bash/%{origname} %{buildroot}%{_datadir}/bash-completion/completions/%{origname}
install -p -m 644 cli-%{commit_cli}/contrib/completion/zsh/_%{origname} %{buildroot}%{_datadir}/zsh/vendor-completions/_%{origname}
install -p -m 644 cli-%{commit_cli}/contrib/completion/fish/%{origname}.fish %{buildroot}%{_datadir}/fish/vendor_completions.d/%{origname}.fish

# install manpages
install -dp %{buildroot}%{_mandir}/man{1,5,8}
install -p -m 644 cli-%{commit_cli}/man/man1/*.1 %{buildroot}%{_mandir}/man1
install -p -m 644 cli-%{commit_cli}/man/man5/*.5 %{buildroot}%{_mandir}/man5
install -p -m 644 cli-%{commit_cli}/man/man8/*.8 %{buildroot}%{_mandir}/man8

# add vimfiles
install -dp %{buildroot}%{_datadir}/vim/vimfiles/doc
install -dp %{buildroot}%{_datadir}/vim/vimfiles/ftdetect
install -dp %{buildroot}%{_datadir}/vim/vimfiles/syntax
install -p -m 644 contrib/syntax/vim/doc/%{origname}file.txt %{buildroot}%{_datadir}/vim/vimfiles/doc/%{origname}file.txt
install -p -m 644 contrib/syntax/vim/ftdetect/%{origname}file.vim %{buildroot}%{_datadir}/vim/vimfiles/ftdetect/%{origname}file.vim
install -p -m 644 contrib/syntax/vim/syntax/%{origname}file.vim %{buildroot}%{_datadir}/vim/vimfiles/syntax/%{origname}file.vim

# add nano files
install -dp %{buildroot}%{_datadir}/nano
install -p -m 644 contrib/syntax/nano/Dockerfile.nanorc %{buildroot}%{_datadir}/nano/Dockerfile.nanorc

for cli_file in LICENSE MAINTAINERS NOTICE README.md; do
    cp "cli-%{commit_cli}/$cli_file" "$(pwd)/cli-$cli_file"
done

%post
%systemd_post %{origname}

%preun
%systemd_preun %{origname}

%postun
%systemd_postun_with_restart %{origname}

%files
%license cli-LICENSE LICENSE
%doc AUTHORS CHANGELOG.md CONTRIBUTING.md MAINTAINERS NOTICE README.md
%doc cli-MAINTAINERS cli-NOTICE cli-README.md
%{_bindir}/%{origname}
%{_bindir}/%{origname}d
%{_libexecdir}/%{name}/%{origname}-containerd
%{_libexecdir}/%{name}/%{origname}-containerd-shim
%{_libexecdir}/%{name}/%{origname}-containerd-ctr
%{_libexecdir}/%{name}/%{origname}-proxy
%{_libexecdir}/%{name}/%{origname}-runc
%{_libexecdir}/%{name}/%{origname}-init
%{_sysconfdir}/udev/rules.d/80-%{origname}.rules
%{_unitdir}/%{origname}.service
%{_unitdir}/%{origname}-containerd.service
%{_datadir}/bash-completion/completions/%{origname}
%{_mandir}/man1/*
%{_mandir}/man5/*
%{_mandir}/man8/*

%files vim
%dir %{_datadir}/vim/vimfiles/{doc,ftdetect,syntax}
%{_datadir}/vim/vimfiles/doc/%{origname}file.txt
%{_datadir}/vim/vimfiles/ftdetect/%{origname}file.vim
%{_datadir}/vim/vimfiles/syntax/%{origname}file.vim

%files zsh-completion
%dir %{_datadir}/zsh/vendor-completions/
%{_datadir}/zsh/vendor-completions/_%{origname}

%files fish-completion
%dir %{_datadir}/fish/vendor_completions.d
%{_datadir}/fish/vendor_completions.d/%{origname}.fish

%files nano
%dir %{_datadir}/nano
%{_datadir}/nano/Dockerfile.nanorc

%changelog
* Sun Aug 13 2017 Lokesh Mandvekar <lsm5@fedoraproject.org> 17.06.0-1.gitf34e4d2
- initial build
- built moby commit f34e4d2
- built cli commit 4b61f56
- built docker-runc commit 2d41c047
- built docker-containerd commit 3addd84
- built docker-proxy commit 7b2b1fe
