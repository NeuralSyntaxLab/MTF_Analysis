The Project aims to measure the quality of the in-lab made miniscope.
to quantify the quality of the miniscope we use Modulation Transfer Function (MTF). The analasys is done by placing the miniscope on a stage made for that propose,
and using the MTF analysis app that is implemented in this reposatory, take a series of pictures of the airforce target while it is located above the flueorscent slide.

![T-20-final-rev-1](https://github.com/user-attachments/assets/ba2381ab-a2bf-4d7e-98e7-2732af19a851)

The series of picture should be of different airforce targets, in differeent line pairs per milimeter values (LPS), to create a graph of the regression in contranst as function of 
decreasing LPS values.

ALGORITHM
After a picture is sent to the algorithm, it is first align the lines to be verticals as much as possible, both by getting help from the user, but also by
an algorithm that is trying to minimize the x-axis distance between lines: 
