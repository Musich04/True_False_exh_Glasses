#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128 
#define SCREEN_HEIGHT 64 
#define SDA_PIN 5
#define SCL_PIN 6

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

void setup() {
  // Начинаем слушать USB порт (скорость 115200)
  Serial.begin(115200);

  // Инициализация дисплея
  Wire.begin(SDA_PIN, SCL_PIN);
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    for(;;); 
  }

  // Приветственный экран
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(30, 40);
  display.println("WAITING...");
  display.display();

  display.ssd1306_command(0xA0);
}

void loop() {
  // Если пришли данные от Python
  if (Serial.available() > 0) {
    char data = Serial.read(); // Читаем символ ('1' или '0')

    display.clearDisplay();

    display.setTextSize(2); // Увеличим шрифт для результата
    
    if (data == '1') {
      display.setCursor(30, 40);
      display.println("TRUE");
    } 
    else if (data == '0') {
      display.setCursor(30, 40);
      display.println("FALSE");
    }

    display.setTextSize(1); // Возвращаем размер шрифта
    display.display();
  }
}