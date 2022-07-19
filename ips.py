## importing socket module
from this import s
import geocoder
import socket
from gmplot import gmplot
from apis.twilio import send_mail

def get_ip(ip_address,goba_update_maillist):

    print(f"IP Address: {ip_address}")

    ip = geocoder.ip(ip_address)
    cords=ip.latlng
    gmap = gmplot.GoogleMapPlotter(cords[0],cords[1], 13)
    # Add a marker
    gmap.marker(cords[0],cords[1], 'cornflowerblue')
    # Draw map into HTML file
    gmap.draw("templates/map.html")
    link="https://gobawebtool.herokuapp.com/ip-display"
    mess=" <h3 style='color:red;'> Someone is trying to access to the system. </h3> \n <h4> details </h4>:<u> <a href={} style='color:blue;'> Go to location </a> </u>".format(link)
    HTML="<html><head></head><body>{}</body></html>".format(mess)
    send_mail("gobacapital.it@gmail.com",goba_update_maillist,subject="Alert notification",html_content=HTML)
