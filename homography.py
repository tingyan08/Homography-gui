import os
import cv2
import numpy as np



def show_xy(event,x,y,flags,userdata):
    if event == cv2.EVENT_LBUTTONDOWN:
        dst.append([x, y])

def unwarp(img, src, dst):
    """
    Args:
        img: np.array
        src: list
        dst: list
    Returns:
        un_warped: np.array
    """
    h, w = img.shape[:2]
    M = cv2.getPerspectiveTransform(np.array(dst).astype(np.float32), np.array(src).astype(np.float32))
    max_v = np.max(src, axis=0)
    W, H = int(max_v[0]), int(max_v[1])
    un_warped = cv2.warpPerspective(img, M, (W, H), flags=cv2.INTER_LINEAR)

    return un_warped


if __name__ == '__main__':
    path = "./images"
    for i in os.listdir(path):
        dst = []
        whole_path = os.path.join(path, i)
        img = cv2.imread(whole_path)

        cv2.namedWindow("image", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("image", 744, 1120)
        cv2.imshow("image", img)
        cv2.setMouseCallback('image', show_xy) 
        cv2.waitKey(0)

        un_warp = unwarp(img, dst)
 
        

        cv2.namedWindow("warp", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("warp", 870, 800)
        cv2.imshow("warp", un_warp)
        cv2.waitKey(0)

        cv2.imwrite(whole_path.replace(path, "crop"), un_warp)
        cv2.destroyAllWindows()
   