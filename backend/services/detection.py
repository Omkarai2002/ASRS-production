from ultralytics import YOLO

CONF_THERSHOLD = 0.5
AREA_THERSHOLD = 5000000

_model = None

def get_model():
    global _model
    if _model is None:
        _model = YOLO('trained_models/esrsyolo11 1.pt')
    return _model

def detect_vehicle(image_path, records):
    model = get_model()
    preds = model.predict(image_path)[0]

    for box in preds.boxes:
        conf = box.conf.item()
        if conf < CONF_THERSHOLD:
            continue

        cls = int(box.cls.item())
        label = model.names[cls]
        if label != "Chassis":
            continue

        x1, y1, x2, y2 = map(int, box.xyxy[0])

        area = (x2 - x1) * (y2 - y1)
        print("area: ",area)
        print("area_threshold: ",AREA_THERSHOLD)
        if area < AREA_THERSHOLD:
            continue

        return True
    return False
