import glob
import MySQLdb
import subprocess

connection = MySQLdb.connect(host="localhost", user="lightshow", passwd="lightshow", db="lightshow")
cursor = connection.cursor()
file_id = connection.insert_id() + 1

files_to_analyze = glob.glob("./wav/*.wav")

length = len(files_to_analyze)
print 'Analyzing',length,'audio files...'

count = 1
for file in files_to_analyze:
    print 'Processing file',count,'of',length,file
    file = file.replace(" ", "\ ")
    command = "aubio onset "+file+" > ./onset/"+str(file_id)+".txt"
    return_code = subprocess.call(command, shell=True)