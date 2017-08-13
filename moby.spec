%global git_moby https://github.com/moby/moby
%global commit_moby f34e4d295d5c17a78c33beb14b65e5d001c16968
%global shortcommit_moby %(c=%{commit_moby}; echo ${c:0:7})

%global git_cli https://github.com/docker/cli
%global commit_cli 4b61f560b5b0812fcebbe320a98baac9408a5dd4
%global shortcommit_cli %(c=%{commit_cli}; echo ${c:0:7})

%global git_runc https://github.com/docker/runc
%global commit_runc 2d41c047c83e09a6d61d464906feb2a2f3c52aa4
%global shortcommit_runc %(c=%{commit_runc}; echo ${c:0:7})

Name: moby
Version: 17.06.0
Release: 1.git%{shortcommit_moby}%{?dist}
Summary: The open-source application container engine
License: ASL 2.0
Source0: %{git_moby}/archive/%{commit_moby}/moby-%{shortcommit_moby}.tar.gz
Source1: %{git_cli}/archive/%{commit_cli}/cli-%{shortcommit_cli}.tar.gz
Source2: %{git_runc}/archive/%{commit_runc}/runc-%{shortcommit_runc}.tar.gz
URL: https://www.docker.com

# DWZ problem with multiple golang binary, see bug
# https://bugzilla.redhat.com/show_bug.cgi?id=995136#c12
%global _dwz_low_mem_die_limit 0

BuildRequires: libtool-ltdl-devel
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
Conflicts: docker
Conflicts: docker-io
Conflicts: docker-engine-cs
Conflicts: docker-ee

# Obsolete packages
Obsoletes: docker-ce-selinux
Obsoletes: docker-engine-selinux
Obsoletes: docker-engine

%description
Docker is an open source project to build, ship and run any application as a
lightweight container.

Docker containers are both hardware-agnostic and platform-agnostic. This means
they can run anywhere, from your laptop to the largest EC2 compute instance and
everything in between - and they don't require you to use a particular
language, framework or packaging system. That makes them great building blocks
for deploying and scaling web apps, databases, and backend services without
depending on a particular stack or provider.

%prep
%autosetup -Sgit -n %{name}-%{commit_moby}
tar zxf %{SOURCE1}

%build
mkdir _build
pushd _build
mkdir -p $(pwd)/src/github.com/docker
ln -s $(dirs +1 -l) src/github.com/docker/moby
popd

export DOCKER_GITCOMMIT=%{shortcommit_moby}
pushd _build/src/github.com/docker/%{name}
GOPATH=$(pwd) RUNC_BUILDTAGS="seccomp selinux" hack/dockerfile/install-binaries.sh runc-dynamic containerd-dynamic proxy-dynamic tini
#TMP_GOPATH="/go" hack/dockerfile/install-binaries.sh runc-dynamic containerd-dynamic proxy-dynamic tini
BUILDTAGS="seccomp selinux" hack/make.sh dynbinary
popd

pushd cli-%{commit_cli}
mkdir -p src/github.com/docker/cli
ln -s $(pwd)/* src/github.com/docker/cli
export GOPATH=%{gopath}:$(pwd)
make VERSION=$(cat VERSION) GITCOMMIT=%{shortcommit_cli} dynbinary # cli
popd

%check
#cli/build/docker -v
#engine/bundles/%{_origversion}/dynbinary-daemon/dockerd -v

%install
# install binary
install -d $RPM_BUILD_ROOT/%{_bindir}
install -p -m 755 cli/build/docker $RPM_BUILD_ROOT/%{_bindir}/docker
install -p -m 755 engine/bundles/%{_origversion}/dynbinary-daemon/dockerd-%{_origversion} $RPM_BUILD_ROOT/%{_bindir}/dockerd

# install proxy
install -p -m 755 /usr/local/bin/docker-proxy $RPM_BUILD_ROOT/%{_bindir}/docker-proxy

# install containerd
install -p -m 755 /usr/local/bin/docker-containerd $RPM_BUILD_ROOT/%{_bindir}/docker-containerd
install -p -m 755 /usr/local/bin/docker-containerd-shim $RPM_BUILD_ROOT/%{_bindir}/docker-containerd-shim
install -p -m 755 /usr/local/bin/docker-containerd-ctr $RPM_BUILD_ROOT/%{_bindir}/docker-containerd-ctr

# install runc
install -p -m 755 /usr/local/bin/docker-runc $RPM_BUILD_ROOT/%{_bindir}/docker-runc

# install tini
install -p -m 755 /usr/local/bin/docker-init $RPM_BUILD_ROOT/%{_bindir}/docker-init

# install udev rules
install -d $RPM_BUILD_ROOT/%{_sysconfdir}/udev/rules.d
install -p -m 644 engine/contrib/udev/80-docker.rules $RPM_BUILD_ROOT/%{_sysconfdir}/udev/rules.d/80-docker.rules

# add init scripts
install -d $RPM_BUILD_ROOT/etc/sysconfig
install -d $RPM_BUILD_ROOT/%{_initddir}
install -d $RPM_BUILD_ROOT/%{_unitdir}
install -p -m 644 /systemd/docker.service $RPM_BUILD_ROOT/%{_unitdir}/docker.service
# add bash, zsh, and fish completions
install -d $RPM_BUILD_ROOT/usr/share/bash-completion/completions
install -d $RPM_BUILD_ROOT/usr/share/zsh/vendor-completions
install -d $RPM_BUILD_ROOT/usr/share/fish/vendor_completions.d
install -p -m 644 cli/contrib/completion/bash/docker $RPM_BUILD_ROOT/usr/share/bash-completion/completions/docker
install -p -m 644 cli/contrib/completion/zsh/_docker $RPM_BUILD_ROOT/usr/share/zsh/vendor-completions/_docker
install -p -m 644 cli/contrib/completion/fish/docker.fish $RPM_BUILD_ROOT/usr/share/fish/vendor_completions.d/docker.fish

# install manpages
install -d %{buildroot}%{_mandir}/man1
install -p -m 644 cli/man/man1/*.1 $RPM_BUILD_ROOT/%{_mandir}/man1
install -d %{buildroot}%{_mandir}/man5
install -p -m 644 cli/man/man5/*.5 $RPM_BUILD_ROOT/%{_mandir}/man5
install -d %{buildroot}%{_mandir}/man8
install -p -m 644 cli/man/man8/*.8 $RPM_BUILD_ROOT/%{_mandir}/man8

# add vimfiles
install -d $RPM_BUILD_ROOT/usr/share/vim/vimfiles/doc
install -d $RPM_BUILD_ROOT/usr/share/vim/vimfiles/ftdetect
install -d $RPM_BUILD_ROOT/usr/share/vim/vimfiles/syntax
install -p -m 644 engine/contrib/syntax/vim/doc/dockerfile.txt $RPM_BUILD_ROOT/usr/share/vim/vimfiles/doc/dockerfile.txt
install -p -m 644 engine/contrib/syntax/vim/ftdetect/dockerfile.vim $RPM_BUILD_ROOT/usr/share/vim/vimfiles/ftdetect/dockerfile.vim
install -p -m 644 engine/contrib/syntax/vim/syntax/dockerfile.vim $RPM_BUILD_ROOT/usr/share/vim/vimfiles/syntax/dockerfile.vim

# add nano
install -d $RPM_BUILD_ROOT/usr/share/nano
install -p -m 644 engine/contrib/syntax/nano/Dockerfile.nanorc $RPM_BUILD_ROOT/usr/share/nano/Dockerfile.nanorc

mkdir -p build-docs
for engine_file in AUTHORS CHANGELOG.md CONTRIBUTING.md LICENSE MAINTAINERS NOTICE README.md; do
    cp "engine/$engine_file" "build-docs/engine-$engine_file"
done
for cli_file in LICENSE MAINTAINERS NOTICE README.md; do
    cp "cli/$cli_file" "build-docs/cli-$cli_file"
done

# list files owned by the package here
%files
%doc build-docs/engine-AUTHORS build-docs/engine-CHANGELOG.md build-docs/engine-CONTRIBUTING.md build-docs/engine-LICENSE build-docs/engine-MAINTAINERS build-docs/engine-NOTICE build-docs/engine-README.md
%doc build-docs/cli-LICENSE build-docs/cli-MAINTAINERS build-docs/cli-NOTICE build-docs/cli-README.md
%{_bindir}/docker
%{_bindir}/dockerd
%{_bindir}/docker-containerd
%{_bindir}/docker-containerd-shim
%{_bindir}/docker-containerd-ctr
%{_bindir}/docker-proxy
%{_bindir}/docker-runc
%{_bindir}/docker-init
%{_sysconfdir}/udev/rules.d/80-docker.rules
%{_unitdir}/docker.service
%{_datadir}/bash-completion/completions/docker
%{_datadir}/zsh/vendor-completions/_docker
%{_datadir}/fish/vendor_completions.d/docker.fish
%{_mandir}/man1/*
%{_mandir}/man5/*
%{_mandir}/man8/*
%{_datadir}/vim/vimfiles/doc/dockerfile.txt
%{_datadir}/vim/vimfiles/ftdetect/dockerfile.vim
%{_datadir}/vim/vimfiles/syntax/dockerfile.vim
%{_datadir}/nano/Dockerfile.nanorc

%pre
if [ $1 -gt 0 ] ; then
    # package upgrade scenario, before new files are installed

    # clear any old state
    rm -f %{_localstatedir}/lib/rpm-state/docker-is-active > /dev/null 2>&1 || :

    # check if docker service is running
    if systemctl is-active docker > /dev/null 2>&1; then
        systemctl stop docker > /dev/null 2>&1 || :
        touch %{_localstatedir}/lib/rpm-state/docker-is-active > /dev/null 2>&1 || :
    fi
fi

%post
%systemd_post docker
if ! getent group docker > /dev/null; then
    groupadd --system docker
fi

%preun
%systemd_preun docker

%postun
%systemd_postun_with_restart docker

%posttrans
if [ $1 -ge 0 ] ; then
    # package upgrade scenario, after new files are installed

    # check if docker was running before upgrade
    if [ -f %{_localstatedir}/lib/rpm-state/docker-is-active ]; then
        systemctl start docker > /dev/null 2>&1 || :
        rm -f %{_localstatedir}/lib/rpm-state/docker-is-active > /dev/null 2>&1 || :
    fi
fi

%changelog
* Sun Aug 13 2017 Lokesh Mandvekar <lsm5@fedoraproject.org> 17.06.0-1.gitf34e4d2
- release docker-ce 17.06.0-ce-rc1
