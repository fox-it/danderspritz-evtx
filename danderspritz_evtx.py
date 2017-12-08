#!/usr/bin/env python

"""
Copyright 2017, Fox-IT

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice,
this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation
and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING,
BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER
OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT
OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

danderspritz_evtx.py: Parse evtx files and detect use of the danderspritz \
delete event module.

Requires python-evtx (https://github.com/williballenthin/python-evtx)
"""

import argparse

from mmap import mmap, ACCESS_READ
from contextlib import closing
from tempfile import TemporaryFile
from struct import pack, unpack

from Evtx.Evtx import FileHeader
from Evtx.Views import evtx_record_xml_view

__author__ = "Fox-IT"
__year__ = "2017"
__version__ = "1.0"
__status__ = "Final"


# Parse command line interface arguments
def parse_cli_arguments():
  parser = argparse.ArgumentParser(description="danderspritz_evtx.py "
                                               "- Parse evtx files and "
                                               "detect the use of the "
                                               "danderspritz module that "
                                               "deletes evtx entries")

  parser.add_argument('-i', '--input', required=True, action='store',
                      dest='input_path', help='Path to evtx file',
                      type=argparse.FileType('rb'))
  parser.add_argument('-o', '--output', required=False, action='store',
                      dest='output_path', help='Path to corrected evtx file',
                      type=argparse.FileType('wb'))
  parser.add_argument('-e', '--export', required=False, action='store',
                      dest='export_path',
                      help='Path to location to store exported xml records',
                      type=argparse.FileType('w'))

  args = parser.parse_args()
  return args


def temp_evtx_copy(input_path):
  '''
  Create a temporary copy of the input file
  :param input_path: string path to input file
  :return: TemporaryFile
  '''
  try:
    corrected_file = TemporaryFile()
    with input_path as input_file:
      with closing(mmap(input_file.fileno(), 0,
                        access=ACCESS_READ)) as buf:
        # Write complete contents of original file
        corrected_file.write(buf)
    input_file.close()
  except:
    return False
  return corrected_file


def read_evtx_records(evtx_file):
  '''
  Reads an evtx file, extracts the records, and returns them as a generator
  :param evtx_file: string path to input evtx file
  :return: generator
  '''
  evtx_file.seek(0)
  buf = evtx_file.read()
  fh = FileHeader(buf, 0x0)
  for chunk in fh.chunks():
    for record in chunk.records():
      yield record


def main():
  args = parse_cli_arguments()

  print
  print("Reading records from {}...".format(args.input_path.name))

  # try to create a temporary copy of the evtx file
  corrected_file = temp_evtx_copy(args.input_path)

  if not corrected_file:
    print("Could not create temporary file!")
    exit(1)
  else:
    offsets_restored_records = []

    # Loop through corrected file until no changes are needed anymore
    file_ready = False
    while not file_ready:
      # No changes made (since last loop)
      corrected = False

      # loop over the records inside the evtx file
      for record in read_evtx_records(corrected_file):
        # Retrieve the complete contents of this record.
        record_data = record.data()

        # Deleted records are not actually deleted, but are still
        # present within the content of the preceeding record.
        # This is easily spotted by checking for the magic value
        # of a record within the record data.

        # We start searching at the end of the header
        start_pos = 24
        while not corrected:
          magic_pos = record_data.find('\x2a\x2a\x00\x00', start_pos,
                                       record.size() - 28)
          if magic_pos == -1:
            # No magic found
            break
          else:
            # Magic found; this could be a record.
            # If this is in fact a deleted record, a copy the
            # record size of the preceeding record is present
            # just before the magic of the deleted record. We would
            # find the size of the deleted record just after
            # the magic. The position where we found the magic is
            # also the old size of the record.
            cur_size = record.size()
            (old_size,) = unpack('I', record_data[(magic_pos - 4)
                          :magic_pos])
            (del_size,) = unpack('I', record_data[(magic_pos + 4)
                          :(magic_pos + 8)])

            if magic_pos == old_size and \
                            (del_size + old_size) == record.size():
              print(
                'Found a deleted record within record number {}'
                ' at offset 0x{:04X}').format(
                record.record_num(),
                magic_pos)

              # Flag
              corrected = True
              # Restore original size
              corrected_file.seek(record.offset() + 4)
              corrected_file.write(pack('I', old_size))
              # Restore deleted size
              corrected_file.seek(record.offset() + cur_size - 4)
              corrected_file.write(pack('I', del_size))
              # Remember that we restored a record on this offset
              offsets_restored_records.append(
                old_size + record.offset())

            # Find next
            start_pos = magic_pos + 1

      if not corrected:
        file_ready = True
      # Else: if a correction was made, we need to
      # go back and start over,
      # as more records may have been deleted.

    # Dump corrected record
    if args.output_path:
      corrected_file.seek(0)
      with closing(mmap(corrected_file.fileno(), 0, \
                        access=ACCESS_READ)) as buf:
        args.output_path.write(buf)

    # Print all records for which we found a deleted record
    if offsets_restored_records:
      corrected_file.seek(0)
      with closing(mmap(corrected_file.fileno(), 0, \
                        access=ACCESS_READ)) as buf:

        # We simply open the corrected file and enumerate the records
        #  until we found a record which starts on the offset that we
        #  have remembered.
        fh = FileHeader(buf, 0x0)
        for chunk in fh.chunks():
          for record in chunk.records():

            if record.offset() in offsets_restored_records:
              xml = evtx_record_xml_view(record)

              # Export record in XML
              if args.export_path:
                args.export_path.write(xml)

    print


if __name__ == "__main__":
  main()
