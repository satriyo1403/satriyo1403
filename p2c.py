#!/usr/bin/env python3

import os, time, re, subprocess, glob

path_repfile     = "/opt/earthworm/run_working/params/"
path_backup_file = path_repfile + "backup/"
eews_message     = path_backup_file + "eew"
push2android     = path_backup_file + "push.php"

#print("cleanning for residual .rep file that still exist")
repdata = re.findall(r"\d{14}_\w{2}.rep", " ".join(os.listdir(path_repfile)))
if len(repdata) !=0 :
   print("found some repfiles and cleanning")
   os.system("mv %s*.rep %s " %(path_repfile,path_backup_file))

def main():
   # Clear log for sender eews message
   sent2cube = 0

   # Check for the directory and script we used inside the main loop
   if not os.path.exists(path_repfile):
      print("*** The rep files directory does not exist! Please create first!!!")
      exit()

   if not os.path.exists(path_backup_file):
      print ("*** The backup directory does not exist; create automatically!")
      subprocess.call(['mkdir', path_backup_file])
      subprocess.call(['chmod', '-R', '777', path_backup_file])

   # Main process loop
   while True:
      repdata = re.findall(r"\d{14}_\w{2}.rep", " ".join(os.listdir(path_repfile)))
      repdata_num = len(repdata)

      if repdata_num == 0:
         print ("No rep data", time.strftime("%Y-%m-%d %H:%M:%S"))
         sent2cube   = 0

      elif len(glob.glob(path_repfile+'*_n3.rep')) >= 1 :
         print("get _n3.rep file")
         print("extract rep files to get the eews message")
         get_repfile = glob.glob(path_repfile+'*_n3.rep')
         print(get_repfile[0])
         os.system(''' sed -n 4,4p %s | awk '{print "21, "$1", "$2", "$3", "$4", "$5", "$6", "$7", "$8", "$9", "$13}' > %s ''' %(get_repfile[0],eews_message))
         print("EEW Message : %s" %(eews_message))
         if sent2cube == 0 :
            print(" Sending eews message into eews sender ") 
            os.system('curl --user eews:1111 --upload-file %s ftp://172.19.1.62/' %(eews_message))
            sent2cube = 1
            extr_eews_msg = open(eews_message, "r")
            data_eews_msg = extr_eews_msg.readline().strip()
            extr_data = data_eews_msg.split(",")
            tahun =  extr_data[1].strip()
            bulan =  extr_data[2].strip()
            tnggl =  extr_data[3].strip()
            jam   =  extr_data[4].strip()
            menit =  extr_data[5].strip()
            detik =  extr_data[6].strip()
            lat   =  extr_data[7].strip()
            long  =  extr_data[8].strip()
            depth =  extr_data[9].strip()
            mpd   =  extr_data[10].strip()
            dec_detik = detik.split('.')[0]
            dec_tnggl = str(tnggl).zfill(2)
            dec_bulan = str(bulan).zfill(2)
            dec_jam   = str(jam).zfill(2)
            dec_menit = str(menit).zfill(2)
            dec_detik = str(dec_detik).zfill(2)

            # update name for xml file
            xml_report = path_backup_file + "eews.xml"
            xml_rep_bakup = path_backup_file + "report_date_" + tahun + dec_bulan + dec_tnggl + dec_jam + dec_menit + dec_detik + ".xml"
            now_time   = time.strftime("%Y-%m-%d %H:%M:%S")

            #### generate xml file ####
            os.system("echo '<?xml version="'"1.0"'" encoding="'"utf-8"'" ?>' > %s" %(xml_report))
            os.system('echo "<earthquake>" >> %s' %(xml_report))
            os.system('echo "   <identifier>BMKG-EEW-%s%s%s%s%s%s</identifier>" >> %s' %(tahun,dec_bulan,dec_tnggl,dec_jam,dec_menit,dec_detik,xml_report))
            os.system('echo "   <schemaVer>IA-BMKG-XML-EEW:1.0</schemaVer>" >> %s' %(xml_report))
            os.system('echo "   <language>en-US</language>" >> %s' %(xml_report))
            os.system('echo "   <event>Earthquake</event>" >> %s' %(xml_report))
            os.system('echo "   <senderName>Data Center</senderName>" >> %s' %(xml_report))
            os.system('echo "   <sent>%s</sent>" >> %s' %(now_time,xml_report))
            os.system('echo "   <status>Actual</status>" >> %s' %(xml_report))
            os.system('echo "   <msgType>Update</msgType>" >> %s' %(xml_report))
            os.system('echo "   <references>%s</references>" >> %s' %(get_repfile,xml_report))
            os.system('echo "   <msgNo>3</msgNo>" >> %s' %(xml_report))
            os.system('echo "   <description></description>" >> %s' %(xml_report))
            os.system('echo "   <originTime>%s-%s-%sT%s:%s:%s</originTime>" >> %s' %(tahun,dec_bulan,dec_tnggl,dec_jam,dec_menit,detik,xml_report))
            os.system('echo "   <epicenter>" >> %s' %(xml_report))
            os.system("echo '       <epicenterLon unit="'"deg"'">%s</epicenterLon>' >> %s" %(long,xml_report))
            os.system("echo '       <epicenterLat unit="'"deg"'">%s</epicenterLat>' >> %s" %(lat,xml_report))
            os.system('echo "   </epicenter>" >> %s' %(xml_report))
            os.system("echo '   <depth unit="'"km"'">%s</depth>' >> %s" %(depth,xml_report))
            os.system('echo "   <magnitude>" >> %s' %(xml_report))
            os.system('echo "       <magnitudeType>Mpd</magnitudeType>" >> %s' %(xml_report))
            os.system('echo "       <magnitudeValue>%s</magnitudeValue>" >> %s' %(mpd,xml_report))
            os.system('echo "   </magnitude>" >> %s' %(xml_report))
            os.system('echo "   <pgaAdj>1.0</pgaAdj> " >> %s' %(xml_report))
            os.system('echo "</earthquake> " >> %s' %(xml_report))
            os.system('chmod +x %s' %(xml_report))

            #### New server android data
            os.system("cp -r %s /var/www/html/jejal/. " %(xml_report))

            #### Push Notification
            os.system("php %s " %(push2android))

            #### Sending data other EEW Sender Server
            os.system('curl --user xxxx:xxxx --upload-file %s ftp://xxx.xxx.xxx.xx/' %(eews_message))
            ### Backup event_xml_file
            os.system("more %s > %s" %(xml_report,xml_rep_bakup))
            os.system("mv %s*.rep %s " %(path_repfile,path_backup_file))


      else:
         repdata = sorted(repdata)
         print ("Found rep : ", ", ".join(repdata)+" "+time.strftime("%Y-%m-%d %H:%M:%S"))

      time.sleep(1)

if __name__ == "__main__":
    main()





