rev = '2.11'
release_full_name = rev.split(".")
print release_full_name

if len(release_full_name) == 1:
    release_name = str(int(release_full_name[-1]) + 1)
else:
    release_name = '{product}.{release}'.format(product=release_full_name[0],
                                                release=int(release_full_name[1]) + 1)


print release_name
