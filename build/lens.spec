Name:           lens
Version:        0.7.2
Release:        1%{?dist}
Summary:        Simple desktop environment agnostic SDK

License:        GPLv3+
URL:            https://github.com/kororaproject/kp-lens.git
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python2-devel python3-devel

%description
Lightweight ENvironement-agnostic SDK (LENS) for building graphical UIs.

%prep
%setup -q

%build
# Nothing to build

%install
mkdir -p %{buildroot}%{python3_sitelib}/lens
mkdir -p %{buildroot}%{python_sitelib}/lens
mkdir -p %{buildroot}%{_datadir}/%{name}

./build-bundles.sh

cp -a lens-data/*  %{buildroot}%{_datadir}/%{name}/

install -m 0644 COPYING %{buildroot}%{_datadir}/%{name}/
install -m 0644 README %{buildroot}%{_datadir}/%{name}/


install -m 0644 lens/* %{buildroot}%{python_sitelib}/lens/
install -m 0644 lens/* %{buildroot}%{python3_sitelib}/lens/


%package -n python3-%{name}
Summary:        Python 3 API for constructing LENS applications
Group:          Applications/System
BuildRequires:  python3-devel
Requires:       %{name} = %{version}-%{release}
Requires:       python3-gobject lens

%description -n python3-%{name}
Python 3 API for constructing LENS applications

%files -n  python3-%{name}
%{python3_sitelib}/lens

%package -n python-%{name}
Summary:        Python 2 API for constructing LENS applications
Group:          Applications/System
BuildRequires:  python2-devel
Requires:       %{name} = %{version}-%{release}
Requires:       pygobject3 lens

%description -n python-%{name}
Python 2 API for constructing LENS applications

%files -n  python-%{name}
%{python_sitelib}/lens


%files
%doc README COPYING
%{_datadir}/%{name}/


%changelog
* Tue Dec 16 2014 Ian Firns <firnsy@kororaproject.org> 0.7.1-1
- Updated to latest upstream.

* Thu Dec 12 2014 Ian Firns <firnsy@kororaproject.org> 0.7.0-1
- Updated to latest upstream.

* Thu Dec 11 2014 Ian Firns <firnsy@kororaproject.org> 0.6.3-1
- Updated to latest upstream.

* Wed Dec 10 2014 Chris Smart <csmart@kororaproject.org> 0.6.2-2
- Pull in python-lens for main lens app

* Sun Nov 16 2014 Ian Firns <firnsy@kororaproject.org> 0.6.2-1
- Updated to latest upstream.

* Thu Oct 16 2014 Ian Firns <firnsy@kororaproject.org> 0.6.1-1
- Updated to latest upstream.

* Mon Oct  6 2014 Ian Firns <firnsy@kororaproject.org> 0.6.0-1
- Updated to latest upstream.

* Sun Oct  5 2014 Ian Firns <firnsy@kororaproject.org> 0.5.1-1
- Updated to latest upstream.

* Wed Oct  1 2014 Ian Firns <firnsy@kororaproject.org> 0.5.0-1
- Updated to latest upstream.

* Mon Sep 29 2014 Ian Firns <firnsy@kororaproject.org> 0.4.2-1
- Updated to latest upstream.

* Fri Sep 26 2014 Ian Firns <firnsy@kororaproject.org> 0.4.1-1
- Updated to latest upstream.

* Thu Sep 25 2014 Ian Firns <firnsy@kororaproject.org> 0.4.0-1
- Updated to latest upstream.

* Wed Sep 24 2014 Ian Firns <firnsy@kororaproject.org> 0.3.0-1
- Updated to latest upstream.

* Tue Sep 23 2014 Ian Firns <firnsy@kororaproject.org> 0.2.0-1
- Updated to latest namespace changes for applications.

* Mon Sep 22 2014 Ian Firns <firnsy@kororaproject.org> 0.1.0-1
- Initial RPM for LENS.
