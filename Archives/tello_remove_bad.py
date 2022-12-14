import os
import cv2
from shutil import move

def remove_bad_images(name, chessboard_size, frame_size):
    img_location = f'telloImages_{name}'
    DELETED_DIR = os.path.join(img_location, f'deleted_pics_')
    # Arrays to store object points and image points from all the images.
    # UNUSED LISTS FOR NOW
    objpoints = []  # 3d point in real world space
    imgpoints = []  # 2d points in image plane.
    #total img counter
    counter = 0
    #images with found chessboards counter
    ret_counter = 0
    
    #if deleted file path doesn't exist, create
    if not os.path.exists(DELETED_DIR):
        os.makedirs(DELETED_DIR)
        
    # get list of files in image directory, but only keep the ones that end in .png
    image_dirs = os.listdir(img_location)
    files_with_images = [x for x in image_dirs if x.endswith(".png")]
    
    #establish dir length before modifying
    dir_length = len(files_with_images)
    
    #for file in dir list
    for afile in files_with_images:
        img = cv2.imread(os.path.join(img_location, afile))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Find the chess board corners
        ret, _ = cv2.findChessboardCorners(gray, chessboard_size, None)
        #if chessboard found
        if ret:
            ret_counter +=1
            
        #if not found
        else:
            print(f"{afile} - no chessboard found")
            src = os.path.join(img_location, afile)
            dest = os.path.join(DELETED_DIR, afile)
            move(src, dest)
        #total counter increment
        counter += 1
        #print loading percent
        if counter % int(dir_length/4) == 0:
            print(f"loading : {(counter/dir_length)*100}%")
    #print total chessboards found
    print(f"{ret_counter} chessboards found out of {dir_length} images.")
