import cv2
from deepface import DeepFace   
import serial
import numpy as np


# Убедись, что COM-порт и скорость (115200) совпадают с кодом в Arduino
ser_cam = serial.Serial('COM8', 2000000, timeout=0.1) 
ser_act = serial.Serial('COM5', 115200, timeout=0.1)

print("Связь установлена. Ищу кадры...")

raw_data = bytearray()

while True:
    if ser_cam.in_waiting > 20000: 
        ser_cam.reset_input_buffer()
    # Читаем всё, что есть в порту на данный момент
    if ser_cam.in_waiting > 0:
        raw_data += ser_cam.read(ser_cam.in_waiting)
        
        # Ищем маркер начала кадра
        start_idx = raw_data.find(b"START")
        
        if start_idx != -1:
            # Проверяем, есть ли после START хотя бы 4 байта размера
            if len(raw_data) >= start_idx + 5 + 4:
                # Вырезаем размер кадра (он идет сразу после START)
                size_offset = start_idx + 5
                size_bytes = raw_data[size_offset:size_offset + 4]
                size = int.from_bytes(size_bytes, byteorder='little')
                
                # Проверяем, догрузился ли весь кадр в буфер
                if len(raw_data) >= size_offset + 4 + size:
                    # Извлекаем JPEG данные
                    img_start = size_offset + 4
                    img_data = raw_data[img_start:img_start + size]
                    
                    # Переводим в картинку
                    nparr = np.frombuffer(img_data, np.uint8)
                    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    
                   # if frame is not None:
                    #    cv2.imshow("ESP32-S3 Camera Stream", frame)
                    
                    
                    # КОД ДЛЯ ПЕРЕДАЧИ ДАННЫХ НА ЭКРАН ESP32-C3!!!!!!!!!!!!!!
                    if frame is not None:
                        
                        # 1. ТВОЙ ИИ / ОБРАБОТКА
                        # Для примера: простое условие (например, если средняя яркость > 100)
                       # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                       # brightness = np.mean(gray)
                        
                      #  result = brightness > 120 # Твоя логика ИСТИНА/ЛОЖЬ
                        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
                        
                        result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
            
                        # ИИ СИСТЕМА
                        font = cv2.FONT_HERSHEY_SIMPLEX
                        
                        if isinstance(result, list):
                            dominant_emotion = result[0].get("dominant_emotion", "unknow")                            
                        
                        result = dominant_emotion == "neutral" or dominant_emotion == "happy" or dominant_emotion == "sad"
                        
                        cv2.putText(frame, str(result), (10,80), font, 2, (0,0,255), 2, cv2.LINE_4)
                        cv2.imshow('Face Detection', frame)
                        
                        # All stas: sad, fear, angry, happy, suprised
                        
                        # 2. ОТПРАВКА НА ESP32-C3
                        if result:
                            ser_act.write(b'1') # Команда для C3
                            cv2.putText(frame, "TRUE", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        else:
                            ser_act.write(b'0')
                            cv2.putText(frame, "FALSE", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    
                    ###########################################################
                    
                    # Очищаем буфер от обработанного кадра
                    raw_data = raw_data[img_start + size:]
    
    # Выход по нажатию 'q'
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or key == 27: # 27 — это клавиша Esc
        break

ser_cam.close()
cv2.destroyAllWindows()