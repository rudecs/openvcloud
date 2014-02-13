import sys
import struct
import os


class Qcow2():  
    #object representing a qcow2, at this moment only readonly!


    def __init__(self, filename):
        qcow2header = struct.Struct(">IIQIIQIIQQIIQ")
        data = self._read_data(filename, qcow2header.size)
        if (len(data) < qcow2header.size) or not data.startswith('QFI'):
           raise 'Invalid header this is not a correct qcow2 file.'
        unpackeddata = qcow2header.unpack(data)
        self.path = filename
        self.magic = unpackeddata[0]
        self.version = unpackeddata[1]
        self.backing_file_offset = unpackeddata[2]
        self.backing_file_size = unpackeddata[3]
        self.cluster_bits = unpackeddata[4]
        self.size = unpackeddata[5]
        self.crypt_method = unpackeddata[6]
        self.l1_size = unpackeddata[7]
        self.l1_table_offset = unpackeddata[8]
        self.refcount_table_offset = unpackeddata[9]
        self.refcount_table_clusters = unpackeddata[10]
        self.nb_snapshots = unpackeddata[11]
        self.snapshots_offset = unpackeddata[12]

        self.backing_file_path = self._read_data(filename, self.backing_file_size, self.backing_file_offset)

    def _read_data(self, filename, size, offset=0):
        try:
            f = open(filename, 'r')
            f.seek(offset)
            data = f.read(size)
            f.close()
            return data
        except:
            f.close()
            raise 'A error occured during reading of the file'


    def get_parents(self):
        """
        Function returns the parents of this file a ordered list of Qcow2 objects is returned
        """
        parent = True
        parents = []
        if self.backing_file_path:
            backingfile = self.backing_file_path
        else:
            return parents
        while(backingfile):
            backingqcow2 = Qcow2(backingfile)
            parents.append(backingqcow2)
            backingfile = backingqcow2.backing_file_path
        return parents











