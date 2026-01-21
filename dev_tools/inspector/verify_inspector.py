import subprocess
import sys

def verify():
    # We will pipe "continue\n" to the inspector test
    cmd = [sys.executable, "inspector.py"]
    
    # "continue" is the default or explicit choice
    input_str = "continue\n"
    
    process = subprocess.Popen(
        cmd, 
        stdin=subprocess.PIPE, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        text=True
    )
    
    stdout, stderr = process.communicate(input=input_str)
    
    print("STDOUT:", stdout)
    print("STDERR:", stderr)
    
    if "Resulting Data: {'action': 'buy', 'symbol': 'AAPL', 'qty': 100}" in stdout:
        print("Verification Successful: Data passed through unchanged via 'continue'.")
    else:
        print("Verification Failed.")
        sys.exit(1)

if __name__ == "__main__":
    verify()
