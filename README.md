# Automation_in_socks_label_validation 

# THEME: MACHINE LEARNING

This is a project for socks card label validation where the socks card is validated comparing with the correct socks card whose coordinates are stored in the database. When the test socks card is compared with the correct socks card(master socks card) the software checks whether both test and master socks card mathches or not.

For comparing the test socks card with the master socks card, we first mark the coordinates of each feature(text,image) and store the coordinates in the database.

Then a test socks card before being validated is first detected from the image by applying object detection using <b>machine learning</b>. After the test socks card alone is cropped from the image, the test socks card is compared with the master socks card using the following techniques like:
<ol>
  <li>Object Detection using YOLO-with the help of machine learning we are separating the test socks card from the background.</li>
  <li>Template matching - is done for identifying the position of a particular feature by using the coordinates of the corresponding feature of the master socks card.</li>
  <li>Feature matching done by finding the mse between the two images - is done after template matching for comparing the images present in the test socks card with that of the master socks card.</li>
  <li>Text recognition using Optical Character Recognition(OCR) - is done after template matching for comparing the text information present in the test socks card with that of the master socks card.</li>
    <li>Colour Matching - is done after text recognition to compare the background colour of the text in test socks card with that of master socks card.</li>
</ol>
  
If any one of the features is not matched with the corresponding feature of the master socks card then the test card is an invalid card and vice-versa.

# Getting Started:

Training and Weights file : <a href="https://drive.google.com/drive/folders/1AgvQbPaQzvm0TTzzf8aSUhYr6TEaTsG3?usp=sharing">LINK</a>

