# Author : Rahul Bhadani
# Initial Date: March 2, 2020
# About: bagreader class to read  ros bagfile and extract relevant data
# License: MIT License

#   Permission is hereby granted, free of charge, to any person obtaining
#   a copy of this software and associated documentation files
#   (the "Software"), to deal in the Software without restriction, including
#   without limitation the rights to use, copy, modify, merge, publish,
#   distribute, sublicense, and/or sell copies of the Software, and to
#   permit persons to whom the Software is furnished to do so, subject
#   to the following conditions:

#   The above copyright notice and this permission notice shall be
#   included in all copies or substantial portions of the Software.

#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
#   ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
#   TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
#   PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
#   SHALL THE AUTHORS, COPYRIGHT HOLDERS OR ARIZONA BOARD OF REGENTS
#   BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN
#   AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#   OR OTHER DEALINGS IN THE SOFTWARE.

__author__ = 'Rahul Bhadani'
__email__  = 'rahulbhadani@email.arizona.edu'

def slotvalues(m, slot):
    vals = getattr(m, slot)
    try:
        slots = vals.__slots__
        varray = []
        sarray = []
        for s in slots:
            vnew, snew = slotvalues(vals, s)
            if isinstance(snew, list):
                for i, snn in enumerate(snew):
                    sarray.append(slot + '.' + snn)
                    varray.append(vnew[i])
            elif isinstance(snew, str):
                sarray.append(slot + '.' + snew)
                varray.append(vnew)
        return varray, sarray
    except AttributeError:
        return vals, slot
      
def divide_message(msg):
    """ Divide message into name index """
    vals = []
    cols = []
    slots = msg.__slots__
    for s in slots:
        v, s = slotvalues(msg, s)
        if isinstance(s, list):
            for i, s1 in enumerate(s):
                vals.append(v[i])
                cols.append(s1)
        else:
            vals.append(v)
            cols.append(s)
    return vals, cols