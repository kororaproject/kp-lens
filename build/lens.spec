Name:           lens
Version:        0.12.4
Release:        1%{?dist}.1
Summary:        Simple desktop environment agnostic SDK

License:        GPLv3+
URL:            https://github.com/kororaproject/kp-lens.git
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python2-devel python3-devel
Requires:       adobe-source-sans-pro-fonts
Requires:       google-roboto-condensed-fonts


%description
Lightweight, ENvironment-agnostic SDK (LENS) for building graphical UIs.


%prep
%setup -q

%build
# Nothing to build

%install
mkdir -p %{buildroot}%{python3_sitelib}/lens
mkdir -p %{buildroot}%{_datadir}/%{name}

./build-bundles.sh

cp -a lens-data/*  %{buildroot}%{_datadir}/%{name}/
install -m 0644 COPYING %{buildroot}%{_datadir}/%{name}/

for f in __init__.py app.py appgtk3.py appqt4.py appqt5.py system.py thread.py view.py
do
  install -m 0644 lens/${f} %{buildroot}%{python3_sitelib}/lens/${f}
done


%package -n python3-%{name}
Summary:        Python 3 API for constructing LENS applications
Group:          Applications/System
BuildRequires:  python3-devel
Requires:       %{name} = %{version}-%{release}
Requires:       python3-%{name}-backend = %{version}-%{release}

%description -n python3-%{name}
Python 3 API for constructing LENS applications

%files -n  python3-%{name}
%{python3_sitelib}/lens/__init__.py
%{python3_sitelib}/lens/app.py
%{python3_sitelib}/lens/system.py
%{python3_sitelib}/lens/thread.py
%{python3_sitelib}/lens/view.py
%{python3_sitelib}/lens/__pycache__/__init__.*.py*
%{python3_sitelib}/lens/__pycache__/app.*.py*
%{python3_sitelib}/lens/__pycache__/system.*.py*
%{python3_sitelib}/lens/__pycache__/thread.*.py*
%{python3_sitelib}/lens/__pycache__/view.*.py*


%package -n python3-%{name}-gtk
Summary:        Python 3 API for constructing LENS applications on Gtk
Group:          Applications/System
Provides:       python3-%{name}-backend
Requires:       python3-%{name} = %{version}-%{release}
Requires:       python3-gobject webkitgtk4

%description -n python3-%{name}-gtk
Python 3 API for constructing LENS applications on Gtk systems

%files -n python3-%{name}-gtk
%{python3_sitelib}/lens/appgtk*.py
%{python3_sitelib}/lens/__pycache__/appgtk*.py*


%package -n python3-%{name}-qt4
Summary:        Python 3 API for constructing LENS applications on Qt4
Group:          Applications/System
Provides:       python3-%{name}-backend
Requires:       python3-%{name} = %{version}-%{release}
Requires:       python3-PyQt4

%description -n python3-%{name}-qt4
Python 3 API for constructing LENS applications on Qt4 systems

%files -n python3-%{name}-qt4
%{python3_sitelib}/lens/appqt4.py
%{python3_sitelib}/lens/__pycache__/appqt4.*.py*

%package -n python3-%{name}-qt5
Summary:        Python 3 API for constructing LENS applications on Qt5
Group:          Applications/System
Provides:       python3-%{name}-backend
Requires:       python3-%{name} = %{version}-%{release}
Requires:       python3-qt5
Requires:       python3-qt5-webkit
Requires:       qt5-qtwebchannel
Obsoletes:      python3-%{name}-qt

%description -n python3-%{name}-qt5
Python 3 API for constructing LENS applications on Qt5 systems

%files -n python3-%{name}-qt5
%{python3_sitelib}/lens/appqt5.py
%{python3_sitelib}/lens/__pycache__/appqt5.*.py*

%files
%doc COPYING
%{_datadir}/%{name}/


%changelog
* Sun Nov 20 2016 Ian Firns <firnsy@kororaproject.org> 0.12.4-1
- Fix missing dependency for the qt5 backend.

* Sat Nov 12 2016 Ian Firns <firnsy@kororaproject.org> 0.12.3-1
- Fix geometry setting on gtk backends.

* Mon Jun 27 2016 Ian Firns <firnsy@kororaproject.org> 0.12.2-1
- Fixed incorrect number of parameters passed to subscribers.

* Mon Jun 27 2016 Ian Firns <firnsy@kororaproject.org> 0.12.1-1
- Fixed lens-bridge and modified liveuser detection.

* Sat Mar  5 2016 Ian Firns <firnsy@kororaproject.org> 0.12.0-1
- Utilise QtWebChannel for python/webkit bridge.

* Wed Nov  4 2015 Ian Firns <firnsy@kororaproject.org> 0.11.4-1
- Fixed missing toolkit and fallback detection.

* Mon Oct 19 2015 Ian Firns <firnsy@kororaproject.org> 0.11.3-1
- Support backend specific lens styling.

* Sun Oct 18 2015 Ian Firns <firnsy@kororaproject.org> 0.11.2-1
- Manually handle resource loading.

* Thu Oct  8 2015 Ian Firns <firnsy@kororaproject.org> 0.11.1-1
- Bump all resources.

* Thu Oct  8 2015 Ian Firns <firnsy@kororaproject.org> 0.11.0-1
- Remove HTML replace hack for resource loading.

* Fri Oct  2 2015 Ian Firns <firnsy@kororaproject.org> 0.10.1-1
- No longer build for python 2.

* Thu Oct  1 2015 Ian Firns <firnsy@kororaproject.org> 0.10.0-1
- Refactored angularjs bridge out of core lens.

* Tue Jun 23 2015 Ian Firns <firnsy@kororaproject.org> 0.9.1-1
- Updated button theme.

* Thu Apr 23 2015 Ian Firns <firnsy@kororaproject.org> 0.9.0-1
- Provided initial system theme matching
- Fixed widget fallback.
- Added window toggling.
- Fixed dep handling on python3 packages.

* Fri Jan 30 2015 Ian Firns <firnsy@kororaproject.org> 0.8.0-1
- Updated bootstrap to 3.3.1.

* Sun Jan 18 2015 Ian Firns <firnsy@kororaproject.org> 0.7.6-1
- Fixed locale detection for float conversions.

* Mon Dec 29 2014 Ian Firns <firnsy@kororaproject.org> 0.7.5-1
- Fixed live environment detection logic.

* Sun Dec 28 2014 Ian Firns <firnsy@kororaproject.org> 0.7.4-1
- Updated Xfce detection logic.

* Sun Dec 28 2014 Ian Firns <firnsy@kororaproject.org> 0.7.3-1
- Fixed QString does not exist in python3 Qt4 bindings.

* Tue Dec 16 2014 Ian Firns <firnsy@kororaproject.org> 0.7.1-1
- Updated to latest upstream.

* Fri Dec 12 2014 Ian Firns <firnsy@kororaproject.org> 0.7.0-1
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
