old = open("s3-uris.txt", "r").readlines()
new = open("new-uris.txt", "r").readlines()

filtered = [uri for uri in new if uri not in old]




with open('filtered-uris.txt', 'w') as f:
    for filt in filtered:
        f.write(f"{filt}")
