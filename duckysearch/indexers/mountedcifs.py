from subprocess import check_output
import os.path
from . import localfs
from .. import ldaphelper


class Mountedcifs(localfs.Localfs):

    # Docs on SID's: https://msdn.microsoft.com/en-us/library/windows/desktop/aa379649(v=vs.85).aspx

    ACE_ACCESS_ALLOWED = 0
    ACE_ACCESS_DENIED = 1

    # Types from https://github.com/Distrotech/cifs-utils/blob/distrotech-cifs-utils/cifsacl.h

    # D | RC | P | O | S | R | W | A | E | DC | REA | WEA | RA | WA
    ACE_TYPE_FULL_CONTROL = 0x001f01ff

    # RC | S | R | E | REA | RA
    ACE_TYPE_EREAD = 0x001200a9

    # RC | S | R | E | REA | GR | GE
    ACE_TYPE_OREAD = 0xa01200a1

    # RC | S | R | REA | RA
    ACE_TYPE_BREAD = 0x00120089

    # W | A | WA | WEA
    ACE_TYPE_EWRITE = 0x00000116

    # D | RC | S | R | W | A | E |REA | WEA | RA | WA
    ACE_TYPE_CHANGE = 0x001301bf

    # GR | RC | REA | RA | REA | R
    ACE_TYPE_ALL_READ_BITS = 0x80020089

    # WA | WEA | A | W
    ACE_TYPE_ALL_WRITE_BITS = 0x40000116

    def process_file(self, path, file):
        id, info = super(Mountedcifs, self).process_file(path, file)
        info.update(self.cifs_info(path, file))

        return id, info

    def cifs_info(self, path, file):
        output = check_output(['getcifsacl', '-r', os.path.join(path, file)])

        acl = self.parse_cifsacl(output)
        allowed = self.acl_sids(self.filter_acl_read(acl, self.ACE_ACCESS_ALLOWED))
        denied = self.acl_sids(self.filter_acl_read(acl, self.ACE_ACCESS_DENIED))

        info = {'read_allowed': allowed, 'read_denied': denied}

        return info

    def parse_cifsacl(self, data):
        '''Parse Access Control List'''
        read_perms = []

        for line in data.split("\n"):
            user = self.parse_cifsace(line)
            if (user):
                read_perms.append(user)

        return read_perms

    def parse_cifsace(self, line):
        '''Parse Access Control Entry'''
        parts = line.split(':')
        ace = {}

        if (parts[0] == 'ACL'):
            ace['sid'] = parts[1]

            if ace['sid'][:1] != 'S':
                raise Exception('Access Control Entry does not contain an SID')

            permission_parts = parts[2].split('/')

            # convert hex strings to int
            ace['access'] = int(permission_parts[0], 0)
            ace['mask'] = int(permission_parts[2], 0)

            return ace

    def filter_acl_read(self, acl, ace_access):
        for ace in acl:
            # check if access allowed
            if ace['access'] != ace_access:
                continue

            # check for read access
            if (((ace['mask'] & self.ACE_TYPE_FULL_CONTROL) != self.ACE_TYPE_FULL_CONTROL)
                    and ((ace['mask'] & self.ACE_TYPE_EREAD) != self.ACE_TYPE_EREAD)
                    and ((ace['mask'] & self.ACE_TYPE_BREAD) != self.ACE_TYPE_BREAD)
                    and ((ace['mask'] & self.ACE_TYPE_OREAD) != self.ACE_TYPE_OREAD)):
                continue

            yield ace

    def acl_sids(self, acl):
        return [ace['sid'] for ace in acl]
