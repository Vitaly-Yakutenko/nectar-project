from connect import ec2_conn

images = ec2_conn.get_all_images()
for img in images:
 	print('Image id: {}, image name: {}'.format(img.id, img.name)) 
