Ducky
=====

Requirements
------------

 * pipenv
 * flask
 * python-ldap

mountedcifs:

 * getcifsacls

Development
-----------

To start the web interface: 

 $ pipenv run ./ducky.py --webserver indexname

An elastic search server can be started with docker:

 $ docker run docker.elastic.co/elasticsearch/elasticsearch:6.0.0

LDAP Notes
----------

 # connect to ldap
 import ldap
 conn = ldap.initialize('ldap://yourldapserver')
 conn.set_option(ldap.OPT_REFERRALS, 1)

 # auth
 conn.bind_s(username, password)

 # get user info
 info_result_id = conn.search('ou=ARI,dc=ari,dc=local', ldap.SCOPE_SUBTREE, 'cn=username', ['cn', 'objectSid', 'memberof'])
 info_results = conn.result(search_result_id)

 # find user groups
 groups_result_id = conn.search('ou=ARI,dc=ari,dc=local', ldap.SCOPE_SUBTREE, '(|(cn=IT)(cn=Webteam)(cn=sshusers))', ['cn', 'objectSid'])
 groups_results = conn.result(groups_result_id)

