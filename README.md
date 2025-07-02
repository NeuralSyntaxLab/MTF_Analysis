The Project aims to measure the quality of the in-lab made miniscope.
to quantify the quality of the miniscope we use Modulation Transfer Function (MTF).
The analasys is done by placing the miniscope on a stage made for that propose,
and using the MTF analysis app that is implemented in this reposatory, take a series of pictures of the airforce target while it is located above the flueorscent slide.

![AirForce tagret with different LPS levels](https://github.com/user-attachments/assets/b7c5e5cd-c980-454b-ad8d-6f81b2c97a67)


The series of picture should be of different airforce targets, in differeent line pairs per milimeter values (LPS), to create a graph of the regression in contranst as function of 
decreasing LPS values.

ALGORITHM
After a picture is sent to the algorithm, it is first align the lines to be verticals as much as possible, both by getting help from the user, but also by
an algorithm that is trying to minimize the x-axis distance between lines. All this process is coded in the preprocess_image.py file.
![The reduce in x-axis distance align the line vertically](https://github.com/user-attachments/assets/14dddbc9-c96f-4b5b-b36a-173ba0c09cfe).
After aliginig the lines vertically, we averaging the pixel intensity across the y-axis, to get a function of the mean intensity as function of column.
That way, we reduce the image to 1-d vector, that can be visualize:
![intensity as function of x-axis coordinate](https://github.com/user-attachments/assets/79a179bf-24b3-417c-95fa-5febd242ef9d)
Then, we can calculate the MTF, whice quantify the contrast between neibhoring peak points, to assess how sharp the picture is. abviously, we excpect the
score to be higher for lower LPS values.
![MTF function](https://github.com/user-attachments/assets/fd0727cb-b91a-42d1-81b2-8dc46e549b57)




