from ultralytics import YOLO

def main():
    # 加载模型
    model = YOLO("runs/detect/BRV11/weights/best.pt")

    results= model.predict(source='data2/images/train',save=True)

main()