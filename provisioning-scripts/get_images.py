#######################################################################
# GROUP 23
# CITY: Melbourne
# MEMBERS:
#  - Vitaly Yakutenko - 976504
#  - Shireen Hassan - 972461
#  - Himagna Erla - 975172
#  - Areeb Moin - 899193
#  - Syed Muhammad Dawer - 923859
#######################################################################
from connect import ec2_conn

images = ec2_conn.get_all_images()
for img in images:
 	print('Image id: {}, image name: {}'.format(img.id, img.name)) 
