from constants import Constants
import cv2
import numpy as np

class yoloDetectionModel():
    def __init__(self,img_path):
        self.img = cv2.imread(img_path)

    def crop_coor_func(self):

        img =self.img
        net = cv2.dnn.readNet(Constants.yolo_weights_file,Constants.yolo_config_file)

        classes = ["socks_card"]

        layer_names = net.getLayerNames()
        output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
        colors = np.random.uniform(0, 255, size=(len(classes), 3))


        # img = cv2.imread("C:\\Users\\HARIVIGNESH A\\Downloads\\validation\\images\\yolo.jpeg")

        # img = cv2.resize(img, None, fx=0.7, fy=0.7)
        height, width, channels = img.shape
        blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        net.setInput(blob)
        outs = net.forward(output_layers)

        class_ids = []
        confidences = []
        boxes = []
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.3:
                    # Object detected
                    print(class_id)
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)

                    # Rectangle coordinates
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)

                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
        font = cv2.FONT_HERSHEY_TRIPLEX
        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]
                label = str(classes[class_ids[i]])
                color = colors[class_ids[i]]
                cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
                cv2.putText(img, label, (x, y+20), font, 0.7, color, 1)
                print(x,y,x+w,y+h)
        
        print(x,y,x+w,y+h)
        return [x,y,x+w,y+h]


# cv2.imshow('img',img)
# cv2.waitKey(0)

