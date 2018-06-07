""" 
 Angelis Pseftis
 v3
 Change Notes:
 --Works with Python 3.6
 --Added argparse vs sys.argv[x] : functionally identical
"""

from xml.etree import ElementTree as et
import sys
import os
import json
import argparse


def compute(ele):
    """ 
        compute the string tag equivalent
    """
    ele_string = ele.tag + " " + json.dumps(ele.attrib)
    return ele_string


class XMLCombiner(object):
    def __init__(self, filenames):
        assert len(filenames) > 0, 'No filenames!'
        self.roots = [et.parse(f).getroot() for f in filenames]

    def combine(self):
        for r in self.roots[1:]:
            self.combine_element(self.roots[0], r)
        return et.tostring(self.roots[0])

    def combine_element(self, one, other):
        mapping = {compute(el): el for el in one}
        for el in other:
            ele_string = compute(el)
            if len(el) == 0:
                try:
                    mapping[ele_string].text = el.text
                except KeyError:
                    mapping[ele_string] = el
                    one.append(el)
            else:
                try:
                    self.combine_element(mapping[ele_string], el)
                except KeyError:
                    mapping[ele_string] = el
                    one.append(el)


def filter(files):
    for file in files:
        r = open(file,'r').read()
        r = r.replace("cm:compliance","cmcompliance")
        r = r.replace("xmlns:cm","xmlnscm")
        w = open(file,'w')
        w.write(r)
        w.flush()
        w.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory",help="Enter --directory followed by path")
    args = parser.parse_args()
    if args.directory:
        directory = os.path.abspath(args.directory)
        results = []
        results += [os.path.abspath(os.path.join(directory,each)) for each in os.listdir(directory) if each.endswith('.nessus')]
        print (results)
        filter(results)
        r = XMLCombiner(tuple(results)).combine()
        r = r.replace(b"cmcompliance",b"cm:compliance")
        r = r.replace(b"xmlnscm",b"xmlns:cm")
        f = open("output.nessus","w")
        f.write(str(r, 'utf-8'))
        f.flush()
        f.close()
