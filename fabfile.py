import textwrap
from fabric.api import *
from fabric.contrib import files
from fabric.api import settings
import fabtools
from fabtools.vagrant import vagrant
from fabtools import require
import fabtools.mysql


@task
def install():
#     _rpm_setup()
#     _devtools_install()
#     _utilities_install()
#     _java_install()
#     _fedora_prep()
#     _mysql_install()
#     _php_install()
    _apache_install()

def _rpm_setup():
    # prepare rpm installations
    fabtools.rpm.update()
    require.rpm.package('redhat-lsb-core-4.0-7.el6.centos.x86_64')

def _devtools_install():    
    # development tools
    require.rpm.repository('rpmforge')    
    fabtools.rpm.groupinstall('Development Tools', options='--skip-broken')

def _utilities_install():    
    # install utilities
    utilities = ['puppet', 'wget', 'mlocate']
    require.rpm.packages(utilities)

def _java_install():    
    # Java
    #run('wget http://download.oracle.com/otn-pub/java/jdk/7u2-b13/jdk-7u2-linux-x64.rpm')
    #sudo('sudo yum install jdk-7u2-linux-x64.rpm')
    require.oracle_jdk.installed(version='7u25-b15')
#    require.oracle_jdk.installed(version='7u2')
    sudo('alternatives --install /usr/bin/java java /usr/java/latest/jre/bin/java 20000')
    sudo('alternatives --install /usr/bin/javaws javaws /usr/java/latest/jre/bin/javaws 20000')
#    sudo('alternatives --install /usr/lib/mozilla/plugins/libjavaplugin.so libjavaplugin.so /usr/java/latest/jre/lib/i386/libnpjp2.so 20000')
#    sudo('alternatives --install /usr/lib64/mozilla/plugins/libjavaplugin.so libjavaplugin.so.x86_64 /usr/java/latest/jre/lib/amd64/libnpjp2.so 20000')

def _fedora_prep():     
     # prepare Fedora
    if not fabtools.user.exists('fedora'):
        fabtools.user.create('fedora')
        bash = ['export FEDORA_HOME=/usr/local/fedora','export CATALINA_HOME=/usr/local/fedora/tomcat','export JAVA_OPTS="-Xms1024m -Xmx1024m -XX:MaxPermSize=256m']
        with cd('/home/fedora'):
            files.append('.bash_profile', bash, use_sudo=True)

#     with cd('/home/fedora'):
    fedora_url = 'http://downloads.sourceforge.net/project/fedora-commons/fedora/3.4.2/fcrepo-installer-3.4.2.jar'
    sudo("wget -P /home/fedora '{}'".format(fedora_url))
    
def _mysql_install():
    '''
    Installs mysql and creates databases with credentials
    '''
    
    #require.mysql.server(password='qwerty')
    require.rpm.packages(['mysql', 'mysql-server'])
    sudo('chkconfig mysqld on')
    fabtools.service.start('mysqld')
    mysql_passwd = 'qwerty'
    sudo('/usr/bin/mysqladmin -u root password %s' % (mysql_passwd))
    
    with settings(mysql_user='root',mysql_password='qwerty'):
#     with settings(mysql_user='root',mysql_password=None):
        if not fabtools.mysql.user_exists('drupaldbuser'):
            fabtools.mysql.create_user('drupaldbuser', password='Password123')
        if not fabtools.mysql.user_exists('fedora'):
            fabtools.mysql.create_user('fedora', password='Password123')

        # Drupal databases
        if not fabtools.mysql.database_exists('drupal6_default'):
            fabtools.mysql.create_database('drupal6_default')
        if not fabtools.mysql.database_exists('drupal6_exhibition'):
            fabtools.mysql.create_database('drupal6_exhibition')
        if not fabtools.mysql.database_exists('drupal6_fieldbooks'):
            fabtools.mysql.create_database('drupal6_fieldbooks')
        
        # Fedora databases
        if not fabtools.mysql.database_exists('fedora3'):
            fabtools.mysql.create_database('fedora3')

        fabtools.mysql.query("GRANT ALL ON drupal6_default.* TO drupaldbuser@localhost IDENTIFIED BY 'Password123';")
        fabtools.mysql.query("GRANT ALL ON drupal6_exhibition.* TO drupaldbuser@localhost IDENTIFIED BY 'Password123';")
        fabtools.mysql.query("GRANT ALL ON drupal6_fieldbooks.* TO drupaldbuser@localhost IDENTIFIED BY 'Password123';")
        fabtools.mysql.query("GRANT ALL ON fedora3.* TO fedora@localhost IDENTIFIED BY 'Password123';")
        
def _php_install():
    require.rpm.packages(['php'])
    
    # Expand Key PHP Limits
    files.sed('/etc/php.ini', 'upload_max_filesize = \w+', 'upload_max_filesize = 64M', use_sudo=True)
    files.sed('/etc/php.ini', 'post_max_size = \w+', 'post_max_size = 100M', use_sudo=True)
    files.sed('/etc/php.ini', 'memory_limit = \w+', 'memory_limit = 128M', use_sudo=True)

def _apache_install():
    require.rpm.packages(['httpd'])
    
    if not files.is_dir('/var/www/drupal'):
        sudo('mkdir /var/www/drupal')
    
    httpd_conf = "/etc/httpd/conf/httpd.conf"
    files.sed(httpd_conf, 'DocumentRoot "/var/www/html"', 'DocumentRoot "/var/www/drupal"', use_sudo=True)
    files.append(httpd_conf,'<Directory "/var/www/drupal">', use_sudo=True)
    files.append(httpd_conf,'   Options FollowSymLinks', use_sudo=True)
    files.append(httpd_conf,'   AllowOverride All', use_sudo=True)
    files.append(httpd_conf,'   Order allow,deny', use_sudo=True)
    files.append(httpd_conf,'   Allow from all', use_sudo=True)
    files.append(httpd_conf,'</Directory>', use_sudo=True)

#     files.sed(httpd_conf, '<Directory "/var/www/html">', '<Directory "/var/www/drupal">', use_sudo=True)



#     s = '''\
#         #
#         # DocumentRoot: The directory out of which you will serve your
#         # documents. By default, all requests are taken from this directory, but
#         # symbolic links and aliases may be used to point to other locations.
#         #
#         DocumentRoot "/var/www/html"
#         '''
#     r = '''\
#         #
#         # DocumentRoot: The directory out of which you will serve your
#         # documents. By default, all requests are taken from this directory, but
#         # symbolic links and aliases may be used to point to other locations.
#         #
#         DocumentRoot "/var/www/drupal"    
#         '''
#     files.sed(httpd_conf, textwrap.dedent(s), textwrap.dedent(r), use_sudo=True)
# 
#     s = '''\
#         # First, we configure the "default" to be a very restrictive set of
#         # features.
#         #
#         <Directory />
#             Options FollowSymLinks
#             AllowOverride None
#         </Directory>
#         '''
#     r = '''\
#         # First, we configure the "default" to be a very restrictive set of
#         # features.
#         #
#         <Directory />
#             Options FollowSymLinks
#             AllowOverride None
#         </Directory>
#         '''
#     files.sed(httpd_conf, textwrap.dedent(s), textwrap.dedent(r), use_sudo=True)
# 
#     s = '''\
#         #
#         # Note that from this point forward you must specifically allow
#         # particular features to be enabled - so if something's not working as
#         # you might expect, make sure that you have specifically enabled it
#         # below.
#         #
# 
#         #
#         # This should be changed to whatever you set DocumentRoot to.
#         #
#         <Directory "/var/www/html">
# 
#         #
#         # Possible values for the Options directive are "None", "All",
#         # or any combination of:
#         #   Indexes Includes FollowSymLinks SymLinksifOwnerMatch ExecCGI MultiViews
#         #
#         # Note that "MultiViews" must be named *explicitly* --- "Options All"
#         # doesn't give it to you.
#         #
#         # The Options directive is both complicated and important.  Please see
#         # http://httpd.apache.org/docs/2.2/mod/core.html#options
#         # for more information.
#         #
#             Options Indexes FollowSymLinks
# 
#         #
#         # AllowOverride controls what directives may be placed in .htaccess files.
#         # It can be "All", "None", or any combination of the keywords:
#         #   Options FileInfo AuthConfig Limit
#         #
#             AllowOverride None
# 
#         #
#         # Controls who can get stuff from this server.
#         #
#             Order allow,deny
#             Allow from all
# 
#         </Directory>
#         '''
#     r = '''\
#         #
#         # Note that from this point forward you must specifically allow
#         # particular features to be enabled - so if something's not working as
#         # you might expect, make sure that you have specifically enabled it
#         # below.
#         #
# 
#         #
#         # This should be changed to whatever you set DocumentRoot to.
#         #
#         <Directory "/var/www/drupal">
#             Options FollowSymLinks
#             AllowOverride All
#             Order allow,deny
#             Allow from all
#         </Directory>
#         '''
#     files.sed(httpd_conf, textwrap.dedent(s), textwrap.dedent(r), use_sudo=True)

    sudo('chkconfig httpd on')
    fabtools.service.start('httpd')



@task
def deploy():
    # Require SIdora from github
    #fabtools.require.git.working_copy("https://github.com/Smithsonian/sidora.git")
    fabtools.require.git.working_copy("https://github.com/Smithsonian/sidora-deploy")
    #run("git clone https://github.com/Smithsonian/sidora.git")

@task
def setup():
    # Require git
    fabtools.rpm.install('git')
    
    
    
    
    
##########################    
# Fedora server management
@task
def fc(cmd):
    sudo('/etc/init.d/fcrepo-server %s' % cmd)
    
    
    
    
# Shell provisioning
#   # somehow need to incorporate this: http://cbednarski.com/articles/creating-vagrant-base-box-for-centos-62/
# #  config.vm.provision :shell, :inline => "sudo cp /vagrant/conf/ifcfg-eth0 /etc/sysconfig/network-scripts/ifcfg-eth0"
#   #config.vm.provision :unix_reboot
#   config.vm.provision :shell, :inline => "sudo yum -y update"
#   config.vm.provision :shell, :inline => "sudo yum -y upgrade"
# #  config.vm.provision :shell, :inline => "sudo rpm -Uvh http://packages.sw.be/rpmforge-release/rpmforge-release-0.5.3-1.el5.rf.x86_64.rpm "
#   config.vm.provision :shell, :inline => "sudo rpm -Uvh http://packages.sw.be/rpmforge-release/rpmforge-release-0.5.3-1.el6.rf.x86_64.rpm "
#   config.vm.provision :shell, :inline => "sudo yum -y --skip-broken groupinstall 'Development Tools'"
#   config.vm.provision :shell, :inline => "sudo yum -y install puppet wget mlocate"
# 
#   # Fedora
# 
#   config.vm.provision :shell, :inline => "sudo yum -y install mysql mysql-server"
#   config.vm.provision :shell, :inline => "sudo chkconfig mysqld on"
#   config.vm.provision :shell, :inline => "sudo service mysqld start"
# #/usr/bin/mysqladmin -u root password 'new-password'
# #/usr/bin/mysqladmin -u root -h localhost.localdomain password 'new-password'