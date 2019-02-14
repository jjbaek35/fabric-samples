from subprocess import call
import subprocess 

result = subprocess.check_output ('node send.js PMU10000 21312 12312 23423' , shell=True);
print result;
