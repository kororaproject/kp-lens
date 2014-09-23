Name:           lens
Version:        0.2.0
Release:        1%{?dist}
Summary:        Simple desktop environment agnostic SDK

License:        GPLv3+
URL:            https://github.com/kororaproject/kp-lens.git
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python2-devel
Requires:       python

%description
Lightweight ENvironement-agnostic SDK (LENS) for building graphical UIs.

%prep
%setup -q

%build
# Nothing to build

%install
mkdir -p %{buildroot}%{python3_sitelib}/Lens
mkdir -p %{buildroot}%{python_sitelib}/Lens
mkdir -p %{buildroot}%{_datadir}/%{name}


cp -a lens-data/*  %{buildroot}%{_datadir}/%{name}/

cat lens-data/js/{jquery,angular,bootstrap,lens-bridge,lens-ui}.js > %{buildroot}%{_datadir}/%{name}/js/lens.js
cat lens-data/js/{jquery,angular,bootstrap}.min.js lens-data/js/{lens-bridge,lens-ui}.js > %{buildroot}%{_datadir}/%{name}/js/lens.min.js

install -m 0644 COPYING %{buildroot}%{_datadir}/%{name}/
install -m 0644 README %{buildroot}%{_datadir}/%{name}/


install -m 0644 Lens/* %{buildroot}%{python_sitelib}/Lens/
install -m 0644 Lens/* %{buildroot}%{python3_sitelib}/Lens/


%package -n python3-%{name}
Summary:        Python 3 API for constructing LENS applications
Group:          Applications/System
BuildRequires:  python3-devel
Requires:       %{name} = %{version}-%{release}
Requires:       python3-gobject

%description -n python3-%{name}
Python 3 API for constructing LENS applications

%files -n  python3-%{name}
%{python3_sitelib}/Lens

%package -n python-%{name}
Summary:        Python 2 API for constructing LENS applications
Group:          Applications/System
BuildRequires:  python2-devel
Requires:       %{name} = %{version}-%{release}
Requires:       pygobject3

%description -n python-%{name}
Python 2 API for constructing LENS applications

%files -n  python-%{name}
%{python_sitelib}/Lens


%files
%doc README COPYING
%{_datadir}/%{name}/


%changelog
* Tue Sep 23 2014 Ian Firns <firnsy@kororaproject.org> 0.2.0-1
- Updated to include latest namespace changes for applications.

* Mon Sep 22 2014 Ian Firns <firnsy@kororaproject.org> 0.1.0-1
- Initial RPM for LENS.
