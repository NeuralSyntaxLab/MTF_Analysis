## Project Overview

This project aims to measure the quality of a lab-made Miniscope.
To quantify the optical performance of the Miniscope, we use the Modulation Transfer Function (MTF).

The analysis is performed by placing the Miniscope on a dedicated stage designed for this purpose, and using the MTF analysis app provided in this repository. A series of images are captured of an Air Force target positioned over a fluorescent slide.

![AirForce tagret with different LPS levels](https://github.com/user-attachments/assets/b7c5e5cd-c980-454b-ad8d-6f81b2c97a67)


The image series should include different Air Force targets, each with different line pairs per millimeter (LPS) values. This enables the generation of a graph showing the decline in contrast as a function of increasing spatial frequency (LPS).

#### Algorithm
Once an image is sent to the algorithm, it is first aligned vertically. This is done with assistance from the user, as well as an automatic alignment process that minimizes the x-axis distance between lines. This alignment step is implemented in the 'preprocess_image.py' file.
![The reduce in x-axis distance align the line vertically](https://github.com/user-attachments/assets/14dddbc9-c96f-4b5b-b36a-173ba0c09cfe).
After alignment, we average the pixel intensities along the y-axis to produce a 1D signal representing the mean intensity as a function of column position (x-axis). This reduction simplifies the analysis:
![intensity as function of x-axis coordinate](https://github.com/user-attachments/assets/79a179bf-24b3-417c-95fa-5febd242ef9d)
We then compute the MTF by measuring the contrast between neighboring peaks, maxima peak and the closest minima peak to its right. The final score is calculated by the average score of contrast of all maxima-minima pairs, in our standard air force target there should be 5 such pairs for each LPS value.This contrast quantifies the sharpness of the image. The score of an image is bounded 0-100, and we anticipate higher MTF scores for targets with lower LPS values.
![MTF function](https://github.com/user-attachments/assets/fd0727cb-b91a-42d1-81b2-8dc46e549b57)
All this part, is implemented in the 'score_photo.py' file.

#### Connecting the Miniscope and Stage Placing
First, connect the arduino, both with the voltage cable and the 3 colors cable. Then, connect the miniscope with the flux cable to the arduino.
Place the flourecent slide, in the middle of the airforce target stage, in its dedicated cranny then place the airforce target over it.
place the miniscope in the holder, and make sure that the holder lower part is as high as it can get, then make sure that the miniscope objective len is in 
its hole and close the screws on it. make sure that the miniscope is well held and can not move.
using the 3 handels, steer the airforce target to be directly over an airforce target lines. precise the highet of the miniscope above the target to get
the maximal resolution.

#### The MTF Analysis App

After pressing start on the home window, you will be asked to choose the LPS targets you want to analyse. Options are all the above 23 options of the 
airforce target the we have in the lab. We recommend to asses on LPS values from both ends of the scale to see the regression of the MTF score. To change the
possible LPS values you can change the 'LPS' array variable in the 'main.py' file.
after confirming the LPS values to assess, the camera window will pop. **If you dont see an image on the window, please check the miniscope connection. if this does not help, try to change the argument for the 'cv2.videoCapture(n)' function in 'main.py' (currently in line 57):
![VideoCapture](https://github.com/user-attachments/assets/d5250d84-f9fd-4d9b-984c-a73ae7e6cac1)

The first step of the user should be finding the apropriate power of the led light, to get the best results. To turn on the light, you first need to select the currect COM port, then press on the connect bottun. You should get a message that the port had a succesful connection. after that, set the LED power using the scale.
![LED control panel](https://github.com/user-attachments/assets/1f1b1d7f-77eb-4c7a-9a2a-7b418d5491a1)

The App will ask you take a picture of a certain LPS target. 
After the picture is taken, a window asking if you are statisfied with the result will pop, if you press continue, the app will ask the user to draw a line paralel to the Target lines, to align them vertically:
![stripe alignment](https://github.com/user-attachments/assets/bdb9a42f-de79-45fc-b989-d186d479ea7d)
Then, the app will ask the user to crop the picture. Please crop to a smaller picture that contains the lines only (suppose to be 5 lines) from the sharpest are of the picture:
![cropping the picture](https://github.com/user-attachments/assets/b8c1e15f-6044-45c3-a6ca-5cd2f10dd5fb)
After this, the code will try to optimize the alingment and score the picture.
if the picture could not be scored the app will ask the user to skip on that LPS value, or retry with a new pictue.
If the picture was scored succesfully, a window with the score will pop up, and after that the user will be asked to repeat the process on the next LPS value.
After all the images were scored, the app will ask to save a CSV table that holds the results, and a figure of the scoring will be displayed:
![MTF score as function of LPS](https://github.com/user-attachments/assets/d8d4c3e7-94f1-479c-a809-c57b6a2b6491)

For any questions please contact Itamar Nini at: itamar.nini@weizmann.ac.il






