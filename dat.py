#! python
# coding=utf-8
"""
"Decode" DAT files for "C-Control I" that contain scrambled assembly "system tokens" as generated by bpp.exe.
Unscrambled "system tokens" (usually 255) are ASCII integer decimals from "0"..."255" separated by space (" "), just like the "program data tokens".
The scrambled token string begins with "SCU " and is approximately twice as long as the unscrambled one. 
Each character from the original is XORed with a byte from a key string, the result is written as hex value (e.g. "3F"). 
Decoding is achieved by the reverse operation. It appears that an additional 0 (zero) token is generated at the end.
The resulting cleartext tokens can be transferred to the CPU with a simple serial protocol (as with CCTrans32.exe, which handles both types of files.).
In essence, this frees you from having to use CCTrans32.
*  not well-tested
*  No warranty, use at your own risk
"""


def chunks(l, n):
  """Yield successive n-sized chunks from l."""
  for i in range(0, len(l), n):
    yield l[i:i+n]



class dat():
  """ Read, decode, write .dat file. """
  
  # CCTrans32.exe shows the cleartext key in an error message if provided with the string "SCU 00..."
  key = "HCC782370532589511EMCCBPPCCASM2005"
  
  def __init__(self):
    """  """
    self.filename = None


  def __repr__(self):
    """  """
    return "<DAT:" + str( self.filename ) + ">"


  def read(self, filename):
    """ Read .dat file """
    self.filename = filename

    with open( filename, 'r', encoding="latin-1", newline="\r\n" ) as f:      
      self.CPU          = f.readline()
      self.programcount = f.readline()
      self.program      = f.readline()
      self.systemcount  = f.readline()
      self.system       = f.readline()
      
      if self.system.startswith("SCU"):
        self.encoded = True



  def decode(self):
    """ Decode system tokens. """
    
    if not self.filename:
      print("ERROR: no file read.")
      return
    
    if not self.encoded:
      print("WARNING: system tokens are not encoded")
      return
    
    # 
    decoded = ""
    token = ""
    tokens = 0
    
    # get data from .dat file line: "SCU <DATA>\r\n"
    stringtokens = self.system.strip().replace(" ", "")[3:]
    # split DATA into list of hex bytes
    bytetokens = list( chunks(stringtokens, 2) )
    # iterate
    for n,t in enumerate( bytetokens ):
      # XOR each byte with the corresponding key character
      value = int(t, 16) ^ ord( self.key[ n % len(self.key) ] )
    
      # actual decoded character
      c = chr( value )
      # must be digit or space
      if c not in "0123456789 ":
        print("ERROR: illegal character from code", t, "at", n)
      # space separates tokens (numbers)
      if c == " ":
        tokens += 1
        if tokens > int( self.systemcount.strip() ):
          print( "Ignoring token {}/{}: '{}', followed by SPACE {}='{}' at {}/{}".format( tokens, int( self.systemcount.strip() ), token, t, c, n, len(bytetokens)-1 ) )
          if int(token) != 0:
            print("WARNING: last value is not zero! ")
          break
        else:
          # append token to output
          decoded += token
        
        # clear token
        token = ""
      
      # append decoded character to token
      token += c
    
    # overwrite input line with decoded line
    self.system = decoded + "\r\n"
    
    
    
  def encode(self):
    """ Not implemented """
    
    if not self.filename:
      print("ERROR: no file read.")
      return
    
    if self.encoded:
      print("WARNING: system tokens are encoded already")
      return
    
    print("WARNING: not implemented yet")
  
  
  
  def write(self, filename):
    """ Write data to file """
    
    if not self.filename:
      print("ERROR: no file read.")
      return
    
    with open( filename, 'w', encoding="latin-1", newline="" ) as f:
      f.write( self.CPU )
      f.write( self.programcount )
      f.write( self.program )
      f.write( self.systemcount )
      f.write( self.system )
  
  
  def compare(self, filename):
    """ Not implemented. """
    #print("[Comparing", self.filename, "with", filename, "...]")
    print("WARNING: not implemented yet")


if __name__ == "__main__":

  import sys
  
  try:
    rf = sys.argv[1]
  except IndexError:
    print("Error: no input file given.")
    sys.exit()
  
  try:
    wf = sys.argv[2]
  except IndexError:
    wf = None
  
  d = dat()
  d.read( rf )
  d.decode()
  d.write( wf )
  