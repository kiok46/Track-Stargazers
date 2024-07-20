import urllib.request
import json
import datetime
import os

def main(number_of_files):
    """
    Merge the data from all the json files.
    """
    all_users = [] # Valid users
    all_unique_users = []

    def clear_data_files():
        """
        This is optional, if you want to delete your entire data then
        call this method before main ends.
        """
        for i in range(number_of_files):
            try:
                os.remove("jsons/data_{}.json".format(i))
            except:
                print ("unable to remove file number {}".format(i))

    for i in range(number_of_files):
        try:
            if not os.path.exists("jsons"):
                os.makedirs("jsons")
            with open("jsons/data_{}.json".format(i), "r") as datafile:
                data = json.load(datafile)
            for d in data["users"]:
                if d["user"] in all_unique_users:
                    pass
                else:     
                    l = {"user": d["user"],
                         "country": d["country"]}
                    all_unique_users.append(d["user"])
                    all_users.append(l)

            datafile.close()
        except Exception as e:
            print (e)
            pass

    year = str(datetime.datetime.now().year)
    month = str(datetime.datetime.now().month)
    day = str(datetime.datetime.now().day)

    with open("data/stargazers.js", "w", encoding='utf-8') as js_file:
        js_file.write("var DATA = { users:")
        js_file.write(str(all_users))
        js_file.write(", created_at: new Date(%s, %s, %s) };" % (year, month, day))

    js_file.close()

    # clear_data_files()

if __name__ == "__main__":
    """
    Command: python3 merge_data.py 2

    Argument 1: Number of files you want to merge.

    """
    import sys
    number_of_files = int(1)
    main(number_of_files)
