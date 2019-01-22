
import sys
import getopt
import scribus

# https://pypi.org/project/xvfbwrapper/  
#from xvfbwrapper import Xvfb
#
#with Xvfb() as xvfb:
#    # launch stuff inside virtual display here.
#    # It starts/stops around this code block.
    
# print(sys.argv)

text_usage = "scribus -g -py " + sys.argv[0] + " -pa -o <outputfile.pdf> -pa -t <text place holder> <inputfile.sla>"
pdf_file = ''
text_placeholder = ''

try:
  opts, args = getopt.getopt(sys.argv[2:],"ho:t:v:",["output=", "text="])
except getopt.GetoptError:
  print "exceptin"
  print(text_usage)
  sys.exit(2)

for opt, arg in opts:
  if opt == "-h":
     print(text_usage)
     sys.exit()
  elif opt in ("-o", "--output"):
     pdf_file = arg
  elif opt in ("-t", "--text"):
     text_placeholder = arg

print "pdf-file %s text %s" % (pdf_file,text_placeholder)

if (pdf_file == "") :
     print(text_usage)
     print opts
     sys.exit()

if scribus.haveDoc() :
    #scribus.setText(text_placeholder, "placeholder")
    pdf = scribus.PDFfile()
    pdf.file = pdf_file
    pdf.save()
else :
    print("No file open")
