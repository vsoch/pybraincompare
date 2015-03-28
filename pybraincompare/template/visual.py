'''
visual.py: part of pybraincompare package
Functions to visualize in browser

'''
from pybraincompare.template.futils import make_tmp_folder
import SimpleHTTPServer
import SocketServer
import webbrowser


'''View code in temporary browser!'''
def view(html_snippet):
  with make_tmp_folder() as tmp_dir:  
    # Write to temporary file
    tmp_file = "%s/pycompare.html" %(tmp_dir)
    internal_view(html_snippet,tmp_file)

'''Internal view function'''
def internal_view(html_snippet,tmp_file):
  html_file = open(tmp_file,'wb')
  html_file.writelines(html_snippet)
  html_file.close()
  url = 'file://%s' %(tmp_file)
  webbrowser.open_new_tab(url)
  raw_input("Press Enter to finish...")

'''Web server (for Papaya Viewer in QA report'''
def run_webserver(PORT=8000,html_page="index.html"):
  Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
  httpd = SocketServer.TCPServer(("", PORT), Handler)
  print "Serving pybraincompare at port", PORT
  webbrowser.open("http://localhost:%s/%s" %(PORT,html_page))
  httpd.serve_forever()


"""Get svg html from matplotlib figures (eg, glass brain images)"""
def get_svg_html(mpl_figures):
  svg_images = []
  with make_tmp_folder() as tmp_dir:  
    for fig in mpl_figures:
      tmp_svg = "%s/mplfig.svg" %(tmp_dir)
      fig.savefig(tmp_svg)
      fig_data = open(tmp_svg,"rb").readlines()
      svg_images.append(fig_data)
  return svg_images
