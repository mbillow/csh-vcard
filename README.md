CSH LDAP vCard Generator
========================
Built For: [Computer Science House](csh.rit.edu) at RIT


The purpose of this script is to create a web server that is able to respond to HTTP ```GET``` requests on a specified port for a ```<username>.vcf``` file which then returns a properly formatted (according to [RFC 6350](https://tools.ietf.org/html/rfc6350)) vCard Version 3 file. The server is also configured with correct MIME headers (```[text/vcard]```) so browsers will automatically open the vCard file in the Operating System's default contact application.

Images are pulled first from LDAP and then, if the field in LDAP is blank, will pull from Gravatar based on a user's CSH email address. Either image is then encoded in Base 64 and formatted for the vCard file.

**Must run ```kinit``` to grab ticket-granting ticket from kerberos before running the script.**

Uses the CSHLDAP module created by [Matt Gambogi](https://github.com/gambogi).
