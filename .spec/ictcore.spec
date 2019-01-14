%define core_version __CORE_VERSION__
%define core_edition __CORE_EDITION__
%define core_build   __CORE_BUILD__
%define core_home    %{_prefix}/ictcore
%define core_token   __CORE_TOKEN__

Name:    ictcore
Version: %{core_version}.%{core_build}
Release: %{core_edition}%{?dist}
Summary: library for fax and email related services provided API interface

Vendor:   ICT Innovations
Group:    ict
Packager: Nasir Iqbal <nasir@ictinnovations.com> 
License:  MPLv2
URL:      https://ictcore.org/

Source0:  %{name}-%{version}.tar.gz
Source1:  composer

BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%if %{rhel} < 7
BuildRequires: php php-process php-cli subversion
%else
BuildRequires: php php-process php-cli subversion composer
%endif

Provides: ictcore

# ICTCore developed in php
Requires: php php-cli php-curl php-mcrypt php-mbstring php-xmlrpc php-process php-mysql php-xml
Requires: php-pear php-pear-Pager php-pear-SOAP php-pear-HTTP-Request
Requires: php-pecl-imagick php-pecl-json php-pecl-libevent
# ICTCore use mysql as database in centos 6 or mariadb in centos 7
%if %{rhel} < 7
Requires: mysql mysql-server mysql-connector-odbc
%else
Requires: mariadb mariadb-server mysql-connector-odbc
%endif
# ICTCore exposse its services via apache web server
%if %{rhel} < 7
Requires: httpd
%else
Requires: httpd certbot python2-certbot-apache
%endif
# Other dependencies
Requires: coreutils acl sudo tzdata ntp cronie dos2unix shadow-utils


%description
ICTCore is backend library for voice, fax, sms and email related services, it provide API interface to interact with other applications

%package freeswitch
Group: ict
Summary: Freeswitch addon for ICTCore
Requires: ictcore curl sed
Requires: freeswitch freeswitch-config-vanilla freeswitch-lua freeswitch-application-curl freeswitch-sounds-en-us-callie-8000
Requires: freeswitch-asrtts-flite
Provides: ictcore-freeswitch ictcore-gateway-voice ictcore-gateway-fax

%description freeswitch
add freeswitch gateway support in ICTCore

%package kannel
Group: ict
Summary: Kannel addon for ICTCore
Requires: ictcore kannel
Provides: ictcore-kannel ictcore-gateway-sms

%description kannel
add kannel gateway support in ICTCore

%package sendmail
Group: ict
Summary: Sendmail addon for ICTCore
Requires: ictcore sendmail sendmail-cf php-imap
Provides: ictcore-sendmail ictcore-gateway-email

%description sendmail
add Sendmail gateway support in ICTCore

%package voice
Group: ict
Summary: voice addon for ICTCore
Requires: ictcore ictcore-gateway-voice sox

%description voice
add voice related services support in ICTCore

%package fax
Group: ict
Summary: fax addon for ICTCore
# for pdf and tiff handling  # TODO yudit
%if %{rhel} < 7
Requires: ictcore ictcore-gateway-fax ghostscript ImageMagick poppler-utils hylafax+-client libreoffice-core libtiff
%else
Requires: ictcore ictcore-gateway-fax ghostscript ImageMagick poppler-utils hylafax+-client libreoffice-core libtiff-tools
%endif

%description fax
add sms related services support in ICTCore

%package sms
Group: ict
Summary: sms addon for ICTCore
Requires: ictcore ictcore-gateway-sms

%description sms
add sms related services support in ICTCore

%package email
Group: ict
Summary: email addon for ICTCore
Requires: ictcore ictcore-gateway-email

%description email
add email related services support in ICTCore


%prep
%setup -q -n %{name}-%{version}

%build


%install
%{__rm} -rf %{buildroot}
%{__install} -d %{buildroot}%{core_home}
%{__cp} -pr * %{buildroot}%{core_home}

# install composer based dependencies
php %SOURCE1 config --global github-oauth.github.com %{core_token}
php %SOURCE1 update -d %{buildroot}%{core_home}
php %SOURCE1 config --global --auth --unset github-oauth.github.com

# basic configuration in system
%{__mkdir} -p %{buildroot}/etc
%{__ln_s} /usr/ictcore/etc/ictcore.conf %{buildroot}/etc/ictcore.conf
# cronjob configuration in system
%{__mkdir} -p %{buildroot}/etc/cron.d
%{__cp} %{buildroot}%{core_home}/etc/ictcore.cron %{buildroot}/etc/cron.d/ictcore.cron
# install ictcore configuration for apache
%{__mkdir} -p %{buildroot}/etc/httpd/conf.d/
%{__cp} %{buildroot}%{core_home}/etc/http/ictcore.conf %{buildroot}/etc/httpd/conf.d/ictcore.conf

# install ictbroadcast configuration for php
%{__mkdir} -p %{buildroot}/etc/php.d
%{__cp} %{buildroot}%{core_home}/etc/php/ictcore.ini %{buildroot}/etc/php.d/ictcore.ini

# Freeswitch related configuration installation
%{__mkdir} -p %{buildroot}/etc/freeswitch/directory/default
%{__mkdir} -p %{buildroot}/etc/freeswitch/sip_profiles
%{__mkdir} -p %{buildroot}/etc/freeswitch/dialplan
%{__ln_s} /usr/ictcore/etc/freeswitch/directory/ictcore.xml %{buildroot}/etc/freeswitch/directory/default/ictcore.xml
%{__ln_s} /usr/ictcore/etc/freeswitch/sip_profiles/ictcore.xml %{buildroot}/etc/freeswitch/sip_profiles/ictcore.xml
%{__ln_s} /usr/ictcore/etc/freeswitch/dialplan/ictcore.xml %{buildroot}/etc/freeswitch/dialplan/ictcore.xml

# Sendmail related configuration installation
%{__mkdir} -p %{buildroot}/var/spool/mail
touch %{buildroot}/var/spool/mail/ictcore


%clean
%{__rm} -rf %{buildroot}


%files
# basic configuration files
%defattr(644,root,root,755)
/etc/ictcore.conf
/etc/cron.d
/etc/php.d
%config /etc/cron.d/ictcore.cron
%config /etc/httpd/conf.d/ictcore.conf

# include all ictcore files and folder
%defattr(644,ictcore,ictcore,755)
%{core_home}

# we need all etc files as config files
%config %{core_home}/etc
# some config files should never be replaced during an update
# don't update any general configuration file
%config(noreplace) %{core_home}/etc/ictcore.conf
%config(noreplace) %{core_home}/etc/odbc.ini

# save documents
%doc %{core_home}/docs
%doc %{core_home}/CHANGLOG.md
%doc %{core_home}/README.md
%doc %{core_home}/LICENSE.md
%doc %{core_home}/TODO.md

# write-able directories and files
%defattr(664,ictcore,ictcore,775)
%{core_home}/log
%{core_home}/data

# binary files should be exectuteable
%defattr(755,ictcore,ictcore,755)
%{core_home}/bin

# Packages
# ========
# exclude All other optional addons from main package

# exclude freeswitch related files
%exclude %{core_home}/etc/freeswitch
%exclude %{core_home}/bin/freeswitch
%exclude %{core_home}/core/Gateway/Freeswitch.php

# exclude kannel related files
%exclude %{core_home}/etc/kannel
%exclude %{core_home}/core/Gateway/Kannel.php

# exclude sendmail related files
# TODO: kannel configurations
%exclude %{core_home}/core/Gateway/Sendmail.php

# exclude voice related files
%exclude %{core_home}/db/voice.sql
%exclude %{core_home}/core/Service/Voice.php
%exclude %{core_home}/core/Message/Recording.php
%exclude %{core_home}/core/Api/Message/RecordingApi.php
%exclude %{core_home}/core/Application/Voice_play.php
%exclude %{core_home}/core/Program/Voicemessage.php

# exclude fax related files.
%exclude %{core_home}/db/fax.sql
%exclude %{core_home}/core/Service/Fax.php
%exclude %{core_home}/core/Message/Document.php
%exclude %{core_home}/core/Api/Message/DocumentApi.php
%exclude %{core_home}/core/Application/Fax_send.php
%exclude %{core_home}/core/Application/Fax_receive.php
%exclude %{core_home}/core/Program/Sendfax.php
%exclude %{core_home}/core/Program/Receivefax.php

# exclude sms related files
%exclude %{core_home}/db/sms.sql
%exclude %{core_home}/core/Service/Sms.php
%exclude %{core_home}/core/Message/Text.php
%exclude %{core_home}/core/Api/Message/TextApi.php
%exclude %{core_home}/core/Application/Sms_send.php
%exclude %{core_home}/core/Application/Sms_receive.php
%exclude %{core_home}/core/Program/Sendsms.php
%exclude %{core_home}/core/Program/Receivesms.php

# exclude email related files
%exclude %{core_home}/db/email.sql
%exclude %{core_home}/core/Service/Email.php
%exclude %{core_home}/core/Message/Template.php
%exclude %{core_home}/core/Api/Message/TemplateApi.php
%exclude %{core_home}/core/Application/Email_send.php
%exclude %{core_home}/core/Application/Email_receive.php
%exclude %{core_home}/core/Program/Sendemail.php
%exclude %{core_home}/core/Program/Receiveemail.php
%exclude %{core_home}/core/Program/Faxtoemail.php
%exclude %{core_home}/core/Program/Emailtofax.php
%exclude %{core_home}/core/Program/Faxtoemail
%exclude %{core_home}/core/Program/Emailtofax

%files freeswitch
# freeswitch configuration files
%defattr(644,freeswitch,daemon,755)
# /etc/freeswitch # this directory will be provided by freeswitch package so avoid it
/etc/freeswitch/directory/default/ictcore.xml
/etc/freeswitch/sip_profiles/ictcore.xml
/etc/freeswitch/dialplan/ictcore.xml

# other freeswitch related files
%defattr(664,ictcore,ictcore,775)
%{core_home}/etc/freeswitch
%defattr(644,ictcore,ictcore,755)
%{core_home}/bin/freeswitch
%{core_home}/core/Gateway/Freeswitch.php

%files kannel
# kannel related files
%defattr(644,ictcore,ictcore,755)
# %{core_home}/etc/kannel # this directory will be provided by kannel package, so avoid it
%defattr(664,ictcore,ictcore,775)
%{core_home}/etc/kannel/provider
%defattr(644,ictcore,ictcore,755)
%{core_home}/core/Gateway/Kannel.php

%files sendmail
# create inbox for incoming mails
%defattr(660,ictcore,ictcore,770)
%config(noreplace) /var/spool/mail/ictcore
# other sendmail related files
%defattr(644,ictcore,ictcore,755)
%{core_home}/core/Gateway/Sendmail.php

%files voice
# voice related files
%defattr(644,ictcore,ictcore,755)
%{core_home}/db/voice.sql
%{core_home}/core/Service/Voice.php
%{core_home}/core/Message/Recording.php
%{core_home}/core/Api/Message/RecordingApi.php
%{core_home}/core/Application/Voice_play.php
%{core_home}/core/Program/Voicemessage.php

%files fax
# fax related files
%defattr(644,ictcore,ictcore,755)
%{core_home}/db/fax.sql
%{core_home}/core/Service/Fax.php
%{core_home}/core/Message/Document.php
%{core_home}/core/Api/Message/DocumentApi.php
%{core_home}/core/Application/Fax_send.php
%{core_home}/core/Application/Fax_receive.php
%{core_home}/core/Program/Sendfax.php
%{core_home}/core/Program/Receivefax.php

%files sms
# sms related files
%defattr(644,ictcore,ictcore,755)
%{core_home}/db/sms.sql
%{core_home}/core/Service/Sms.php
%{core_home}/core/Message/Text.php
%{core_home}/core/Api/Message/TextApi.php
%{core_home}/core/Application/Sms_send.php
%{core_home}/core/Application/Sms_receive.php
%{core_home}/core/Program/Sendsms.php
%{core_home}/core/Program/Receivesms.php

%files email
# email related files
%defattr(644,ictcore,ictcore,755)
%{core_home}/db/email.sql
%{core_home}/core/Service/Email.php
%{core_home}/core/Message/Template.php
%{core_home}/core/Api/Message/TemplateApi.php
%{core_home}/core/Application/Email_send.php
%{core_home}/core/Application/Email_receive.php
%{core_home}/core/Program/Sendemail.php
%{core_home}/core/Program/Receiveemail.php
%{core_home}/core/Program/Faxtoemail.php
%{core_home}/core/Program/Emailtofax.php
%{core_home}/core/Program/Faxtoemail
%{core_home}/core/Program/Emailtofax

%pre
# create ictcore user and group
useradd -r -M -s /sbin/nologin -d /usr/ictcore ictcore 2> /dev/null || :
# assign additional group to ictcore
usermod --append --groups ictcore apache
# also allow ictcore to access apache files
usermod --append --groups apache ictcore

%pre freeswitch
usermod --append --groups daemon ictcore
usermod --append --groups ictcore freeswitch

%pre kannel
usermod --append --groups kannel ictcore

%pre sendmail
usermod --append --groups mail ictcore
usermod --append --groups mail apache # only to fetch new emails, cron can be trigger via apache


%post
# all new logs must be writable for group users
chmod g+s %{core_home}/log
setfacl -d -m g::rw %{core_home}/log
# system cache directory must be writable
chmod g+rws %{core_home}/cache
setfacl -d -m g::rw %{core_home}/cache
# enable event support in mysql
grep 'event-scheduler=ON' /etc/my.cnf || sed -i "s/\[mysqld\]/[mysqld]\nevent-scheduler=ON/" /etc/my.cnf
# enable and start cron service
%if %{rhel} < 7
/sbin/chkconfig crond on
/sbin/service crond restart
%else
/usr/bin/systemctl enable crond.service
/usr/bin/systemctl restart crond.service
%endif
# enable and start mysql or mariadb server
%if %{rhel} < 7
/sbin/chkconfig mysqld on
/sbin/service mysqld start
%else
/usr/bin/systemctl enable mariadb.service
/usr/bin/systemctl start mariadb.service
%endif
# enable and start apache server
%if %{rhel} < 7
/sbin/chkconfig httpd on
/sbin/service httpd restart
%else
/usr/bin/systemctl enable httpd.service
/usr/bin/systemctl restart httpd.service
%endif
# configure firewall for web
%if %{rhel} < 7
/sbin/iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 80 -j ACCEPT    # web
/sbin/iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 443 -j ACCEPT   # ssl web
/etc/init.d/iptables save
%else
/bin/firewall-cmd --zone=public --add-port=80/tcp --permanent    # web
/bin/firewall-cmd --zone=public --add-port=443/tcp --permanent   # ssl web
/bin/firewall-cmd --runtime-to-permanent
/bin/firewall-cmd --reload
%endif
# Finally generate security keys for ictcore
bash /usr/ictcore/bin/keygen

%post voice
# all new data files must be writable for group users
chmod g+rws %{core_home}/data/recording
setfacl -d -m g::rw %{core_home}/data/recording

%post fax
# all new data files must be writable for group users
chmod g+rws %{core_home}/data/document
setfacl -d -m g::rw %{core_home}/data/document

%post email
# all new data files must be writable for group users
chmod g+rws %{core_home}/data/template
setfacl -d -m g::rw %{core_home}/data/template

%post freeswitch
# all new configuration files must be writable for group users
chmod g+rws %{core_home}/etc/freeswitch/directory/account
setfacl -d -m g::rw %{core_home}/etc/freeswitch/directory/account
chmod g+rws %{core_home}/etc/freeswitch/sip_profiles/provider
setfacl -d -m g::rw %{core_home}/etc/freeswitch/sip_profiles/provider
# enable curl module in freeswitch module configuration
sed -i 's/<!-- <load module="mod_flite"\/> -->/<load module="mod_flite"\/>/g' \
/etc/freeswitch/autoload_configs/modules.conf.xml
sed -i 's/<!-- <load module="mod_curl"\/> -->/<load module="mod_curl"\/>/g' \
/etc/freeswitch/autoload_configs/modules.conf.xml
# enable and start freeswitch server
%if %{rhel} < 7
/sbin/chkconfig freeswitch on
/sbin/service freeswitch restart
%else
/usr/bin/systemctl enable freeswitch.service
/usr/bin/systemctl restart freeswitch.service
%endif
# alter firewall for sip
%if %{rhel} < 7
# sip internal profile
/sbin/iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 5060 -j ACCEPT    # tcp
/sbin/iptables -I INPUT -p tcp -m state --state NEW -m udp --dport 5060 -j ACCEPT    # udp
/sbin/iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 5061 -j ACCEPT    # tls
/sbin/iptables -I INPUT -p tcp -m state --state NEW -m udp --dport 5061 -j ACCEPT    # dtls
# sip external profile
/sbin/iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 8060 -j ACCEPT    # tcp
/sbin/iptables -I INPUT -p tcp -m state --state NEW -m udp --dport 8060 -j ACCEPT    # udp
/sbin/iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 8061 -j ACCEPT    # tls
/sbin/iptables -I INPUT -p tcp -m state --state NEW -m udp --dport 8061 -j ACCEPT    # dtls
# sip ictcore profile
/sbin/iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 5070 -j ACCEPT    # tcp
/sbin/iptables -I INPUT -p tcp -m state --state NEW -m udp --dport 5070 -j ACCEPT    # udp
/sbin/iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 5071 -j ACCEPT    # tls
/sbin/iptables -I INPUT -p udp -m state --state NEW -m udp --dport 5071 -j ACCEPT    # dtls
# WebRTC ports
/sbin/iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 7443 -j ACCEPT    # wss
# media ports
/sbin/iptables -I INPUT -p udp --dport 10000:20000 -j ACCEPT     # rtp
/etc/init.d/iptables save
%else
# sip internal profile
/bin/firewall-cmd --zone=public --add-port=5060/udp --permanent  # udp
/bin/firewall-cmd --zone=public --add-port=5060/tcp --permanent  # tcp
/bin/firewall-cmd --zone=public --add-port=5061/udp --permanent  # tls
/bin/firewall-cmd --zone=public --add-port=5061/tcp --permanent  # dtls
# sip external profile
/bin/firewall-cmd --zone=public --add-port=5080/udp --permanent  # udp
/bin/firewall-cmd --zone=public --add-port=5080/tcp --permanent  # tcp
/bin/firewall-cmd --zone=public --add-port=5081/udp --permanent  # tls
/bin/firewall-cmd --zone=public --add-port=5081/tcp --permanent  # dtls
# sip ictcore profile
/bin/firewall-cmd --zone=public --add-port=5070/udp --permanent  # udp
/bin/firewall-cmd --zone=public --add-port=5070/tcp --permanent  # tcp
/bin/firewall-cmd --zone=public --add-port=5071/udp --permanent  # tls
/bin/firewall-cmd --zone=public --add-port=5071/tcp --permanent  # dtls
# WebRTC ports
/bin/firewall-cmd --zone=public --add-port=7443/tcp --permanent  # wss
# media ports
/bin/firewall-cmd --zone=public --add-port=10000-20000/udp --permanent # rtp
/bin/firewall-cmd --runtime-to-permanent
/bin/firewall-cmd --reload
%endif

%post kannel
# all new configuration files must be writable for group users
chmod g+rws %{core_home}/etc/kannel/provider
setfacl -d -m g::rw %{core_home}/etc/kannel/provider
# save original configuration if exist
if [ ! -L "/etc/kannel.conf" ]; then
  mv /etc/kannel.conf /etc/kannel.conf.backup
  ln -s /usr/ictcore/etc/kannel/kannel.conf /etc/kannel.conf
fi
# alter firewall for smtp
%if %{rhel} < 7
/sbin/iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 2775 -j ACCEPT    # smpp
/etc/init.d/iptables save
%else
/bin/firewall-cmd --zone=public --add-port=2775/tcp --permanent  # smpp
/bin/firewall-cmd --runtime-to-permanent
/bin/firewall-cmd --reload
%endif
%if %{rhel} < 7
/sbin/chkconfig kannel on
/sbin/service kannel restart
%else
/usr/bin/systemctl enable kannel.service
/usr/bin/systemctl restart kannel.service
%endif

%post sendmail
# enable sendmail on public ip address
sed -i 's/Port=smtp,Addr=127.0.0.1, Name=MTA/Port=smtp,Addr=0.0.0.0, Name=MTA/g' /etc/mail/sendmail.mc
# serve all available IPs as domains for incoming mail requests, and redirect incoming mail into ictcore mailbox
for domain in `hostname -I`; do echo "$domain localhost" >> /etc/hosts; done
for domain in `hostname -I`; do echo "$domain" >> /etc/mail/local-host-names; done
for domain in `hostname -I`; do echo "@$domain ictcore" >> /etc/mail/virtusertable; done
# who can send email
echo "ictcore" >> /etc/mail/trusted-users
echo "apache" >> /etc/mail/trusted-users
# apply configuration
/etc/mail/make
# enable and start sendmail server
%if %{rhel} < 7
/sbin/chkconfig sendmail on
/sbin/service sendmail restart
%else
/usr/bin/systemctl enable sendmail.service
/usr/bin/systemctl restart sendmail.service
%endif
# alter firewall for smtp
%if %{rhel} < 7
/sbin/iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 25 -j ACCEPT    # smtp
/etc/init.d/iptables save
%else
/bin/firewall-cmd --zone=public --add-port=25/tcp --permanent  # smtp
/bin/firewall-cmd --runtime-to-permanent
/bin/firewall-cmd --reload
%endif

%changelog
* Thu Dec 21 2017 Nasir Iqbal <nasir@ictinnovations.com> - 0.8.0
- Campaign support and APIs added
- Call Transfer application and Agent program added
- Extension support added for accounts
- Sip, SMTP and SMPP added as provider sub-type
- Authentication improved, JWT support added
- Media related APIs improved for file upload / download support
- Rest URL structure improved as per REST standards / recommendations
- CORS (cross origin) support added
- Twig based template added for gateway configurations and Application data

* Tue Sep 20 2016 Nasir Iqbal <nasir@ictinnovations.com> - 0.7.0
- Refactoring, logic and flow and api refactoring (third release)

* Wed Jun 29 2016 Nasir Iqbal <nasir@ictinnovations.com> - 0.6.0
- Rest interface and APIs development
- User guide for REST APIs
- User authentication and authorization support added
- Proprietary license replaced with MPLv2
- Code compilation removed, to make it open source
- CentOs 7 support added

* Thu Mar 5 2015 Nasir Iqbal <nasir@ictinnovations.com> - 0.2.0
- ICTCore 0.2.0 release (second release)
- Program, Application and action introduced
- Kannel gateway support added
- Voice and SMS added as new services

* Fri Oct 31 2014 Nasir Iqbal <nasir@ictinnovations.com> - 0.1.0
- ICTCore 0.1.0 release (first release)
