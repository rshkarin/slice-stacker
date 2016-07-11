import os
import re
import sys
import argparse

import numpy as np
import fabio as fb
import nibabel as nib

def open_data(filepath):
    _, glob_ext = os.path.splitext(os.path.basename(filepath))
    data = None

    if glob_ext == '.raw':
        name, bits, size, ext = parse_filename(filepath)
        data_type = np.float32 if bits == 32 else np.uint8
        data = np.memmap(filepath, dtype=data_type, shape=tuple(reversed(size)))
    elif glob_ext == '.nii.gz' or glob_ext == '.nii' or glob_ext == '.gz':
        print filepath
        data = nib.load(filepath).get_data()
    else:
        print 'Incorrent file format, or filename.'

    return data

def create_raw_stack(dirpath, prefix):
    if os.path.exists(dirpath):
        files = [f for f in os.listdir(dirpath) if prefix in f]
        files.sort()

        _shape = fb.open(os.path.join(dirpath, files[0])).data.shape

        stack_data = np.zeros((len(files), _shape[1], _shape[0]), dtype=np.float32)

        for i in np.arange(stack_data.shape[0]):
            stack_data[i] = fb.open(os.path.join(dirpath, files[i])).data.astype(np.float32)
            print 'Converted slices %d' % i

        return stack_data
    else:
        print 'No dir: %s' % dirpath
        return None

def parse_filename(filepath):
    basename, ext = os.path.splitext(os.path.basename(filepath))

    comps = basename.split('_')
    size = tuple([int(v) for v in comps[-1:][0].split('x')])
    bits = int(re.findall('\d+', comps[-2:-1][0])[0])
    name = '_'.join(comps[:-2])

    return name, bits, size, ext

def convert_data(dir_path, prefix, out_path, filename):
    print '---- Raw stack creation is started -----'

    raw_data_stack = create_raw_stack(dir_path, prefix)

    bits = 32 if raw_data_stack.dtype == np.float32 else 8

    if not os.path.exists(out_path):
            os.makedirs(out_path)

    full_out_path = os.path.join(out_path, "%s_%dbit_%dx%dx%d.raw" % \
            (filename, bits, raw_data_stack.shape[2], raw_data_stack.shape[1], raw_data_stack.shape[0]))

    raw_data_stack.tofile(full_out_path)

    print 'Written to {0}'.format(full_out_path)
    print '---- Raw stack creation is finished -----'
    del raw_data_stack

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--input_dir", help="path to a folder containing files", required=True)
    parser.add_argument("-p", "--prefix", help="files' prefix", required=True)
    parser.add_argument("-f", "--filename", help="name of an output file", required=True)
    parser.add_argument("-o", "--output_dir", help="path to an output folder", required=True)

    args = parser.parse_args()

    convert_data(args.input_dir, args.prefix, args.output_dir, args.filename)

if __name__ == "__main__":
    sys.exit(main())
