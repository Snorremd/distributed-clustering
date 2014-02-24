import math

__author__ = 'snorre'
import subprocess

if __name__ == "__main__":
    # logged_on = subprocess.check_output("who")
    # users = logged_on.splitlines()
    # for user in users:
    #     user = user.decode()
    #     if not user.startswith("snorre"):
    #         print(user)

    f_beta = 2.0
    f_beta = math.pow(f_beta, 2)
    print(f_beta)