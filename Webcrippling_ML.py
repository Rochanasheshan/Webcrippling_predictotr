import tkinter as tk
import numpy as np
import joblib
from PIL import Image, ImageTk
import subprocess
import sys


def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
try:
    import numpy as np
except ImportError:
    install('numpy')

try:
    import joblib
except ImportError:
    install('joblib')

try:
    from PIL import Image, ImageTk
except ImportError:
    install('Pillow')

class StrengthPredictionApp:
    def __init__(self, window):
        self.window = window
        self.window.geometry("800x600")
        self.window.title("IOF and EOF Prediction App")
        self.model_IOF = joblib.load('IOF_RF.sav')
        self.model_EOF = joblib.load('EOF_RF.sav')       
        self.setup_input_fields()
        self.setup_predict_button()
        self.setup_result_label()
        self.setup_image()  
        self.setup_range_labels() 
    def setup_input_fields(self):
        self.numeric_entries = {}
        numeric_labels = {
            'Web (D)': 'Web',
            'Flange (Bf)': 'Flange',
            'Thickness (t)': 'Thickness',
            'Corner radius (Ri)': 'Corner_radius',
            'Slot length (Lsl)': 'Slot_length',
            'Slot rows (n)': 'Slot_rows',
            'Bearing plate (lb)': 'Bearing_plate',
            'Yield strength (Fy)': 'Yield_strength'
        }
        for original_label, display_label in numeric_labels.items():
            tk.Label(self.window, text=original_label, font=("Arial", 10)).grid(row=len(self.numeric_entries), column=0, sticky='w')
            entry = tk.Entry(self.window, width=10, font=("Arial", 10))  
            entry.grid(row=len(self.numeric_entries), column=1)
            self.numeric_entries[display_label] = entry
    def setup_predict_button(self):
        predict_button = tk.Button(self.window, text="Predict IOF and EOF", command=self.predict_strengths, font=("Arial", 12))
        predict_button.grid(row=len(self.numeric_entries), columnspan=2)
    def setup_result_label(self):
        self.result_label = tk.Label(self.window, text="", font=("Arial", 10))
        self.result_label.grid(row=len(self.numeric_entries) + 1, columnspan=2)
    def setup_image(self):
        img_path = "image.png" 
        try:
            img = Image.open(img_path)
            original_width, original_height = img.size

            max_width = 800 
            max_height = 600 
            aspect_ratio = original_width / original_height
            if original_width > max_width or original_height > max_height:
                if aspect_ratio > 1:  
                    new_width = max_width
                    new_height = int(max_width / aspect_ratio)
                else:  
                    new_height = max_height
                    new_width = int(max_height * aspect_ratio)
            else:
                new_width = original_width
                new_height = original_height

            img = img.resize((new_width, new_height), Image.ANTIALIAS)  
            self.img_tk = ImageTk.PhotoImage(img)
            img_label = tk.Label(self.window, image=self.img_tk)
            img_label.grid(row=len(self.numeric_entries) + 2, columnspan=2)
        except FileNotFoundError:
            print(f"Error: Image file not found at {img_path}")
            tk.Label(self.window, text="Image file not found.", font=("Arial", 12)).grid(row=len(self.numeric_entries) + 2, columnspan=2)
        except Exception as e:
            print(f"An error occurred: {e}")

    def setup_range_labels(self):

        valid_ranges = {
            'Web': (150, 250),          # Web (D) - Min: 150, Max: 250
            'Flange': (45, 65),         # Flange (Bf) - Min: 45, Max: 65
            'Thickness': (1, 2),        # Thickness (t) - Min: 1, Max: 2
            'Corner_radius': (3, 5),    # Corner radius (Ri) - Min: 3, Max: 5
            'Slot_length': (60, 75),    # Slot length (Lsl) - Min: 60, Max: 75
            'Slot_rows': (6, 12),       # Slot rows (n) - Min: 6, Max: 12
            'Bearing_plate': (50, 150), # Bearing plate (lb) - Min: 50, Max: 150
            'Yield_strength': (300, 500) # Yield strength (Fy) - Min: 300, Max: 500
        }
        range_text = "\n".join([f"{label}: Min: {range_[0]}, Max: {range_[1]}"
                                for label, range_ in valid_ranges.items()])
        range_label = tk.Label(self.window, text=range_text, justify='left', font=("Arial", 9))
        range_label.grid(row=len(self.numeric_entries) + 3, columnspan=2, sticky='w')

        note_label = tk.Label(self.window, text="*Dimensions are in mm", font=("Arial", 9), justify='left')
        note_label.grid(row=len(self.numeric_entries) + 4, columnspan=2, sticky='w')

    def predict_strengths(self):
        valid_ranges = {
            'Web': (150, 250),          
            'Flange': (45, 65),         
            'Thickness': (1, 2),        
            'Corner_radius': (3, 5),    
            'Slot_length': (60, 75),    
            'Slot_rows': (6, 12),       
            'Bearing_plate': (50, 150), 
            'Yield_strength': (300, 500) 
        }
        input_data = []
        try:
            for label, entry in self.numeric_entries.items():
                value = float(entry.get())
                if not (valid_ranges[label][0] <= value <= valid_ranges[label][1]):
                    self.result_label.config(text=f"{label.replace('_', ' ')} must be between {valid_ranges[label][0]} and {valid_ranges[label][1]}.")
                    return                
                input_data.append(value)
        except ValueError:
            self.result_label.config(text="Check numeric input values.")
            return
        input_data = np.array(input_data).reshape(1, -1)
        try:
            prediction_IOF = self.model_IOF.predict(input_data)[0]
            prediction_EOF = self.model_EOF.predict(input_data)[0]
            self.result_label.config(
                text=f"Predicted IOF: {prediction_IOF:.1f} kN\nPredicted EOF: {prediction_EOF:.1f} kN",
            )
        except ValueError as e:
            self.result_label.config(text=f"Error in prediction: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = StrengthPredictionApp(root)
    root.mainloop()
